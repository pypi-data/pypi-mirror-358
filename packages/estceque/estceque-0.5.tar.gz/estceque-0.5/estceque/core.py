#!/usr/bin/env python
# *****************************************************************************
# Copyright (C) 2024 Thomas Touhey <thomas@touhey.fr>
#
# This software is governed by the CeCILL-C license under French law and
# abiding by the rules of distribution of free software. You can use, modify
# and/or redistribute the software under the terms of the CeCILL-C license
# as circulated by CEA, CNRS and INRIA at the following
# URL: https://cecill.info
#
# As a counterpart to the access to the source code and rights to copy, modify
# and redistribute granted by the license, users are provided only with a
# limited warranty and the software's author, the holder of the economic
# rights, and the successive licensors have only limited liability.
#
# In this respect, the user's attention is drawn to the risks associated with
# loading, using, modifying and/or developing or reproducing the software by
# the user in light of its specific status of free software, that may mean
# that it is complicated to manipulate, and that also therefore means that it
# is reserved for developers and experienced professionals having in-depth
# computer knowledge. Users are therefore encouraged to load and test the
# software's suitability as regards their requirements in conditions enabling
# the security of their systems and/or data to be ensured and, more generally,
# to use and operate it in the same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL-C license and that you accept its terms.
# *****************************************************************************
"""Core objects definition."""

from __future__ import annotations

from abc import ABC
from collections.abc import Iterable, Sequence
from ipaddress import IPv4Address, IPv6Address
import re
from typing import Annotated, Any, TypeVar, Union

from annotated_types import Len
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    GetCoreSchemaHandler,
    StringConstraints,
    TypeAdapter,
    create_model,
)
from pydantic_core.core_schema import (
    CoreSchema,
    is_instance_schema,
    json_or_python_schema,
    str_schema,
    no_info_after_validator_function,
    plain_serializer_function_ser_schema,
)
from typing_extensions import TypeAliasType


_ProcessorType = TypeVar("_ProcessorType", bound="Processor")

FieldPathType = TypeVar("FieldPathType", bound="FieldPath")
EmptyFieldPathType = TypeVar("EmptyFieldPathType", bound="EmptyFieldPath")

FieldPathPart = Annotated[str, StringConstraints(pattern=r"^[^\.]+$")]
FieldPathParts = Annotated[tuple[FieldPathPart, ...], Len(min_length=1)]

Element = TypeAliasType(  # type: ignore
    "Element",
    Union[
        dict[str, "Element"],  # type: ignore
        list["Element"],  # type: ignore
        IPv4Address,
        IPv6Address,
        str,
        int,
        float,
        bool,
        None,
    ],
)
"""Document element.

This is a recursive type defining a document element that can represent a JSON
value with extra types supported by Elasticsearch, including:

* Dictionaries associating string keys with document elements;
* Lists of document elements;
* Strings;
* Numbers (integers, floating-point, booleans);
* None.
"""

# Type adapters.
field_path_parts_type_adapter = TypeAdapter(FieldPathParts)

_FIELD_PATH_PART_PATTERN = re.compile(r"([^\.]+)(\.)?")
"""Pattern for a given path part.

See :py:func:`_get_parts_from_string` for usage of this pattern.
"""


def _get_parts_from_string(raw: str, /) -> Sequence[str]:
    """Get field path parts from a string.

    :param raw: Raw string from which to get field path parts.
    :return: Field path parts.
    """
    left = raw
    parts: list[str] = []

    while left:
        match = _FIELD_PATH_PART_PATTERN.match(left)
        if match is None:
            raise ValueError(f"Invalid field path: {raw}")

        left = left[match.end() :]
        if bool(left) != (match[2] == "."):
            # Either there is no string left and the path ends with a dot
            # separator, or there is string left but the path does not
            # end with a dot separator; in either case, the field
            # is not valid.
            raise ValueError(f"Invalid field path: {raw}")

        parts.append(match[1])

    return parts


class FieldPath:
    """Object representing the path to a field in a JSON document.

    This object can be used in a similar fashion to :py:class:`pathlib.Path`.
    For example, in order to create a field path out of several components,
    the following can be used:

    .. doctest::

        >>> FieldPath("hello.world")
        FieldPath('hello.world')
        >>> FieldPath("hello") / "world"
        FieldPath('hello.world')
        >>> FieldPath(["hello", "world"])
        FieldPath('hello.world')

    Field paths can also be used in Pydantic models:

    .. doctest::

        >>> from pydantic import BaseModel
        >>> class MyModel(BaseModel):
        ...     field: FieldPath
        ...
        >>> MyModel(field="hello.world")
        MyModel(field=FieldPath('hello.world'))
    """

    __slots__ = ("_parts",)

    _parts: FieldPathParts
    """Parts of the path."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls: type[FieldPathType],
        source: type[Any],
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """Get the pydantic core schema.

        This allows the field path to be handled within pydantic classes,
        and imported/exported in JSON schemas as strings.

        :param source: Source type.
        """
        return no_info_after_validator_function(
            cls._validate,
            json_or_python_schema(
                json_schema=str_schema(),
                python_schema=is_instance_schema((FieldPath, str)),
                serialization=plain_serializer_function_ser_schema(
                    cls._serialize,
                    info_arg=False,
                    return_schema=str_schema(),
                ),
            ),
        )

    @classmethod
    def _validate(
        cls: type[FieldPathType],
        value: str | FieldPathType,
        /,
    ) -> FieldPathType:
        """Validate a pydantic value.

        :param value: Value to validate.
        :return: Obtained field path.
        """
        if isinstance(value, str):
            return cls(_get_parts_from_string(value))
        if isinstance(value, cls):
            return cls(value.parts)
        raise TypeError()  # pragma: no cover

    @classmethod
    def _serialize(
        cls: type[FieldPath],
        value: Any,
    ) -> str:
        """Serialize a pydantic value.

        :param value: Value to serialize.
        """
        if not isinstance(value, cls):
            raise TypeError()

        return str(value)

    @property
    def parent(self: FieldPathType, /) -> FieldPathType | EmptyFieldPath:
        """Get the field path parent.

        :return: Parent.
        """
        if len(self.parts) == 1:
            return EmptyFieldPath()

        return self.__class__(self.parts[:-1])

    @property
    def parts(self, /) -> tuple[FieldPathPart, ...]:
        """Get the parts of the current path.

        :return: Parts.
        """
        return self._parts

    def __init__(self, path: FieldPath | str | Iterable[str], /) -> None:
        if isinstance(path, FieldPath):
            raw_parts: Iterable[str] = path.parts
        elif isinstance(path, str):
            raw_parts = tuple(_get_parts_from_string(path))
        else:
            raw_parts = path

        self._parts = field_path_parts_type_adapter.validate_python(raw_parts)

    def __eq__(self, other: Any, /) -> bool:
        try:
            other = FieldPath(other)
        except (ValueError, TypeError):
            return False

        return self.parts == other.parts

    def __contains__(self, other: Any, /) -> bool:
        try:
            other = FieldPath(other)
        except (ValueError, TypeError):
            return False

        # NOTE: We consider that a path contains itself, i.e. if a == b,
        # then a in b.
        return other._parts[: len(self._parts)] == self._parts

    def __str__(self, /) -> str:
        return ".".join(self.parts)

    def __repr__(self, /) -> str:
        return f"{self.__class__.__name__}({'.'.join(self.parts)!r})"

    def __truediv__(self: FieldPathType, other: Any, /) -> FieldPathType:
        if isinstance(other, FieldPath):
            return self.__class__([*self.parts, *other.parts])
        if isinstance(other, str):
            return self.__class__(
                [*self.parts, *_get_parts_from_string(other)],
            )

        raise TypeError()  # pragma: no cover

    def __hash__(self, /):
        return hash(".".join(self.parts))


class EmptyFieldPath:
    """Object representing an empty field path."""

    __slots__ = ()

    @classmethod
    def __get_pydantic_core_schema__(
        cls: type[EmptyFieldPathType],
        source: type[Any],
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """Get the pydantic core schema.

        This allows the field path to be handled within pydantic classes,
        and imported/exported in JSON schemas as strings.

        :param source: Source type.
        """
        return no_info_after_validator_function(
            cls._validate,
            json_or_python_schema(
                json_schema=str_schema(),
                python_schema=is_instance_schema((EmptyFieldPath, str)),
                serialization=plain_serializer_function_ser_schema(
                    cls._serialize,
                    info_arg=False,
                    return_schema=str_schema(),
                ),
            ),
        )

    @classmethod
    def _validate(
        cls: type[EmptyFieldPathType],
        value: str | EmptyFieldPathType,
        /,
    ) -> EmptyFieldPathType:
        """Validate a pydantic value.

        :param value: Value to validate.
        :return: Obtained field path.
        """
        if isinstance(value, str):
            if value != "":
                raise ValueError(f"Non-empty field path: {value!r}")

            return cls()
        if isinstance(value, cls):
            return cls()
        raise TypeError()  # pragma: no cover

    @classmethod
    def _serialize(
        cls: type[EmptyFieldPath],
        value: Any,
    ) -> str:
        """Serialize a pydantic value.

        :param value: Value to serialize.
        """
        if not isinstance(value, cls):
            raise TypeError()

        return str(value)

    @property
    def parent(self: EmptyFieldPathType, /) -> EmptyFieldPathType:
        """Get the field path parent.

        :return: Parent.
        """
        return self

    @property
    def parts(self, /) -> tuple[FieldPathPart, ...]:
        """Get the parts of the current path.

        :return: Parts.
        """
        return ()

    def __init__(self, /) -> None:
        pass

    def __eq__(self, other: Any, /) -> bool:
        return isinstance(other, EmptyFieldPath)

    def __contains__(self, other: Any, /) -> bool:
        if other == "" or isinstance(other, EmptyFieldPath):
            return True

        try:
            FieldPath(other)
        except (ValueError, TypeError):
            return False
        else:
            return True

    def __str__(self, /) -> str:
        return ""

    def __repr__(self, /) -> str:
        return f"{self.__class__.__name__}()"

    def __truediv__(self: EmptyFieldPathType, other: Any, /) -> FieldPath:
        if isinstance(other, FieldPath):
            return other
        if isinstance(other, str):
            return FieldPath(other)

        raise TypeError()  # pragma: no cover

    def __hash__(self, /):
        return hash("")


class _ProcessorWrapper(BaseModel):
    """Elasticsearch processor wrapper.

    This class is used for wrappers built dynamically by the pipeline parser.
    """

    value: Processor
    """Actual processor being run."""


class PainlessCondition(BaseModel, ABC):
    """Condition written in Painless.

    See `Painless scripting language`_ for more information.

    .. _Painless scripting language:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        modules-scripting-painless.html
    """

    model_config = ConfigDict(extra="forbid")
    """Model configuration."""

    script: Annotated[str, StringConstraints(min_length=1)]
    """Painless script to run."""


class Processor(ABC, BaseModel):
    """Elasticsearch ingest pipeline processor.

    This class is used for parsing and rendering Elasticsearch ingest
    pipelines, in order to ensure that we check all options, forbid
    additional options, and so on.
    """

    model_config = ConfigDict(extra="forbid")
    """Model configuration."""

    description: str | None = None
    if_: Annotated[str | None, Field(alias="if")] = None
    ignore_failure: bool = False
    on_failure: list[_ProcessorWrapper] | None = None
    tag: str | None = None


# HACK: Fix the circular dependency.
_ProcessorWrapper.model_rebuild()


class _IngestPipeline(BaseModel):
    """Pipeline model."""

    name: str
    """Name of the pipeline."""

    processors: list[_ProcessorWrapper] = []
    """Processor list."""

    on_failure: list[_ProcessorWrapper] = []
    """Failure processor list."""


class IngestPipelineParser:
    """Elasticsearch ingest pipeline converter.

    :param name: Optional name with which the parser wants to be represented.
    :param processors: Processors supported by the pipeline.
    """

    __slots__ = (
        "_name",
        "_processors",
        "_processors_type_adapter",
        "_type_adapter",
    )

    _name: str | None
    """Name by which the processor wants to be represented."""

    _processors: dict[str, type[Processor]]
    """Processors taken into account when parsing."""

    _type_adapter: TypeAdapter[_IngestPipeline | list[Processor]]
    """Type adapter with which to parse.."""

    _processors_type_adapter: TypeAdapter[list[Processor]]
    """Type adapter with which to serialize processors."""

    def __init__(
        self,
        /,
        *,
        processors: dict[str, type[Processor]],
        name: str | None = None,
    ) -> None:
        if len(processors) == 0:
            raise ValueError("At least one processor must be passed.")

        # This bit is quite the complicated type stuff, to delegate as much
        # as we can to pydantic's parsing facilities.
        # The steps here are the following:
        #
        # 1. We define "processor_models" as the dictionary of names to
        #    overridden models to replace ``list[Processor]`` (base class)
        #    with an indirect reference to ``processor_list`` we're going
        #    to define later.
        # 2. We define "processor_wrappers" as the sequence of
        #    models wrapping processors into a dictionary where the processor
        #    definition is indexed by the processor name, in order to match
        #    e.g. ``{"my_processor": {...}}``. The processor data will always
        #    be accessible by the key ``value``; see usage of this in
        #    :py:meth:`convert`.
        # 3. We define our "processor_list" type as the list of our
        #    processor wrappers.
        # 4. We rebuild the models defined at step 1 to include a concrete
        #    definition of the wrapper list.

        processor_models = {
            name: create_model(
                typ.__name__,
                on_failure=(
                    Union["processor_list", None],
                    Field(default=None),
                ),
                __base__=typ,
            )
            for name, typ in processors.items()
        }

        processor_wrappers = tuple(
            create_model(
                f"{typ.__name__}Wrapper",
                value=(typ, Field(alias=name)),
                __base__=_ProcessorWrapper,
            )
            for name, typ in processor_models.items()
        )

        processor_list = TypeAliasType(
            "processor_list",
            list[Union[processor_wrappers]],  # type: ignore
        )

        for typ in processor_models.values():
            typ.model_rebuild()

        # We can now define our pipeline type, and actually define the
        # type adapter.
        class IngestPipeline(_IngestPipeline):
            """Elasticsearch pipeline, as an object to be parsed."""

            processors: processor_list = []
            """Processor list."""

            on_failure: processor_list = []
            """Failure processor list."""

        self._name = name
        self._processors = processors.copy()
        self._processors_type_adapter = TypeAdapter(processor_list)
        self._type_adapter = TypeAdapter(
            Union[IngestPipeline, processor_list],
        )

    def __repr__(self, /) -> str:
        return self._name or f"{self.__class__.__name__}()"

    def copy(
        self,
        /,
        *,
        with_processors: dict[str, type[Processor]] | None = None,
        without_processors: Iterable[str] | None = None,
    ) -> IngestPipelineParser:
        """Copy the parser.

        :param with_processors: Processors to add in the new parser.
            If the key exists in the current parser, the processor will be
            replaced automatically in the new parser.
        :param without_processors: Processors to remove from the
            current parser.
        :return: New parser with the modified processors.
        """
        processors = self._processors.copy()

        if without_processors is not None:
            for key in without_processors:
                processors.pop(key, None)

        if with_processors is not None:
            for key, value in with_processors.items():
                processors[key] = value

        return self.__class__(processors=processors)

    def validate_processors(self, raw: Any, /) -> list[dict]:
        """Validate the provided pipeline's processors.

        :param raw: Pipeline or processor list dictionary, or
            JSON-encoded version of the same.
        :return: Validated object, as Python.
        """
        if isinstance(raw, str):
            obj = self._type_adapter.validate_json(raw)
        else:
            obj = self._type_adapter.validate_python(raw)

        if isinstance(obj, list):
            processors = obj
        else:
            processors = obj.processors

        return self._processors_type_adapter.dump_python(
            processors,
            mode="json",
            by_alias=True,
            exclude_defaults=True,
        )

    def validate_failure_processors(self, raw: Any, /) -> list[dict]:
        """Validate the provided pipeline's failure processors.

        :param raw: Pipeline or processor list dictionary, or
            JSON-encoded version of the same.
        :return: Validated object, as Python.
        """
        if isinstance(raw, str):
            obj = self._type_adapter.validate_json(raw)
        else:
            obj = self._type_adapter.validate_python(raw)

        if isinstance(obj, list):
            processors = obj
        else:
            processors = obj.on_failure

        return self._processors_type_adapter.dump_python(
            processors,
            mode="json",
            by_alias=True,
            exclude_defaults=True,
        )

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
"""Builtin processors and pipeline parser."""

from __future__ import annotations

import re
from typing import Annotated, Any, Literal

from annotated_types import Ge, Lt
from dissec.patterns import Pattern as DissectPattern
from pydantic import StringConstraints, model_validator

from .core import (
    Element,
    EmptyFieldPath,
    FieldPath,
    Processor,
    IngestPipelineParser,
)


class AppendProcessor(Processor):
    """Elasticsearch append processor.

    See `Append processor`_ for more information.

    .. _Append processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        append-processor.html
    """

    field: FieldPath
    value: Element | list[Element]
    allow_duplicates: bool = True
    media_type: str = "application/json"


class BytesProcessor(Processor):
    """Elasticsearch bytes processor.

    See `Bytes processor`_ for more information.

    .. _Bytes processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        bytes-processor.html
    """

    field: FieldPath
    target_field: FieldPath | None = None
    ignore_missing: bool = False


class CommunityIDProcessor(Processor):
    """Elasticsearch Community ID processor.

    See `Community ID processor`_ for more information.

    .. _Community ID processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        community-id-processor.html
    """

    source_ip: FieldPath = FieldPath(("source", "ip"))
    source_port: FieldPath = FieldPath(("source", "port"))
    destination_ip: FieldPath = FieldPath(("destination", "ip"))
    destination_port: FieldPath = FieldPath(("destination", "port"))
    iana_number: FieldPath = FieldPath(("network", "iana_number"))
    icmp_type: FieldPath = FieldPath(("icmp", "type"))
    icmp_code: FieldPath = FieldPath(("icmp", "code"))
    transport: FieldPath = FieldPath(("network", "transport"))
    target_field: FieldPath = FieldPath(("network", "community_id"))
    seed: Annotated[int, Ge(0), Lt(65536)] = 0
    ignore_missing: bool = True


class ConvertProcessor(Processor):
    """Elasticsearch convert processor.

    See `Convert processor`_ for more information.

    .. _Convert processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        convert-processor.html
    """

    field: FieldPath
    target_field: FieldPath | None = None
    type: Literal[
        "integer",
        "long",
        "float",
        "double",
        "string",
        "boolean",
        "ip",
        "auto",
    ]
    ignore_missing: bool = False


class CSVProcessor(Processor):
    """Elasticsearch CSV processor.

    See `CSV processor`_ for more information.

    .. _CSV processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        csv-processor.html
    """

    field: FieldPath
    target_fields: list[FieldPath]
    separator: Annotated[
        str,
        StringConstraints(min_length=1, max_length=1),
    ] = ","
    quote: Annotated[str, StringConstraints(min_length=1, max_length=1)] = '"'
    ignore_missing: bool = False
    trim: bool = False
    empty_value: str = ""


class DateProcessor(Processor):
    """Elasticsearch date processor.

    See `Date processor`_ for more information.

    .. _Date processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        date-processor.html
    """

    field: FieldPath
    target_field: FieldPath = FieldPath("@timestamp")
    formats: list[str]
    timezone: str = "UTC"
    locale: str = "ENGLISH"
    output_format: str = "yyyy-MM-dd'T'HH:mm:ss.SSSXXX"


class DateIndexNameProcessor(Processor):
    """Elasticsearch date index name processor.

    See `Date index name processor`_ for more information.

    .. _Date index name processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        date-index-name-processor.html
    """

    field: FieldPath
    index_name_prefix: str | None = None
    date_rounding: Literal["y", "M", "w", "d", "h", "m", "s"]
    date_formats: str | list[str] = "yyyy-MM-dd'T'HH:mm:ss.SSSXX"
    timezone: str = "UTC"
    locale: str = "ENGLISH"
    index_name_format: str = "yyyy-MM-dd"


class DissectProcessor(Processor):
    """Elasticsearch dissect processor.

    See `Dissect processor`_ for more information.

    .. _Dissect processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        dissect-processor.html
    """

    field: FieldPath
    pattern: DissectPattern
    append_separator: str = ""
    ignore_missing: bool = False


class DotExpander(Processor):
    """Elasticsearch dot expander processor.

    See `Dot expander processor`_ for more information.

    .. _Dot expander processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        dot-expand-processor.html
    """

    field: FieldPath
    path: str | None = None
    override: bool = False


class DropProcessor(Processor):
    """Elasticsearch drop processor.

    See `Drop processor`_ for more information.

    .. _Drop processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        drop-processor.html
    """


class FailProcessor(Processor):
    """Elasticsearch fail processor.

    See `Fail processor`_ for more information.

    .. _Fail processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        fail-processor.html
    """

    message: str


class FingerprintProcessor(Processor):
    """Elasticsearch fingerprint processor.

    See `Fingerprint processor`_ for more information.

    .. _Fingerprint processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        fingerprint-processor.html
    """

    fields: list[FieldPath]
    target_field: FieldPath = FieldPath("fingerprint")
    salt: str | None = None
    method: Literal[
        "MD5",
        "SHA-1",
        "SHA-256",
        "SHA-512",
        "MurmurHash3",
    ] = "SHA-1"
    ignore_missing: bool = False


class GeoIPProcessor(Processor):
    """Elasticsearch GeoIP processor.

    See `GeoIP processor`_ for more information.

    .. _GeoIP processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        geoip-processor.html
    """

    field: FieldPath
    target_field: FieldPath = FieldPath("@timestamp")
    database_file: str = "GeoLite2-City.mmdb"
    properties: list[str] = [
        "continent_name",
        "country_iso_code",
        "country_name",
        "region_iso_code",
        "region_name",
        "city_name",
        "location",
    ]
    ignore_missing: bool = False
    download_database_on_pipeline_creation: bool = True


class GrokProcessor(Processor):
    """Elasticsearch grok processor.

    See `Grok processor`_ for more information.

    .. _Grok processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        grok-processor.html
    """

    field: FieldPath
    patterns: list[str]
    pattern_definitions: dict[str, str] | None = None
    ecs_compatibility: Literal["disabled", "v1"] = "disabled"
    trace_match: bool = False
    ignore_missing: bool = False


class GsubProcessor(Processor):
    """Elasticsearch gsub processor.

    See `Gsub processor`_ for more information.

    .. _Gsub processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        gsub-processor.html
    """

    field: FieldPath
    pattern: str
    replacement: str
    target_field: FieldPath | None = None
    ignore_missing: bool = False


class HTMLStripProcessor(Processor):
    """Elasticsearch HTML strip processor.

    See `HTML strip processor`_ for more information.

    .. _HTML strip processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        htmlstrip-processor.html
    """

    field: FieldPath
    target_field: FieldPath | None = None
    ignore_missing: bool = False


class JoinProcessor(Processor):
    """Elasticsearch join processor.

    See `Join processor`_ for more information.

    .. _Join processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        join-processor.html
    """

    field: FieldPath
    separator: str
    target_field: FieldPath | None = None


class JSONProcessor(Processor):
    """Elasticsearch JSON processor.

    See `JSON processor`_ for more information.

    .. _JSON processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        json-processor.html
    """

    field: FieldPath
    target_field: FieldPath | None = None
    add_to_root: bool = False
    add_to_root_conflict_strategy: Literal["replace", "merge"] = "replace"
    allow_duplicate_keys: bool = False
    strict_json_parsing: bool = False


class KVProcessor(Processor):
    """Elasticsearch KV processor.

    See `KV processor`_ for more information.

    .. _KV processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        kv-processor.html
    """

    field: FieldPath
    field_split: re.Pattern
    value_split: re.Pattern
    target_field: FieldPath | None = None
    include_keys: list[str] | None = None
    exclude_keys: list[str] | None = None
    ignore_missing: bool = False
    prefix: str = ""
    trim_key: str = ""
    trim_value: str = ""
    strip_brackets: bool = False


class LowercaseProcessor(Processor):
    """Elasticsearch lowercase processor.

    See `Lowercase processor`_ for more information.

    .. _Lowercase processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        lowercase-processor.html
    """

    field: FieldPath
    target_field: FieldPath | None = None
    ignore_missing: bool = False


class NetworkDirectionProcessor(Processor):
    """Elasticsearch network direction processor.

    See `Network direction processor`_ for more information.

    .. _Network direction processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        network-direction-processor.html
    """

    source_ip: FieldPath = FieldPath(("source", "ip"))
    destination_ip: FieldPath = FieldPath(("destination", "ip"))
    target_field: FieldPath = FieldPath(("network", "direction"))
    internal_networks: list[str] | None = None
    internal_networks_field: FieldPath | None = None
    ignore_missing: bool = True

    @model_validator(mode="after")
    def _validate(self, /) -> NetworkDirectionProcessor:
        """Validate the model."""
        if (self.internal_networks is None) == (
            self.internal_networks_field is None
        ):
            raise ValueError(
                "Either internal_networks or internal_networks_field "
                + "must be defined.",
            )

        return self


class RedactProcessor(Processor):
    """Elasticsearch redact processor.

    See `Redact processor`_ for more information.

    .. _Redact processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        redact-processor.html
    """

    field: FieldPath
    patterns: list[str]
    pattern_definitions: dict[str, str] | None = None
    prefix: str = "<"
    suffix: str = ">"
    ignore_missing: bool = False


class RegisteredDomainProcessor(Processor):
    """Elasticsearch registered domain processor.

    See `Registered domain processor`_ for more information.

    .. _Registered domain processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        registered-domain-processor.html
    """

    field: FieldPath
    target_field: FieldPath | EmptyFieldPath = EmptyFieldPath()
    ignore_missing: bool = True


class RemoveProcessor(Processor):
    """Elasticsearch remove processor.

    See `Remove processor`_ for more information.

    .. _Remove processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        remove-processor.html
    """

    field: FieldPath | list[FieldPath] | None = None
    ignore_missing: bool = False
    keep: FieldPath | list[FieldPath] | None = None

    @model_validator(mode="after")
    def _validate(self, /) -> RemoveProcessor:
        """Validate the model."""
        if (self.field is None) == (self.keep is None):
            raise ValueError("Either field or keep must be defined.")

        return self


class RenameProcessor(Processor):
    """Elasticsearch rename processor.

    See `Rename processor`_ for more information.

    .. _Rename processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        rename-processor.html
    """

    field: FieldPath
    target_field: FieldPath
    ignore_missing: bool = False
    override: bool = False


class RerouteProcessor(Processor):
    """Elasticsearch reroute processor.

    See `Reroute processor`_ for more information.

    .. _Reroute processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        reroute-processor.html
    """

    destination: FieldPath | None = None
    dataset: str = "{{data_stream.dataset}}"
    namespace: str = "{{data_stream.namespace}}"


class ScriptProcessor(Processor):
    """Elasticsearch script processor.

    See `Script processor`_ for more information.

    .. _Script processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        script-processor.html
    """

    # TODO: Support more than painless.
    lang: Literal["painless", "expression", "mustache"] = "painless"
    id: str | None = None
    source: str | dict | None = None
    params: dict[str, Any] | None = None


class SetProcessor(Processor):
    """Elasticsearch set processor.

    See `Set processor`_ for more information.

    .. _Set processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        set-processor.html
    """

    field: FieldPath
    value: Element = None
    copy_from: str | None = None
    override: bool = True
    ignore_empty_value: bool = False
    media_type: str = "application/json"

    @model_validator(mode="after")
    def _validate(self, /) -> SetProcessor:
        """Validate the model."""
        if (self.value is None) == (self.copy_from is None):
            raise ValueError("Either value or copy_from must be defined.")

        return self


class SetSecurityUserProcessor(Processor):
    """Elasticsearch set security user processor.

    See `Set security user processor`_ for more information.

    .. _Set security user processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        ingest-node-set-security-user-processor.html
    """

    field: FieldPath
    properties: list[str] = [
        "username",
        "roles",
        "email",
        "full_name",
        "metadata",
        "api_key",
        "realm",
        "authentication_type",
    ]


class SortProcessor(Processor):
    """Elasticsearch sort processor.

    See `Sort processor`_ for more information.

    .. _Sort processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        sort-processor.html
    """

    field: FieldPath
    order: Literal["asc", "desc"]
    target_field: FieldPath | None = None


class SplitProcessor(Processor):
    """Elasticsearch split processor.

    See `Split processor`_ for more information.

    .. _Split processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        split-processor.html
    """

    field: FieldPath
    separator: re.Pattern
    target_field: FieldPath | None = None
    ignore_missing: bool = False
    preserve_trailing: bool = False


class TrimProcessor(Processor):
    """Elasticsearch trim processor.

    See `Trim processor`_ for more information.

    .. _Trim processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        trim-processor.html
    """

    field: FieldPath
    target_field: FieldPath | None = None
    ignore_missing: bool = False


class UppercaseProcessor(Processor):
    """Elasticsearch uppercase processor.

    See `Uppercase processor`_ for more information.

    .. _Uppercase processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        uppercase-processor.html
    """

    field: FieldPath
    target_field: FieldPath | None = None
    ignore_missing: bool = False


class URIPartsProcessor(Processor):
    """Elasticsearch URI parts processor.

    See `URI parts processor`_ for more information.

    .. _URI parts processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        uri-parts-processor.html
    """

    field: FieldPath
    target_field: FieldPath | None = None
    keep_original: bool = True
    remove_if_successful: bool = False
    ignore_missing: bool = False


class URLDecodeProcessor(Processor):
    """Elasticsearch URL decode processor.

    See `URL decode processor`_ for more information.

    .. _URL decode processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        urldecode-processor.html
    """

    field: FieldPath
    target_field: FieldPath | None = None
    ignore_missing: bool = False


class UserAgentProcessor(Processor):
    """Elasticsearch user agent processor.

    See `User agent processor`_ for more information.

    .. _User agent processor:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/
        user-agent-processor.html
    """

    field: FieldPath
    target_field: FieldPath = FieldPath(("user_agent",))
    regex_file: str | None = None
    properties: list[str] = [
        "name",
        "major",
        "minor",
        "patch",
        "build",
        "os",
        "os_name",
        "os_major",
        "os_minor",
        "device",
    ]
    ignore_missing: bool = False


class PipelineProcessor(Processor):
    """Elasticsearch pipeline processor.

    See `Pipeline processor`_ for more information.

    .. _Pipeline processor:
        https://www.elastic.co/docs/reference/enrich-processor/pipeline-processor
    """

    name: str
    ignore_missing_pipeline: bool = False


DEFAULT_INGEST_PIPELINE_PARSER = IngestPipelineParser(
    name="DEFAULT_INGEST_PIPELINE_PARSER",
    processors={
        "append": AppendProcessor,
        "bytes": BytesProcessor,
        "community_id": CommunityIDProcessor,
        "convert": ConvertProcessor,
        "csv": CSVProcessor,
        "date": DateProcessor,
        "date_index_name": DateIndexNameProcessor,
        "dissect": DissectProcessor,
        "dot_expander": DotExpander,
        "drop": DropProcessor,
        "fail": FailProcessor,
        "fingerprint": FingerprintProcessor,
        "geoip": GeoIPProcessor,
        "grok": GrokProcessor,
        "gsub": GsubProcessor,
        "html_strip": HTMLStripProcessor,
        "join": JoinProcessor,
        "json": JSONProcessor,
        "kv": KVProcessor,
        "lowercase": LowercaseProcessor,
        "network_direction": NetworkDirectionProcessor,
        "pipeline": PipelineProcessor,
        "redact": RedactProcessor,
        "registered_domain": RegisteredDomainProcessor,
        "remove": RemoveProcessor,
        "rename": RenameProcessor,
        "reroute": RerouteProcessor,
        "script": ScriptProcessor,
        "set": SetProcessor,
        "set_security_user": SetSecurityUserProcessor,
        "sort": SortProcessor,
        "split": SplitProcessor,
        "trim": TrimProcessor,
        "uppercase": UppercaseProcessor,
        "urldecode": URLDecodeProcessor,
        "uri_parts": URIPartsProcessor,
        "user_agent": UserAgentProcessor,
    },
)
"""Default Elasticsearch ingest pipeline parser instance.

This instance defines all of the default processors available in all contexts,
including on Elasticsearch and in Logstash's ``elastic_integration`` filter.
"""

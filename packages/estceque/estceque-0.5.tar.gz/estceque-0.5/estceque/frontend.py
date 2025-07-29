#!/usr/bin/env python
# *****************************************************************************
# Copyright (C) 2024-2025 Thomas Touhey <thomas@touhey.fr>
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
"""Front-end functions."""

from __future__ import annotations

from typing import Any

from .builtin import DEFAULT_INGEST_PIPELINE_PARSER
from .core import IngestPipelineParser


def validate_ingest_pipeline_processors(
    raw: Any,
    /,
    *,
    parser: IngestPipelineParser = DEFAULT_INGEST_PIPELINE_PARSER,
) -> list[dict]:
    """Validate an ingest pipeline's processors.

    :param raw: Raw ingest pipeline to validate the processors from, either
        provided as a dictionary or a raw JSON-encoded string.
    :param parser: Parser to use to validate the pipeline's processors.
    :return: Validated processors.
    """
    return parser.validate_processors(raw)


def validate_ingest_pipeline_failure_processors(
    raw: Any,
    /,
    *,
    parser: IngestPipelineParser = DEFAULT_INGEST_PIPELINE_PARSER,
) -> list[dict]:
    """Validate an ingest pipeline's failure processors.

    :param raw: Raw ingest pipeline to validate the failure processors from,
        either provided as a dictionary or a raw JSON-encoded string.
    :param parser: Parser to use to validate the pipeline's failure processors.
    :return: Validated failure processors.
    """
    return parser.validate_failure_processors(raw)

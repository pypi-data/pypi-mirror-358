#
# Documiner
#
# Copyright 2025 Documiner. All rights reserved. Developed by Sahib ur rehman.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Module for handling document processing pipelines.

This module provides the DocumentPipeline class, which represents a reusable collection
of pre-defined aspects and concepts that can be assigned to documents. Pipelines enable
standardized document analysis by packaging common extraction patterns into reusable units.

Pipelines serve as templates for document processing, allowing consistent application of
the same analysis approach across multiple documents. They encapsulate both the structural
organization (aspects) and the specific information to extract (concepts) in a single,
assignable object.
"""

from __future__ import annotations

from pydantic import Field

from documiner.internal.base.attrs import _AssignedInstancesProcessor
from documiner.internal.base.concepts import _Concept
from documiner.public.aspects import Aspect


class DocumentPipeline(_AssignedInstancesProcessor):
    """
    Represents a reusable collection of predefined aspects and concepts for document analysis.

    Document pipelines serve as templates that can be assigned to multiple documents,
    ensuring consistent application of the same analysis criteria. They package common
    extraction patterns into reusable units, allowing for standardized document processing.

    :ivar aspects: A list of aspects to extract from documents. Aspects represent structural
                  categories of information. Defaults to an empty list.
    :type aspects: list[Aspect]
    :ivar concepts: A list of concepts to identify within documents. Concepts represent
                   specific information elements to extract. Defaults to an empty list.
    :type concepts: list[_Concept]

    Note:
        A pipeline is a reusable configuration of extraction steps. You can use the same pipeline
        to extract data from multiple documents.

    Example:
        .. literalinclude:: ../../../dev/usage_examples/docstrings/pipelines/def_pipeline.py
            :language: python
            :caption: Document pipeline definition
    """

    aspects: list[Aspect] = Field(default_factory=list)
    concepts: list[_Concept] = Field(default_factory=list)

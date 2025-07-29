# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo
from .base_request_context_param import BaseRequestContextParam

__all__ = ["DocumentUpdateSectionOrderParams", "ProcessSection"]


class DocumentUpdateSectionOrderParams(TypedDict, total=False):
    context: BaseRequestContextParam

    process_sections: Annotated[Iterable[ProcessSection], PropertyInfo(alias="processSections")]


class ProcessSection(TypedDict, total=False):
    parent_id: Annotated[Optional[str], PropertyInfo(alias="parentId")]

    position: int

    section_id: Annotated[str, PropertyInfo(alias="sectionId")]

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["BaseRequestContextParam"]


class BaseRequestContextParam(TypedDict, total=False):
    process_public_id: Annotated[Optional[str], PropertyInfo(alias="processPublicId")]

    process_response_public_id: Annotated[Optional[str], PropertyInfo(alias="processResponsePublicId")]

    process_section_public_id: Annotated[Optional[str], PropertyInfo(alias="processSectionPublicId")]

    project_id: Annotated[str, PropertyInfo(alias="projectId")]

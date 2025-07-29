# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from ..base_request_context_param import BaseRequestContextParam

__all__ = ["DuplicateGlobalParams"]


class DuplicateGlobalParams(TypedDict, total=False):
    process_id: Required[Annotated[str, PropertyInfo(alias="processId")]]

    context: BaseRequestContextParam

    project_id: Annotated[Optional[str], PropertyInfo(alias="projectId")]

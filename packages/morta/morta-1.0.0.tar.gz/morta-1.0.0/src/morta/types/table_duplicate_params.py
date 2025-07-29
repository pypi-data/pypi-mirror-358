# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .base_request_context_param import BaseRequestContextParam

__all__ = ["TableDuplicateParams"]


class TableDuplicateParams(TypedDict, total=False):
    target_project_id: Required[Annotated[str, PropertyInfo(alias="targetProjectId")]]

    context: BaseRequestContextParam

    duplicate_linked_tables: Annotated[Optional[bool], PropertyInfo(alias="duplicateLinkedTables")]

    duplicate_permissions: Annotated[bool, PropertyInfo(alias="duplicatePermissions")]

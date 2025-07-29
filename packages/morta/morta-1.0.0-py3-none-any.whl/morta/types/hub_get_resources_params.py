# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["HubGetResourcesParams"]


class HubGetResourcesParams(TypedDict, total=False):
    admin_view: Annotated[Optional[bool], PropertyInfo(alias="adminView")]

    exclude_processes: Annotated[Optional[bool], PropertyInfo(alias="excludeProcesses")]

    exclude_tables: Annotated[Optional[bool], PropertyInfo(alias="excludeTables")]

    only_admin: Annotated[bool, PropertyInfo(alias="onlyAdmin")]

    only_deleted: Annotated[Optional[bool], PropertyInfo(alias="onlyDeleted")]

    project_permissions: Annotated[Optional[bool], PropertyInfo(alias="projectPermissions")]

    type_id: Annotated[Optional[str], PropertyInfo(alias="typeId")]

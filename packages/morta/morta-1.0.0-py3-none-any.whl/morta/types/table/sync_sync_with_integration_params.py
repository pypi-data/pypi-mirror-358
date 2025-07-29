# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from ..base_request_context_param import BaseRequestContextParam

__all__ = ["SyncSyncWithIntegrationParams"]


class SyncSyncWithIntegrationParams(TypedDict, total=False):
    table_id: Required[str]

    company_id: Annotated[str, PropertyInfo(alias="companyId")]

    context: BaseRequestContextParam

    doc_types: Annotated[List[str], PropertyInfo(alias="docTypes")]

    enterprise_id: Annotated[str, PropertyInfo(alias="enterpriseId")]

    folder_id: Annotated[str, PropertyInfo(alias="folderId")]

    hub_id: Annotated[str, PropertyInfo(alias="hubId")]

    license_id: Annotated[str, PropertyInfo(alias="licenseId")]

    model_id: Annotated[str, PropertyInfo(alias="modelId")]

    project_id: Annotated[str, PropertyInfo(alias="projectId")]

    project_ids: Annotated[List[str], PropertyInfo(alias="projectIds")]

    properties: List[str]

    region: str

    top_folder_id: Annotated[str, PropertyInfo(alias="topFolderId")]

    type: Literal[
        "Projects",
        "Resources",
        "Users",
        "Documents",
        "Workflows",
        "Comments",
        "RFIs",
        "Checklists",
        "Columns",
        "Issues",
        "AEC Data Model",
        "Forms",
    ]

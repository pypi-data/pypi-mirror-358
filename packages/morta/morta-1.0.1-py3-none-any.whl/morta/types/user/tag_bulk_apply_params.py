# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["TagBulkApplyParams"]


class TagBulkApplyParams(TypedDict, total=False):
    project_id: Required[Annotated[str, PropertyInfo(alias="projectId")]]

    table_id: Required[Annotated[str, PropertyInfo(alias="tableId")]]

    tag_reference_ids: Required[Annotated[List[str], PropertyInfo(alias="tagReferenceIds")]]

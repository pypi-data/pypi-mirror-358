# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .sort import Sort
from .chart import Chart
from .group import Group
from .colour import Colour
from .filter import Filter
from ..draftjs import Draftjs
from ..._models import BaseModel
from .views.table_view_column import TableViewColumn

__all__ = ["ViewRetrieveResponse", "Data", "DataDocumentTable"]


class DataDocumentTable(BaseModel):
    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    name: Optional[str] = None

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)

    type: Optional[str] = None

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)


class Data(BaseModel):
    name: str

    allow_contributor_delete: Optional[bool] = FieldInfo(alias="allowContributorDelete", default=None)

    chart_settings: Optional[Chart] = FieldInfo(alias="chartSettings", default=None)

    collapsed_group_view: Optional[bool] = FieldInfo(alias="collapsedGroupView", default=None)

    colour_settings: Optional[List[Colour]] = FieldInfo(alias="colourSettings", default=None)

    columns: Optional[List[TableViewColumn]] = None

    description: Optional[Draftjs] = None

    disable_new_row: Optional[bool] = FieldInfo(alias="disableNewRow", default=None)

    disable_sync_csv: Optional[bool] = FieldInfo(alias="disableSyncCsv", default=None)

    display_comment_rows: Optional[int] = FieldInfo(alias="displayCommentRows", default=None)

    display_validation_error_rows: Optional[int] = FieldInfo(alias="displayValidationErrorRows", default=None)

    document_table: Optional[DataDocumentTable] = FieldInfo(alias="documentTable", default=None)

    filter_settings: Optional[List[Filter]] = FieldInfo(alias="filterSettings", default=None)

    frozen_index: Optional[int] = FieldInfo(alias="frozenIndex", default=None)

    group_settings: Optional[List[Group]] = FieldInfo(alias="groupSettings", default=None)

    is_default: Optional[bool] = FieldInfo(alias="isDefault", default=None)

    locked_from_duplication: Optional[bool] = FieldInfo(alias="lockedFromDuplication", default=None)

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)

    row_height: Optional[int] = FieldInfo(alias="rowHeight", default=None)

    sort_settings: Optional[List[Sort]] = FieldInfo(alias="sortSettings", default=None)

    type: Optional[int] = None

    unpack_multiselect_group_view: Optional[bool] = FieldInfo(alias="unpackMultiselectGroupView", default=None)


class ViewRetrieveResponse(BaseModel):
    data: Optional[Data] = None

    metadata: Optional[Dict[str, object]] = None

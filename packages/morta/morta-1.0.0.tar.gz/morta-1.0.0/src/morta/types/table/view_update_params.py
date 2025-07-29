# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Annotated, TypeAlias, TypedDict

from ..._utils import PropertyInfo
from .sort_param import SortParam
from .chart_param import ChartParam
from .group_param import GroupParam
from .colour_param import ColourParam
from .filter_param import FilterParam
from ..draftjs_param import DraftjsParam
from ..base_request_context_param import BaseRequestContextParam
from .views.update_table_view_column_param import UpdateTableViewColumnParam

__all__ = ["ViewUpdateParams", "ChartSettings", "Description"]


class ViewUpdateParams(TypedDict, total=False):
    allow_contributor_delete: Annotated[bool, PropertyInfo(alias="allowContributorDelete")]

    chart_settings: Annotated[ChartSettings, PropertyInfo(alias="chartSettings")]

    collapsed_group_view: Annotated[bool, PropertyInfo(alias="collapsedGroupView")]

    colour_settings: Annotated[Iterable[ColourParam], PropertyInfo(alias="colourSettings")]

    columns: Iterable[UpdateTableViewColumnParam]

    context: BaseRequestContextParam

    description: Description

    disable_new_row: Annotated[bool, PropertyInfo(alias="disableNewRow")]

    disable_sync_csv: Annotated[bool, PropertyInfo(alias="disableSyncCsv")]

    display_comment_rows: Annotated[int, PropertyInfo(alias="displayCommentRows")]

    display_validation_error_rows: Annotated[Literal[0, 1, 2], PropertyInfo(alias="displayValidationErrorRows")]

    filter_settings: Annotated[Iterable[FilterParam], PropertyInfo(alias="filterSettings")]

    frozen_index: Annotated[int, PropertyInfo(alias="frozenIndex")]

    group_settings: Annotated[Iterable[GroupParam], PropertyInfo(alias="groupSettings")]

    name: str

    row_height: Annotated[int, PropertyInfo(alias="rowHeight")]

    sort_settings: Annotated[Iterable[SortParam], PropertyInfo(alias="sortSettings")]

    type: int

    unpack_multiselect_group_view: Annotated[bool, PropertyInfo(alias="unpackMultiselectGroupView")]


ChartSettings: TypeAlias = Union[ChartParam, Optional[object]]

Description: TypeAlias = Union[DraftjsParam, Optional[object]]

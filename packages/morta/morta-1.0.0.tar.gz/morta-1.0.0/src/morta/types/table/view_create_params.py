# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from ..._utils import PropertyInfo
from .sort_param import SortParam
from .chart_param import ChartParam
from .group_param import GroupParam
from .colour_param import ColourParam
from .filter_param import FilterParam
from ..draftjs_param import DraftjsParam
from ..base_request_context_param import BaseRequestContextParam

__all__ = ["ViewCreateParams", "ChartSettings", "Column", "ColumnDescription", "Description"]


class ViewCreateParams(TypedDict, total=False):
    name: Required[str]

    allow_contributor_delete: Annotated[bool, PropertyInfo(alias="allowContributorDelete")]

    chart_settings: Annotated[ChartSettings, PropertyInfo(alias="chartSettings")]

    collapsed_group_view: Annotated[bool, PropertyInfo(alias="collapsedGroupView")]

    colour_settings: Annotated[Iterable[ColourParam], PropertyInfo(alias="colourSettings")]

    columns: Iterable[Column]

    context: BaseRequestContextParam

    description: Description

    disable_new_row: Annotated[bool, PropertyInfo(alias="disableNewRow")]

    disable_sync_csv: Annotated[bool, PropertyInfo(alias="disableSyncCsv")]

    display_comment_rows: Annotated[int, PropertyInfo(alias="displayCommentRows")]

    display_validation_error_rows: Annotated[Literal[0, 1, 2], PropertyInfo(alias="displayValidationErrorRows")]

    filter_settings: Annotated[Iterable[FilterParam], PropertyInfo(alias="filterSettings")]

    frozen_index: Annotated[int, PropertyInfo(alias="frozenIndex")]

    group_settings: Annotated[Iterable[GroupParam], PropertyInfo(alias="groupSettings")]

    include_all_columns: Annotated[bool, PropertyInfo(alias="includeAllColumns")]

    is_default: Annotated[bool, PropertyInfo(alias="isDefault")]

    row_height: Annotated[int, PropertyInfo(alias="rowHeight")]

    sort_settings: Annotated[Iterable[SortParam], PropertyInfo(alias="sortSettings")]

    type: int

    unpack_multiselect_group_view: Annotated[bool, PropertyInfo(alias="unpackMultiselectGroupView")]


ChartSettings: TypeAlias = Union[ChartParam, Optional[object]]

ColumnDescription: TypeAlias = Union[DraftjsParam, Optional[object]]


class Column(TypedDict, total=False):
    column_name: Required[Annotated[str, PropertyInfo(alias="columnName")]]

    column_id: Annotated[str, PropertyInfo(alias="columnId")]

    description: ColumnDescription

    display_validation_error: Annotated[bool, PropertyInfo(alias="displayValidationError")]

    hard_validation: Annotated[bool, PropertyInfo(alias="hardValidation")]

    locked: bool

    required: bool

    string_validation: Annotated[Optional[str], PropertyInfo(alias="stringValidation")]

    validation_message: Annotated[Optional[str], PropertyInfo(alias="validationMessage")]

    validation_no_blanks: Annotated[bool, PropertyInfo(alias="validationNoBlanks")]

    validation_no_duplicates: Annotated[bool, PropertyInfo(alias="validationNoDuplicates")]


Description: TypeAlias = Union[DraftjsParam, Optional[object]]

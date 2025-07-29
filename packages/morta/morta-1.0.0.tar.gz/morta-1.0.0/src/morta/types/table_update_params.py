# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo
from .base_request_context_param import BaseRequestContextParam
from .table.table_column_join_param import TableColumnJoinParam
from .table_join_imported_columns_param import TableJoinImportedColumnsParam

__all__ = ["TableUpdateParams", "Join"]


class TableUpdateParams(TypedDict, total=False):
    allow_comments: Annotated[bool, PropertyInfo(alias="allowComments")]

    context: BaseRequestContextParam

    is_reference_table: Annotated[bool, PropertyInfo(alias="isReferenceTable")]

    joins: Iterable[Join]

    keep_colours_in_sync: Annotated[bool, PropertyInfo(alias="keepColoursInSync")]

    keep_validations_in_sync: Annotated[bool, PropertyInfo(alias="keepValidationsInSync")]

    logo: Optional[str]

    name: str

    sync_hourly_frequency: Annotated[Literal[0, 24], PropertyInfo(alias="syncHourlyFrequency")]

    type: Optional[str]


class Join(TypedDict, total=False):
    data_columns: Annotated[Iterable[TableJoinImportedColumnsParam], PropertyInfo(alias="dataColumns")]

    is_one_to_many: Annotated[bool, PropertyInfo(alias="isOneToMany")]

    join_columns: Annotated[Iterable[TableColumnJoinParam], PropertyInfo(alias="joinColumns")]

    join_table_name: Annotated[str, PropertyInfo(alias="joinTableName")]

    join_view_id: Annotated[str, PropertyInfo(alias="joinViewId")]

    join_view_name: Annotated[str, PropertyInfo(alias="joinViewName")]

    public_id: Annotated[str, PropertyInfo(alias="publicId")]

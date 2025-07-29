# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .table.table_column_param import TableColumnParam
from .base_request_context_param import BaseRequestContextParam
from .table.table_column_join_param import TableColumnJoinParam
from .table_join_imported_columns_param import TableJoinImportedColumnsParam

__all__ = ["TableCreateParams", "Join"]


class TableCreateParams(TypedDict, total=False):
    columns: Required[Iterable[TableColumnParam]]

    name: Required[str]

    project_id: Required[Annotated[str, PropertyInfo(alias="projectId")]]

    context: BaseRequestContextParam

    joins: Iterable[Join]

    type: str


class Join(TypedDict, total=False):
    data_columns: Annotated[Iterable[TableJoinImportedColumnsParam], PropertyInfo(alias="dataColumns")]

    is_one_to_many: Annotated[bool, PropertyInfo(alias="isOneToMany")]

    join_columns: Annotated[Iterable[TableColumnJoinParam], PropertyInfo(alias="joinColumns")]

    join_table_name: Annotated[str, PropertyInfo(alias="joinTableName")]

    join_view_id: Annotated[str, PropertyInfo(alias="joinViewId")]

    join_view_name: Annotated[str, PropertyInfo(alias="joinViewName")]

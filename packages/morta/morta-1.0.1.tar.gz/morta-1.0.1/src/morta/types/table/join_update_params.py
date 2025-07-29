# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .table_column_join_param import TableColumnJoinParam
from ..base_request_context_param import BaseRequestContextParam

__all__ = ["JoinUpdateParams"]


class JoinUpdateParams(TypedDict, total=False):
    table_id: Required[str]

    context: BaseRequestContextParam

    data_columns: Annotated[List[str], PropertyInfo(alias="dataColumns")]

    is_one_to_many: Annotated[bool, PropertyInfo(alias="isOneToMany")]

    join_columns: Annotated[Iterable[TableColumnJoinParam], PropertyInfo(alias="joinColumns")]

    join_view_id: Annotated[str, PropertyInfo(alias="joinViewId")]

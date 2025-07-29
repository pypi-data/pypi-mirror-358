# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo
from .table_column_join_param import TableColumnJoinParam
from ..base_request_context_param import BaseRequestContextParam

__all__ = ["JoinCreateParams"]


class JoinCreateParams(TypedDict, total=False):
    context: BaseRequestContextParam

    data_columns: Annotated[List[str], PropertyInfo(alias="dataColumns")]

    is_one_to_many: Annotated[bool, PropertyInfo(alias="isOneToMany")]

    join_columns: Annotated[Iterable[TableColumnJoinParam], PropertyInfo(alias="joinColumns")]

    join_view_id: Annotated[str, PropertyInfo(alias="joinViewId")]

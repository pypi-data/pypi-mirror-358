# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from ..table_row_action_param import TableRowActionParam
from ...base_request_context_param import BaseRequestContextParam

__all__ = ["RowUpsertParams"]


class RowUpsertParams(TypedDict, total=False):
    rows: Required[Iterable[TableRowActionParam]]

    upsert_column_name: Required[Annotated[str, PropertyInfo(alias="upsertColumnName")]]

    context: BaseRequestContextParam

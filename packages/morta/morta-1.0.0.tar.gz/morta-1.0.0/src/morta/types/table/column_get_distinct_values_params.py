# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Required, TypedDict

__all__ = ["ColumnGetDistinctValuesParams"]


class ColumnGetDistinctValuesParams(TypedDict, total=False):
    table_id: Required[str]

    filter: str
    """Filter criteria for the distinct values"""

    group_columns: List[str]
    """Specify columns for grouping values"""

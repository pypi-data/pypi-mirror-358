# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from datetime import datetime
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["TableRetrieveParams"]


class TableRetrieveParams(TypedDict, total=False):
    columns: List[str]
    """Specific columns to include in the response"""

    distinct_columns: List[str]
    """Columns to apply distinct filtering"""

    filter: str
    """Filter criteria for the table rows"""

    ignore_cached_options: bool
    """Flag to indicate whether to ignore cached options in the response."""

    last_created_at: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Filter for rows created after this date"""

    last_updated_at: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Filter for rows updated after this date"""

    next_page_token: str
    """Token for fetching the next page of results"""

    page: int
    """Page number for pagination"""

    size: int
    """Number of items per page for pagination"""

    sort: str
    """Sorting criteria for the table rows"""

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ViewStreamRowsParams"]


class ViewStreamRowsParams(TypedDict, total=False):
    filter: str
    """Filters to apply to the streaming data."""

    page: int
    """Page number for pagination"""

    process_id: str
    """Optional UUID of a process to filter the data."""

    size: int
    """Number of items per page for pagination"""

    sort: str
    """Sorting parameters for the streaming data."""

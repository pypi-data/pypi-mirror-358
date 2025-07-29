# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["TableDownloadCsvParams"]


class TableDownloadCsvParams(TypedDict, total=False):
    filter: str
    """Filter criteria for the table rows"""

    sort: str
    """Sorting criteria for the table rows"""

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ViewDownloadCsvParams"]


class ViewDownloadCsvParams(TypedDict, total=False):
    filter: str
    """Filters to apply to the CSV data."""

    process_id: str
    """Optional UUID of a process to filter the data."""

    sort: str
    """Sorting parameters for the CSV data."""

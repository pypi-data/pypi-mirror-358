# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["TableGetFileParams"]


class TableGetFileParams(TypedDict, total=False):
    column_id: Required[str]
    """UUID of the column containing the cell."""

    filename: Required[str]
    """Name of the file to retrieve."""

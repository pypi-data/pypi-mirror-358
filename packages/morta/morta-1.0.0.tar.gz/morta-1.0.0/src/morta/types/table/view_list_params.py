# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ViewListParams"]


class ViewListParams(TypedDict, total=False):
    ignore_columns: bool
    """Flag to indicate whether to ignore column data in the response."""

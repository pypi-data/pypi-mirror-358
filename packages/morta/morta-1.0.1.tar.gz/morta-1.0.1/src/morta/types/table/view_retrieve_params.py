# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ViewRetrieveParams"]


class ViewRetrieveParams(TypedDict, total=False):
    ignore_cached_options: bool
    """Flag to indicate whether to ignore cached options in the response."""

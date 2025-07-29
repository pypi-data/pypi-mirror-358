# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["HubSearchResourcesParams"]


class HubSearchResourcesParams(TypedDict, total=False):
    search: Required[str]
    """Search query string"""

    process_public_id: str
    """Optional UUID of a document to restrict the search within a specific document"""

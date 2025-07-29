# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["DocumentRetrieveParams"]


class DocumentRetrieveParams(TypedDict, total=False):
    exclude_children: bool
    """Flag to exclude child elements from the document response"""

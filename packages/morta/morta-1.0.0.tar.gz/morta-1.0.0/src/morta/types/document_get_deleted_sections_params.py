# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["DocumentGetDeletedSectionsParams"]


class DocumentGetDeletedSectionsParams(TypedDict, total=False):
    process_section_id: str
    """Optional UUID of a specific document section to filter deleted sections"""

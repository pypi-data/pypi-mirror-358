# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["DocumentExportParams"]


class DocumentExportParams(TypedDict, total=False):
    page_format: Literal["A1", "A2", "A3", "A4", "letter", "legal"]
    """Page format for the export"""

    page_orientation: Literal["portrait", "landscape"]
    """Page orientation for the export"""

    table_links: bool
    """Include table links in the export"""

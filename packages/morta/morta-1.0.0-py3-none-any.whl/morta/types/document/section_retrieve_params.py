# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["SectionRetrieveParams"]


class SectionRetrieveParams(TypedDict, total=False):
    document_id: Required[str]

    main_parent_section: bool
    """Flag to retrieve the main parent section of the document section"""

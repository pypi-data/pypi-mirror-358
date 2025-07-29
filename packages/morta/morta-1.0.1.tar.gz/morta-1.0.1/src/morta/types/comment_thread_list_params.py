# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["CommentThreadListParams"]


class CommentThreadListParams(TypedDict, total=False):
    reference_id: Required[str]
    """UUID of the reference associated with the comment threads"""

    reference_type: Required[Literal["process_section", "table", "table_view"]]
    """
    Type of the reference (process_section, table, or table_view) associated with
    the comment threads
    """

    main_reference: str
    """Optional main reference for additional filtering"""

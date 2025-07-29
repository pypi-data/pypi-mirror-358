# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["CommentThreadGetStatsParams"]


class CommentThreadGetStatsParams(TypedDict, total=False):
    reference_type: Required[Literal["process_section", "table", "table_view"]]
    """
    Type of the reference (process_section, table, or table_view) for which to
    gather statistics
    """

    main_reference_id: str
    """UUID of the main reference for which to gather statistics"""

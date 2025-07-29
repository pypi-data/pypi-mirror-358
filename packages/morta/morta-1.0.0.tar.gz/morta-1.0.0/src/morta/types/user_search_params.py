# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["UserSearchParams"]


class UserSearchParams(TypedDict, total=False):
    query: Required[str]
    """Query string for searching users"""

    process_id: str
    """Process ID to restrict search"""

    project_id: str
    """Hub ID to restrict search"""

    table_view_id: str
    """Table View ID to restrict search"""

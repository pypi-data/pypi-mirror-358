# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from datetime import datetime
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["NotificationListEventsParams"]


class NotificationListEventsParams(TypedDict, total=False):
    type: Required[Literal["process", "process_section", "process_response", "table", "project", "user"]]
    """The type of the resource (e.g., user, process, table, project)."""

    end_date: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Optional end date to filter the events."""

    page: int
    """Page number for pagination."""

    search: str
    """Optional search term to filter the events."""

    start_date: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Optional start date to filter the events."""

    users: List[str]
    """Optional UUID of a user to filter the events."""

    verb: List[str]
    """Optional list of verbs to filter the events."""

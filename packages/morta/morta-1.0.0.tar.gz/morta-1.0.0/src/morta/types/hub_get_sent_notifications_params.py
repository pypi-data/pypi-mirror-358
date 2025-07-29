# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["HubGetSentNotificationsParams"]


class HubGetSentNotificationsParams(TypedDict, total=False):
    notification_id: Optional[str]
    """UUID of a specific notification to filter the executions"""

    page: int
    """Page number of the notification executions"""

    size: int
    """Number of notification executions per page"""

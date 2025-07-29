# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from .event import Event
from .._models import BaseModel

__all__ = ["NotificationListEventsResponse"]


class NotificationListEventsResponse(BaseModel):
    data: Optional[List[Event]] = None

    metadata: Optional[Dict[str, object]] = None

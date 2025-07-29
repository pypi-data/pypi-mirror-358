# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .notification import Notification

__all__ = ["HubGetNotificationsResponse"]


class HubGetNotificationsResponse(BaseModel):
    data: Optional[List[Notification]] = None

    metadata: Optional[object] = None

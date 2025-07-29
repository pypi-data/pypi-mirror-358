# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel
from .notification import Notification

__all__ = ["NotificationCreateResponse"]


class NotificationCreateResponse(BaseModel):
    data: Optional[Notification] = None

    metadata: Optional[object] = None

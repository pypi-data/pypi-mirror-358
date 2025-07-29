# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["NotificationListEventTypesResponse"]


class NotificationListEventTypesResponse(BaseModel):
    data: Optional[List[str]] = None

    metadata: Optional[object] = None

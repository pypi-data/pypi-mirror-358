# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel
from .user.tag import Tag

__all__ = ["PermissionRetrieveTagResponse"]


class PermissionRetrieveTagResponse(BaseModel):
    data: Optional[Tag] = None

    metadata: Optional[object] = None

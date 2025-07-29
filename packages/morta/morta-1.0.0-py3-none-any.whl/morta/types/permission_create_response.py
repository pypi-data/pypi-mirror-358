# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel
from .access_policy import AccessPolicy

__all__ = ["PermissionCreateResponse"]


class PermissionCreateResponse(BaseModel):
    data: Optional[AccessPolicy] = None

    metadata: Optional[object] = None

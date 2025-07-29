# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .access_policy import AccessPolicy

__all__ = ["PermissionRetrieveResponse"]


class PermissionRetrieveResponse(BaseModel):
    data: Optional[List[AccessPolicy]] = None

    metadata: Optional[object] = None

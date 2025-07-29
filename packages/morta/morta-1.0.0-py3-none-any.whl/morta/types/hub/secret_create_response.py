# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .hub_secret import HubSecret

__all__ = ["SecretCreateResponse"]


class SecretCreateResponse(BaseModel):
    data: Optional[HubSecret] = None

    metadata: Optional[object] = None

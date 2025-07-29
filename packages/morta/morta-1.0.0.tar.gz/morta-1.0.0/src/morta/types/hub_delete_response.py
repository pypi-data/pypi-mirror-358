# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["HubDeleteResponse"]


class HubDeleteResponse(BaseModel):
    data: Optional[str] = None

    metadata: Optional[object] = None

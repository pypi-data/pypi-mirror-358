# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

from .._compat import PYDANTIC_V2
from .._models import BaseModel

__all__ = ["UserCreateResponse"]


class UserCreateResponse(BaseModel):
    data: Optional["User"] = None

    metadata: Optional[object] = None


from .user.user import User

if PYDANTIC_V2:
    UserCreateResponse.model_rebuild()
else:
    UserCreateResponse.update_forward_refs()  # type: ignore

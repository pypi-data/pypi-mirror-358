# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .invited_member import InvitedMember

__all__ = ["InviteUpdateResponse"]


class InviteUpdateResponse(BaseModel):
    data: Optional[InvitedMember] = None

    metadata: Optional[object] = None

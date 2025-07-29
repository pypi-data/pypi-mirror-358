# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .hub.invited_member import InvitedMember

__all__ = ["HubGetInvitedMembersResponse"]


class HubGetInvitedMembersResponse(BaseModel):
    data: Optional[List[InvitedMember]] = None

    metadata: Optional[object] = None

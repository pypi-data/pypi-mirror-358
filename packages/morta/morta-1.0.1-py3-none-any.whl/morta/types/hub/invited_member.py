# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from ..user.tag import Tag
from ..summary_user import SummaryUser

__all__ = ["InvitedMember"]


class InvitedMember(BaseModel):
    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    email: Optional[str] = None

    invited_by: Optional[SummaryUser] = FieldInfo(alias="invitedBy", default=None)

    project_role: Optional[str] = FieldInfo(alias="projectRole", default=None)

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)

    tags: Optional[List[Tag]] = None

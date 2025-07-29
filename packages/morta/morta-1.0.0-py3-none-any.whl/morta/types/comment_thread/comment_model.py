# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from ..summary_user import SummaryUser

__all__ = ["CommentModel"]


class CommentModel(BaseModel):
    comment_text: Optional[str] = FieldInfo(alias="commentText", default=None)

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    deleted_at: Optional[datetime] = FieldInfo(alias="deletedAt", default=None)

    is_owner: Optional[object] = FieldInfo(alias="isOwner", default=None)

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)

    user: Optional[SummaryUser] = None

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .comment_model import CommentModel

__all__ = ["CommentThread", "Resolver"]


class Resolver(BaseModel):
    name: Optional[str] = None


class CommentThread(BaseModel):
    comments: Optional[List[CommentModel]] = None

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    deleted_at: Optional[datetime] = FieldInfo(alias="deletedAt", default=None)

    is_comment_initiator: Optional[object] = FieldInfo(alias="isCommentInitiator", default=None)

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)

    resolved_at: Optional[datetime] = FieldInfo(alias="resolvedAt", default=None)

    resolver: Optional[Resolver] = None

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)

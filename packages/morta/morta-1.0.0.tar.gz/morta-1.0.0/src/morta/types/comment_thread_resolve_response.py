# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .comment_thread.comment_thread import CommentThread

__all__ = ["CommentThreadResolveResponse", "Metadata"]


class Metadata(BaseModel):
    change: Optional[object] = None
    """Changes made to the comment thread"""

    event: Optional[str] = None
    """Event type for the operation"""

    resource_id: Optional[str] = FieldInfo(alias="resourceId", default=None)
    """UUID of the resolved comment thread"""


class CommentThreadResolveResponse(BaseModel):
    data: Optional[CommentThread] = None

    metadata: Optional[Metadata] = None

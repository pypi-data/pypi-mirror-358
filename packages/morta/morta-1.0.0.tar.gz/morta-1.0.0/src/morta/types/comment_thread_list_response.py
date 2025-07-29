# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .comment_thread.comment_thread import CommentThread

__all__ = ["CommentThreadListResponse"]


class CommentThreadListResponse(BaseModel):
    data: Optional[List[CommentThread]] = None

    metadata: Optional[object] = None

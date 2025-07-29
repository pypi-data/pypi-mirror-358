# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel
from .comment_thread.comment_thread import CommentThread

__all__ = ["CommentThreadRetrieveResponse"]


class CommentThreadRetrieveResponse(BaseModel):
    data: Optional[CommentThread] = None

    metadata: Optional[object] = None

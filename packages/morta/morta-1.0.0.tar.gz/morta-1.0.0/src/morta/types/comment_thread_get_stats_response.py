# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["CommentThreadGetStatsResponse", "Data"]


class Data(BaseModel):
    open_comment_threads: int = FieldInfo(alias="openCommentThreads")

    resolved_comment_threads: int = FieldInfo(alias="resolvedCommentThreads")

    reference_id: Optional[str] = FieldInfo(alias="referenceId", default=None)


class CommentThreadGetStatsResponse(BaseModel):
    data: Optional[List[Data]] = None

    metadata: Optional[object] = None

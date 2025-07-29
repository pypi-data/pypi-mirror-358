# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .user_hub import UserHub

__all__ = ["HubGetAIAnswersResponse", "Data"]


class Data(BaseModel):
    answer: Optional[str] = None

    answer_comment: Optional[str] = FieldInfo(alias="answerComment", default=None)

    answer_vote: Optional[bool] = FieldInfo(alias="answerVote", default=None)

    context_urls: Optional[List[str]] = FieldInfo(alias="contextUrls", default=None)

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    question: Optional[str] = None

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)

    user: Optional[UserHub] = None


class HubGetAIAnswersResponse(BaseModel):
    data: Optional[List[Data]] = None

    metadata: Optional[object] = None

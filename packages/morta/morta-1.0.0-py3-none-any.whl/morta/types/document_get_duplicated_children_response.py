# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["DocumentGetDuplicatedChildrenResponse", "Data"]


class Data(BaseModel):
    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    link: Optional[str] = None

    name: Optional[str] = None

    user: Optional[str] = None


class DocumentGetDuplicatedChildrenResponse(BaseModel):
    data: Optional[List[Data]] = None

    metadata: Optional[object] = None

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .summary_user import SummaryUser

__all__ = ["UserListTemplatesResponse", "Data"]


class Data(BaseModel):
    created_by: Optional[SummaryUser] = FieldInfo(alias="createdBy", default=None)


class UserListTemplatesResponse(BaseModel):
    data: Optional[List[Data]] = None

    metadata: Optional[object] = None

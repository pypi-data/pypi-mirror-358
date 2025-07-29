# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["HubGetMembersResponse", "Data", "DataUser"]


class DataUser(BaseModel):
    email: Optional[str] = None

    firebase_user_id: Optional[str] = FieldInfo(alias="firebaseUserId", default=None)

    kind: Optional[str] = None

    name: Optional[str] = None

    profile_picture: Optional[str] = FieldInfo(alias="profilePicture", default=None)

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)

    tags: Optional[object] = None


class Data(BaseModel):
    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    favourite: Optional[bool] = None

    project_role: Optional[str] = FieldInfo(alias="projectRole", default=None)

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)

    user: Optional[DataUser] = None


class HubGetMembersResponse(BaseModel):
    data: Optional[List[Data]] = None

    metadata: Optional[object] = None

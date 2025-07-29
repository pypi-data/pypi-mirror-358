# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["SummaryUser"]


class SummaryUser(BaseModel):
    email: Optional[str] = None

    firebase_user_id: Optional[str] = FieldInfo(alias="firebaseUserId", default=None)

    name: Optional[str] = None

    profile_picture: Optional[str] = FieldInfo(alias="profilePicture", default=None)

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["UserUpdateProfileParams"]


class UserUpdateProfileParams(TypedDict, total=False):
    allow_support_access: Annotated[Optional[bool], PropertyInfo(alias="allowSupportAccess")]

    bio: Optional[str]

    linkedin: Optional[str]

    location: Optional[str]

    name: str

    organisation: Optional[str]

    profile_picture: Annotated[Optional[str], PropertyInfo(alias="profilePicture")]

    twitter: Optional[str]

    university: Optional[str]

    university_degree: Annotated[Optional[str], PropertyInfo(alias="universityDegree")]

    website: Optional[str]

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["HubInviteMultipleUsersParams"]


class HubInviteMultipleUsersParams(TypedDict, total=False):
    emails: List[str]

    project_role: Annotated[Literal["member", "admin", "owner"], PropertyInfo(alias="projectRole")]

    tags: List[str]

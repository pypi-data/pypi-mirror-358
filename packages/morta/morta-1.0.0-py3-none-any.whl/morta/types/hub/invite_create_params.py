# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["InviteCreateParams"]


class InviteCreateParams(TypedDict, total=False):
    email: Required[str]

    project_role: Annotated[Literal["member", "admin", "owner"], PropertyInfo(alias="projectRole")]

    tags: List[str]

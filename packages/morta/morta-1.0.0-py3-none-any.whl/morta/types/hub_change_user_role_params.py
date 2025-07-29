# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["HubChangeUserRoleParams"]


class HubChangeUserRoleParams(TypedDict, total=False):
    hub_id: Required[str]

    role: Required[Literal["owner", "admin", "member"]]

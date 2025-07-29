# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["UserCreateParams"]


class UserCreateParams(TypedDict, total=False):
    email: Required[str]

    name: Required[str]

    password: Required[str]

    opt_out_ai_email: Annotated[bool, PropertyInfo(alias="optOutAiEmail")]

    opt_out_duplication_email: Annotated[bool, PropertyInfo(alias="optOutDuplicationEmail")]

    opt_out_hub_email: Annotated[bool, PropertyInfo(alias="optOutHubEmail")]

    opt_out_sync_email: Annotated[bool, PropertyInfo(alias="optOutSyncEmail")]

    opt_out_welcome_email: Annotated[bool, PropertyInfo(alias="optOutWelcomeEmail")]

    project_id: Annotated[str, PropertyInfo(alias="projectId")]

    template: Optional[str]

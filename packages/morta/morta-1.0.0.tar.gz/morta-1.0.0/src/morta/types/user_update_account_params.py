# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["UserUpdateAccountParams"]


class UserUpdateAccountParams(TypedDict, total=False):
    allow_support_access: Annotated[Optional[bool], PropertyInfo(alias="allowSupportAccess")]

    old_password: Annotated[str, PropertyInfo(alias="oldPassword")]

    opt_out_ai_email: Annotated[Optional[bool], PropertyInfo(alias="optOutAiEmail")]

    opt_out_duplication_email: Annotated[Optional[bool], PropertyInfo(alias="optOutDuplicationEmail")]

    opt_out_hub_email: Annotated[Optional[bool], PropertyInfo(alias="optOutHubEmail")]

    opt_out_sync_email: Annotated[Optional[bool], PropertyInfo(alias="optOutSyncEmail")]

    opt_out_welcome_email: Annotated[Optional[bool], PropertyInfo(alias="optOutWelcomeEmail")]

    password: str

    password_confirm: Annotated[str, PropertyInfo(alias="passwordConfirm")]

    two_factor_code: Annotated[Optional[str], PropertyInfo(alias="twoFactorCode")]

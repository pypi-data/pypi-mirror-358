# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import TypeAlias

from pydantic import Field as FieldInfo

from .._compat import PYDANTIC_V2
from .._models import BaseModel
from .user_hub import UserHub
from .user.api_key import APIKey

__all__ = ["UserUpdateAccountResponse", "Data", "DataSubscriptionManagerUser"]

DataSubscriptionManagerUser: TypeAlias = Union[UserHub, Optional[object]]


class Data(BaseModel):
    id: Optional[int] = None

    aconex_connected: Optional[bool] = FieldInfo(alias="aconexConnected", default=None)

    allow_support_access: Optional[bool] = FieldInfo(alias="allowSupportAccess", default=None)

    allow_support_accesss: Optional[bool] = FieldInfo(alias="allowSupportAccesss", default=None)

    api_keys: Optional[List[APIKey]] = FieldInfo(alias="apiKeys", default=None)

    asite_connected: Optional[bool] = FieldInfo(alias="asiteConnected", default=None)

    auth_token: Optional[str] = FieldInfo(alias="authToken", default=None)

    auth_token_expires_at: Optional[datetime] = FieldInfo(alias="authTokenExpiresAt", default=None)

    autodesk_connected: Optional[bool] = FieldInfo(alias="autodeskConnected", default=None)

    bio: Optional[str] = None

    construction_software: Optional[List[str]] = FieldInfo(alias="constructionSoftware", default=None)

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    eligible_for_free_trial: Optional[bool] = FieldInfo(alias="eligibleForFreeTrial", default=None)

    email: Optional[str] = None

    firebase_user_id: Optional[str] = FieldInfo(alias="firebaseUserId", default=None)

    free_trial_days_remaining: Optional[int] = FieldInfo(alias="freeTrialDaysRemaining", default=None)

    has_password: Optional[object] = FieldInfo(alias="hasPassword", default=None)

    is2_fa_enabled: Optional[object] = FieldInfo(alias="is2FaEnabled", default=None)

    is_on_free_trial: Optional[bool] = FieldInfo(alias="isOnFreeTrial", default=None)

    is_super_admin: Optional[bool] = FieldInfo(alias="isSuperAdmin", default=None)

    kind: Optional[str] = None

    last_login_at: Optional[datetime] = FieldInfo(alias="lastLoginAt", default=None)

    linkedin: Optional[str] = None

    location: Optional[str] = None

    managed_subscription_users: Optional[List["User"]] = FieldInfo(alias="managedSubscriptionUsers", default=None)

    name: Optional[str] = None

    number_of_managed_subscription_users: Optional[int] = FieldInfo(
        alias="numberOfManagedSubscriptionUsers", default=None
    )

    on_scale_plan: Optional[bool] = FieldInfo(alias="onScalePlan", default=None)

    opt_out_ai_email: Optional[bool] = FieldInfo(alias="optOutAiEmail", default=None)

    opt_out_duplication_email: Optional[bool] = FieldInfo(alias="optOutDuplicationEmail", default=None)

    opt_out_hub_email: Optional[bool] = FieldInfo(alias="optOutHubEmail", default=None)

    opt_out_sync_email: Optional[bool] = FieldInfo(alias="optOutSyncEmail", default=None)

    opt_out_welcome_email: Optional[bool] = FieldInfo(alias="optOutWelcomeEmail", default=None)

    organisation: Optional[str] = None

    phone: Optional[str] = None

    procore_connected: Optional[bool] = FieldInfo(alias="procoreConnected", default=None)

    profile_picture: Optional[str] = FieldInfo(alias="profilePicture", default=None)

    projects_worked_on: Optional[List[str]] = FieldInfo(alias="projectsWorkedOn", default=None)

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)

    revizto_connected: Optional[bool] = FieldInfo(alias="reviztoConnected", default=None)

    specialisms: Optional[List[str]] = None

    subscription_level: Optional[int] = FieldInfo(alias="subscriptionLevel", default=None)

    subscription_manager_user: Optional[DataSubscriptionManagerUser] = FieldInfo(
        alias="subscriptionManagerUser", default=None
    )

    subscription_quota: Optional[int] = FieldInfo(alias="subscriptionQuota", default=None)

    tags: Optional[object] = None

    twitter: Optional[str] = None

    university: Optional[str] = None

    university_degree: Optional[str] = FieldInfo(alias="universityDegree", default=None)

    viewpoint_connected: Optional[bool] = FieldInfo(alias="viewpointConnected", default=None)

    website: Optional[str] = None


class UserUpdateAccountResponse(BaseModel):
    data: Optional[Data] = None

    metadata: Optional[object] = None


from .user.user import User

if PYDANTIC_V2:
    UserUpdateAccountResponse.model_rebuild()
    Data.model_rebuild()
else:
    UserUpdateAccountResponse.update_forward_refs()  # type: ignore
    Data.update_forward_refs()  # type: ignore

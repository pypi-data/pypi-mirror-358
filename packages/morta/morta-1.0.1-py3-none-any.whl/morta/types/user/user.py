# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import TypeAlias

from pydantic import Field as FieldInfo

from .api_key import APIKey
from ..._compat import PYDANTIC_V2
from ..._models import BaseModel
from ..user_hub import UserHub

__all__ = ["User", "SubscriptionManagerUser"]

SubscriptionManagerUser: TypeAlias = Union[UserHub, Optional[object]]


class User(BaseModel):
    aconex_connected: Optional[bool] = FieldInfo(alias="aconexConnected", default=None)

    allow_support_accesss: Optional[bool] = FieldInfo(alias="allowSupportAccesss", default=None)

    api_keys: Optional[List[APIKey]] = FieldInfo(alias="apiKeys", default=None)

    asite_connected: Optional[bool] = FieldInfo(alias="asiteConnected", default=None)

    autodesk_connected: Optional[bool] = FieldInfo(alias="autodeskConnected", default=None)

    bio: Optional[str] = None

    construction_software: Optional[List[str]] = FieldInfo(alias="constructionSoftware", default=None)

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    email: Optional[str] = None

    firebase_user_id: Optional[str] = FieldInfo(alias="firebaseUserId", default=None)

    kind: Optional[str] = None

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

    subscription_manager_user: Optional[SubscriptionManagerUser] = FieldInfo(
        alias="subscriptionManagerUser", default=None
    )

    subscription_quota: Optional[int] = FieldInfo(alias="subscriptionQuota", default=None)

    tags: Optional[object] = None

    twitter: Optional[str] = None

    university: Optional[str] = None

    university_degree: Optional[str] = FieldInfo(alias="universityDegree", default=None)

    viewpoint_connected: Optional[bool] = FieldInfo(alias="viewpointConnected", default=None)

    website: Optional[str] = None


if PYDANTIC_V2:
    User.model_rebuild()
else:
    User.update_forward_refs()  # type: ignore

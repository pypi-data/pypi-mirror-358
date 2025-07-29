# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable, Optional
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .create_notification_schema_header_param import CreateNotificationSchemaHeaderParam

__all__ = ["NotificationUpdateParams", "Trigger"]


class NotificationUpdateParams(TypedDict, total=False):
    webhook_url: Required[Annotated[str, PropertyInfo(alias="webhookUrl")]]

    custom_headers: Annotated[Iterable[CreateNotificationSchemaHeaderParam], PropertyInfo(alias="customHeaders")]

    description: Optional[str]

    processes: List[str]

    tables: List[str]

    triggers: Iterable[Trigger]


class Trigger(TypedDict, total=False):
    resource: Required[str]

    verb: Required[str]

    public_id: Annotated[Optional[str], PropertyInfo(alias="publicId")]

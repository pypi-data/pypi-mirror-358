# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo
from .base_request_context_param import BaseRequestContextParam

__all__ = ["HubDuplicateParams"]


class HubDuplicateParams(TypedDict, total=False):
    context: BaseRequestContextParam

    duplicate_permissions: Annotated[bool, PropertyInfo(alias="duplicatePermissions")]

    lock_resource: Annotated[bool, PropertyInfo(alias="lockResource")]

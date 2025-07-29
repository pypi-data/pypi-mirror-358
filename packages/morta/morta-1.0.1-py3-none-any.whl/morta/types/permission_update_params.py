# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

from .base_request_context_param import BaseRequestContextParam

__all__ = ["PermissionUpdateParams"]


class PermissionUpdateParams(TypedDict, total=False):
    role: Required[Literal[0, 1, 2, 3, 4]]

    context: BaseRequestContextParam

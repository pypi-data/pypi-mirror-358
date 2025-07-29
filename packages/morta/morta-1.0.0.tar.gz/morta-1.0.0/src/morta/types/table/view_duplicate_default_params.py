# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from ..base_request_context_param import BaseRequestContextParam

__all__ = ["ViewDuplicateDefaultParams"]


class ViewDuplicateDefaultParams(TypedDict, total=False):
    context: BaseRequestContextParam

    name: str

    type: int

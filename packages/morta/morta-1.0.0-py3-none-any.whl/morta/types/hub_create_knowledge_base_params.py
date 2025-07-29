# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

from .base_request_context_param import BaseRequestContextParam

__all__ = ["HubCreateKnowledgeBaseParams"]


class HubCreateKnowledgeBaseParams(TypedDict, total=False):
    source: Required[str]

    text: Required[str]

    context: BaseRequestContextParam

    link: Optional[str]

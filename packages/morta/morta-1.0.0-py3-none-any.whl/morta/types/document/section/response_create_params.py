# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

from ...base_request_context_param import BaseRequestContextParam

__all__ = ["ResponseCreateParams"]


class ResponseCreateParams(TypedDict, total=False):
    document_id: Required[str]

    context: BaseRequestContextParam

    type: Optional[Literal["Flexible", "File Upload", "Table", "Signature", "Selection"]]

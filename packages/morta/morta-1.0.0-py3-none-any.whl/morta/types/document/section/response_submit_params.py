# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from ...base_request_context_param import BaseRequestContextParam

__all__ = ["ResponseSubmitParams"]


class ResponseSubmitParams(TypedDict, total=False):
    document_id: Required[str]

    document_section_id: Required[str]

    context: BaseRequestContextParam

    response: object

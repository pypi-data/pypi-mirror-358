# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from ..base_request_context_param import BaseRequestContextParam

__all__ = ["CommentCreateParams"]


class CommentCreateParams(TypedDict, total=False):
    comment_text: Required[Annotated[str, PropertyInfo(alias="commentText")]]

    context: BaseRequestContextParam

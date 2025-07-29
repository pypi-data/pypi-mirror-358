# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .base_request_context_param import BaseRequestContextParam

__all__ = ["PermissionCreateParams"]


class PermissionCreateParams(TypedDict, total=False):
    attribute_kind: Required[
        Annotated[Literal["user", "tag", "project", "all_table_tags"], PropertyInfo(alias="attributeKind")]
    ]

    resource_id: Required[Annotated[str, PropertyInfo(alias="resourceId")]]

    resource_kind: Required[Annotated[Literal["process", "table", "table_view"], PropertyInfo(alias="resourceKind")]]

    role: Required[Literal[0, 1, 2, 3, 4]]

    attribute_id: Annotated[str, PropertyInfo(alias="attributeId")]

    context: BaseRequestContextParam

    tag_reference_id: Annotated[str, PropertyInfo(alias="tagReferenceId")]

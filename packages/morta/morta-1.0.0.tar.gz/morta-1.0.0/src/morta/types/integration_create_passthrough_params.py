# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .base_request_context_param import BaseRequestContextParam

__all__ = ["IntegrationCreatePassthroughParams"]


class IntegrationCreatePassthroughParams(TypedDict, total=False):
    method: Required[Literal["GET", "PUT", "POST", "DELETE", "PATCH"]]

    path: Required[str]

    source_system: Required[
        Annotated[
            Literal["viewpoint", "aconex", "autodesk-bim360", "procore", "revizto", "morta", "asite"],
            PropertyInfo(alias="sourceSystem"),
        ]
    ]

    context: BaseRequestContextParam

    data: object

    headers: object

    on_behalf_user_id: Annotated[Optional[str], PropertyInfo(alias="onBehalfUserId")]

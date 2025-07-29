# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .base_request_context_param import BaseRequestContextParam

__all__ = ["HubUpdateHeadingStylingParams"]


class HubUpdateHeadingStylingParams(TypedDict, total=False):
    hub_id: Required[str]

    bold: bool

    colour: str

    context: BaseRequestContextParam

    font_size: Annotated[float, PropertyInfo(alias="fontSize")]

    italic: bool

    numbering_style: Annotated[int, PropertyInfo(alias="numberingStyle")]

    start_at0: Annotated[bool, PropertyInfo(alias="startAt0")]

    underline: bool

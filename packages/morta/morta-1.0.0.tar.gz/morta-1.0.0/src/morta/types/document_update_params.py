# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Optional
from typing_extensions import Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo
from .draftjs_param import DraftjsParam
from .base_request_context_param import BaseRequestContextParam

__all__ = ["DocumentUpdateParams", "Description"]


class DocumentUpdateParams(TypedDict, total=False):
    allow_comments: Annotated[bool, PropertyInfo(alias="allowComments")]

    context: BaseRequestContextParam

    description: Description

    expand_by_default: Annotated[bool, PropertyInfo(alias="expandByDefault")]

    is_template: Annotated[bool, PropertyInfo(alias="isTemplate")]

    locked_template: Annotated[bool, PropertyInfo(alias="lockedTemplate")]

    logo: Optional[str]

    name: Optional[str]

    plaintext_description: Annotated[Optional[str], PropertyInfo(alias="plaintextDescription")]

    type: Optional[str]

    variables: Optional[List[str]]


Description: TypeAlias = Union[DraftjsParam, Optional[object]]

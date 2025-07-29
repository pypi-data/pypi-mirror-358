# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from typing_extensions import Required, Annotated, TypeAlias, TypedDict

from ..._utils import PropertyInfo
from ..draftjs_param import DraftjsParam
from ..base_request_context_param import BaseRequestContextParam

__all__ = ["CreateDocumentSectionParam", "Description"]

Description: TypeAlias = Union[DraftjsParam, Optional[object]]


class CreateDocumentSectionParam(TypedDict, total=False):
    name: Required[str]

    context: BaseRequestContextParam

    description: Description

    parent_id: Annotated[Optional[str], PropertyInfo(alias="parentId")]

    plaintext_description: Annotated[Optional[str], PropertyInfo(alias="plaintextDescription")]

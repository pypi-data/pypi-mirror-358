# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ApikeyUpdateParams"]


class ApikeyUpdateParams(TypedDict, total=False):
    access_level: Required[Annotated[Literal[0, 1], PropertyInfo(alias="accessLevel")]]

    document_restrictions: Annotated[Optional[List[str]], PropertyInfo(alias="documentRestrictions")]

    name: Optional[str]

    project_restrictions: Annotated[Optional[List[str]], PropertyInfo(alias="projectRestrictions")]

    table_restrictions: Annotated[Optional[List[str]], PropertyInfo(alias="tableRestrictions")]

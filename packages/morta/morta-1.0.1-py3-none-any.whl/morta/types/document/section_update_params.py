# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from typing_extensions import Required, Annotated, TypeAlias, TypedDict

from ..._utils import PropertyInfo
from ..draftjs_param import DraftjsParam
from ..base_request_context_param import BaseRequestContextParam

__all__ = ["SectionUpdateParams", "Description"]


class SectionUpdateParams(TypedDict, total=False):
    document_id: Required[str]

    context: BaseRequestContextParam

    description: Description

    name: Optional[str]

    page_break_before: Annotated[Optional[bool], PropertyInfo(alias="pageBreakBefore")]

    pdf_include_description: Annotated[Optional[bool], PropertyInfo(alias="pdfIncludeDescription")]

    pdf_include_section: Annotated[Optional[bool], PropertyInfo(alias="pdfIncludeSection")]

    plaintext_description: Annotated[Optional[str], PropertyInfo(alias="plaintextDescription")]


Description: TypeAlias = Union[DraftjsParam, Optional[object]]

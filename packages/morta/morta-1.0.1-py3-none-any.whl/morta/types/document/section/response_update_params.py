# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from ...base_request_context_param import BaseRequestContextParam

__all__ = ["ResponseUpdateParams"]


class ResponseUpdateParams(TypedDict, total=False):
    document_id: Required[str]

    document_section_id: Required[str]

    context: BaseRequestContextParam

    enable_submission: Annotated[Optional[bool], PropertyInfo(alias="enableSubmission")]

    pdf_include_response: Annotated[Optional[bool], PropertyInfo(alias="pdfIncludeResponse")]

    reset_after_response: Annotated[Optional[bool], PropertyInfo(alias="resetAfterResponse")]

    type: Optional[Literal["Flexible", "File Upload", "Table", "Signature", "Selection"]]

    type_options: Annotated[object, PropertyInfo(alias="typeOptions")]

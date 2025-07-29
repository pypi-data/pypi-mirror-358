# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .draftjs import Draftjs
from .._compat import PYDANTIC_V2
from .._models import BaseModel
from .document.section.document_response import DocumentResponse

__all__ = ["MortaDocumentSection"]


class MortaDocumentSection(BaseModel):
    children: Optional[List["MortaDocumentSection"]] = None

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    deleted_at: Optional[datetime] = FieldInfo(alias="deletedAt", default=None)

    description: Optional[Draftjs] = None

    is_deleted: Optional[bool] = FieldInfo(alias="isDeleted", default=None)

    name: Optional[str] = None

    open_comment_threads: Optional[int] = FieldInfo(alias="openCommentThreads", default=None)

    page_break_before: Optional[bool] = FieldInfo(alias="pageBreakBefore", default=None)

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    pdf_include_description: Optional[bool] = FieldInfo(alias="pdfIncludeDescription", default=None)

    pdf_include_section: Optional[bool] = FieldInfo(alias="pdfIncludeSection", default=None)

    position: Optional[int] = None

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)

    responses: Optional[List[DocumentResponse]] = None


if PYDANTIC_V2:
    MortaDocumentSection.model_rebuild()
else:
    MortaDocumentSection.update_forward_refs()  # type: ignore

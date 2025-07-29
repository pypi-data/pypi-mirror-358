# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ...._models import BaseModel
from ...summary_user import SummaryUser

__all__ = ["DocumentResponse"]


class DocumentResponse(BaseModel):
    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    deleted_at: Optional[datetime] = FieldInfo(alias="deletedAt", default=None)

    enable_submission: Optional[bool] = FieldInfo(alias="enableSubmission", default=None)

    is_deleted: Optional[bool] = FieldInfo(alias="isDeleted", default=None)

    pdf_include_response: Optional[bool] = FieldInfo(alias="pdfIncludeResponse", default=None)

    position: Optional[int] = None

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)

    reset_after_response: Optional[bool] = FieldInfo(alias="resetAfterResponse", default=None)

    response: Optional[object] = None

    response_date: Optional[datetime] = FieldInfo(alias="responseDate", default=None)

    type: Optional[str] = None

    type_options: Optional[object] = FieldInfo(alias="typeOptions", default=None)

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)

    user: Optional[SummaryUser] = None

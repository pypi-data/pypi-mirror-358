# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["HomeHub"]


class HomeHub(BaseModel):
    ai_search_enabled: Optional[bool] = FieldInfo(alias="aiSearchEnabled", default=None)

    allow_document_export: Optional[bool] = FieldInfo(alias="allowDocumentExport", default=None)

    allow_table_export: Optional[bool] = FieldInfo(alias="allowTableExport", default=None)

    deleted_at: Optional[datetime] = FieldInfo(alias="deletedAt", default=None)

    domains_access: Optional[List[str]] = FieldInfo(alias="domainsAccess", default=None)

    font_colour: Optional[str] = FieldInfo(alias="fontColour", default=None)

    hide_process_created: Optional[bool] = FieldInfo(alias="hideProcessCreated", default=None)

    is_deleted: Optional[bool] = FieldInfo(alias="isDeleted", default=None)

    mfa_required: Optional[bool] = FieldInfo(alias="mfaRequired", default=None)

    name: Optional[str] = None

    primary_colour: Optional[str] = FieldInfo(alias="primaryColour", default=None)

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)

    word_template: Optional[str] = FieldInfo(alias="wordTemplate", default=None)

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["Event"]


class Event(BaseModel):
    change: Optional[object] = None

    change_id: Optional[str] = FieldInfo(alias="changeId", default=None)

    channel: Optional[str] = None

    context: Optional[object] = None

    context_process_id: Optional[int] = FieldInfo(alias="contextProcessId", default=None)

    context_process_response_id: Optional[int] = FieldInfo(alias="contextProcessResponseId", default=None)

    context_process_section_id: Optional[int] = FieldInfo(alias="contextProcessSectionId", default=None)

    context_table_column_id: Optional[int] = FieldInfo(alias="contextTableColumnId", default=None)

    context_table_id: Optional[int] = FieldInfo(alias="contextTableId", default=None)

    context_table_view_id: Optional[int] = FieldInfo(alias="contextTableViewId", default=None)

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    project_id: Optional[int] = FieldInfo(alias="projectId", default=None)

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)

    resource: Optional[str] = None

    resource_public_id: Optional[str] = FieldInfo(alias="resourcePublicId", default=None)

    user_id: Optional[int] = FieldInfo(alias="userId", default=None)

    verb: Optional[str] = None

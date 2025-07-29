# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["SimpleHub", "HeadingStyle", "ProjectList", "ProjectListUser"]


class HeadingStyle(BaseModel):
    bold: Optional[bool] = None

    colour: Optional[str] = None

    font_size: Optional[float] = FieldInfo(alias="fontSize", default=None)

    italic: Optional[bool] = None

    level: Optional[int] = None

    numbering_style: Optional[int] = FieldInfo(alias="numberingStyle", default=None)

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)

    start_at0: Optional[bool] = FieldInfo(alias="startAt0", default=None)

    underline: Optional[bool] = None


class ProjectListUser(BaseModel):
    email: Optional[str] = None

    firebase_user_id: Optional[str] = FieldInfo(alias="firebaseUserId", default=None)

    kind: Optional[str] = None

    name: Optional[str] = None

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)


class ProjectList(BaseModel):
    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    favourite: Optional[bool] = None

    project_role: Optional[str] = FieldInfo(alias="projectRole", default=None)

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)

    user: Optional[ProjectListUser] = None


class SimpleHub(BaseModel):
    ai_search_enabled: Optional[bool] = FieldInfo(alias="aiSearchEnabled", default=None)

    allow_document_export: Optional[bool] = FieldInfo(alias="allowDocumentExport", default=None)

    allow_table_export: Optional[bool] = FieldInfo(alias="allowTableExport", default=None)

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    default_banner: Optional[str] = FieldInfo(alias="defaultBanner", default=None)

    default_date_format: Optional[str] = FieldInfo(alias="defaultDateFormat", default=None)

    default_datetime_format: Optional[str] = FieldInfo(alias="defaultDatetimeFormat", default=None)

    default_header_background_color: Optional[str] = FieldInfo(alias="defaultHeaderBackgroundColor", default=None)

    default_header_text_color: Optional[str] = FieldInfo(alias="defaultHeaderTextColor", default=None)

    default_process_id: Optional[str] = FieldInfo(alias="defaultProcessId", default=None)

    deleted_at: Optional[datetime] = FieldInfo(alias="deletedAt", default=None)

    domains_access: Optional[List[str]] = FieldInfo(alias="domainsAccess", default=None)

    font_colour: Optional[str] = FieldInfo(alias="fontColour", default=None)

    heading_styles: Optional[List[HeadingStyle]] = FieldInfo(alias="headingStyles", default=None)

    hide_process_created: Optional[bool] = FieldInfo(alias="hideProcessCreated", default=None)

    image: Optional[str] = None

    is_deleted: Optional[bool] = FieldInfo(alias="isDeleted", default=None)

    logo: Optional[str] = None

    mfa_required: Optional[bool] = FieldInfo(alias="mfaRequired", default=None)

    name: Optional[str] = None

    primary_colour: Optional[str] = FieldInfo(alias="primaryColour", default=None)

    process_title_alignment: Optional[str] = FieldInfo(alias="processTitleAlignment", default=None)

    process_title_bold: Optional[bool] = FieldInfo(alias="processTitleBold", default=None)

    process_title_colour: Optional[str] = FieldInfo(alias="processTitleColour", default=None)

    process_title_font_size: Optional[float] = FieldInfo(alias="processTitleFontSize", default=None)

    process_title_italic: Optional[bool] = FieldInfo(alias="processTitleItalic", default=None)

    process_title_underline: Optional[bool] = FieldInfo(alias="processTitleUnderline", default=None)

    project_list: Optional[List[ProjectList]] = FieldInfo(alias="projectList", default=None)

    public: Optional[bool] = None

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)

    word_template: Optional[str] = FieldInfo(alias="wordTemplate", default=None)

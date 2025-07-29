# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Optional
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo

__all__ = ["HubUpdateParams", "BulkUpdateText", "BulkUpdateTextBulkUpdateText"]


class HubUpdateParams(TypedDict, total=False):
    ai_search_enabled: Annotated[Optional[bool], PropertyInfo(alias="aiSearchEnabled")]

    allow_document_export: Annotated[Optional[bool], PropertyInfo(alias="allowDocumentExport")]

    allow_table_export: Annotated[Optional[bool], PropertyInfo(alias="allowTableExport")]

    bulk_update_text: Annotated[BulkUpdateText, PropertyInfo(alias="bulkUpdateText")]

    default_banner: Annotated[Optional[str], PropertyInfo(alias="defaultBanner")]

    default_date_format: Annotated[Optional[str], PropertyInfo(alias="defaultDateFormat")]

    default_datetime_format: Annotated[Optional[str], PropertyInfo(alias="defaultDatetimeFormat")]

    default_header_background_color: Annotated[Optional[str], PropertyInfo(alias="defaultHeaderBackgroundColor")]

    default_header_text_color: Annotated[Optional[str], PropertyInfo(alias="defaultHeaderTextColor")]

    default_process_id: Annotated[Optional[str], PropertyInfo(alias="defaultProcessId")]

    domains_access: Annotated[Optional[List[str]], PropertyInfo(alias="domainsAccess")]

    font_colour: Annotated[Optional[str], PropertyInfo(alias="fontColour")]

    hide_process_created: Annotated[Optional[bool], PropertyInfo(alias="hideProcessCreated")]

    logo: Optional[str]

    mfa_required: Annotated[Optional[bool], PropertyInfo(alias="mfaRequired")]

    name: Optional[str]

    primary_colour: Annotated[Optional[str], PropertyInfo(alias="primaryColour")]

    process_title_alignment: Annotated[
        Optional[Literal["left", "center", "right"]], PropertyInfo(alias="processTitleAlignment")
    ]

    process_title_bold: Annotated[Optional[bool], PropertyInfo(alias="processTitleBold")]

    process_title_colour: Annotated[Optional[str], PropertyInfo(alias="processTitleColour")]

    process_title_font_size: Annotated[Optional[float], PropertyInfo(alias="processTitleFontSize")]

    process_title_italic: Annotated[Optional[bool], PropertyInfo(alias="processTitleItalic")]

    process_title_underline: Annotated[Optional[bool], PropertyInfo(alias="processTitleUnderline")]

    public: Optional[bool]

    word_template: Annotated[Optional[str], PropertyInfo(alias="wordTemplate")]


class BulkUpdateTextBulkUpdateText(TypedDict, total=False):
    replace_text: Required[Annotated[str, PropertyInfo(alias="replaceText")]]

    search_text: Required[Annotated[str, PropertyInfo(alias="searchText")]]


BulkUpdateText: TypeAlias = Union[BulkUpdateTextBulkUpdateText, Optional[object]]

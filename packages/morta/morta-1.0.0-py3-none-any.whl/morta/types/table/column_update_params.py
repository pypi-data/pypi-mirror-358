# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from ..._utils import PropertyInfo
from ..draftjs_param import DraftjsParam
from .table_column_alter_param import TableColumnAlterParam
from ..base_request_context_param import BaseRequestContextParam
from .select_options_lookup_param import SelectOptionsLookupParam

__all__ = ["ColumnUpdateParams", "AlterOptions", "Description"]


class ColumnUpdateParams(TypedDict, total=False):
    table_id: Required[str]

    aconex_synced: Annotated[int, PropertyInfo(alias="aconexSynced")]

    aconex_workflows_synced: Annotated[int, PropertyInfo(alias="aconexWorkflowsSynced")]

    aggregate: int

    alter_options: Annotated[AlterOptions, PropertyInfo(alias="alterOptions")]

    asite_documents_synced: Annotated[int, PropertyInfo(alias="asiteDocumentsSynced")]

    asite_forms_synced: Annotated[int, PropertyInfo(alias="asiteFormsSynced")]

    autodesk_bim360_checklists_synced: Annotated[int, PropertyInfo(alias="autodeskBim360ChecklistsSynced")]

    autodesk_bim360_issues_synced: Annotated[int, PropertyInfo(alias="autodeskBim360IssuesSynced")]

    autodesk_bim360_models_synced: Annotated[int, PropertyInfo(alias="autodeskBim360ModelsSynced")]

    autodesk_bim360_synced: Annotated[int, PropertyInfo(alias="autodeskBim360Synced")]

    autodesk_bim360_users_synced: Annotated[int, PropertyInfo(alias="autodeskBim360UsersSynced")]

    context: BaseRequestContextParam

    date_format: Annotated[Optional[str], PropertyInfo(alias="dateFormat")]

    decimal_places: Annotated[int, PropertyInfo(alias="decimalPlaces")]

    description: Description

    display_link: Annotated[bool, PropertyInfo(alias="displayLink")]

    export_width: Annotated[Optional[int], PropertyInfo(alias="exportWidth")]

    formula: Optional[str]

    formula_enabled: Annotated[bool, PropertyInfo(alias="formulaEnabled")]

    header_background_color: Annotated[Optional[str], PropertyInfo(alias="headerBackgroundColor")]

    header_text_color: Annotated[Optional[str], PropertyInfo(alias="headerTextColor")]

    is_indexed: Annotated[bool, PropertyInfo(alias="isIndexed")]

    is_joined: Annotated[Optional[bool], PropertyInfo(alias="isJoined")]

    kind: Literal[
        "text",
        "datetime",
        "date",
        "link",
        "multilink",
        "select",
        "multiselect",
        "integer",
        "float",
        "percentage",
        "tag",
        "variable",
        "attachment",
        "phone",
        "email",
        "vote",
        "checkbox",
        "duration",
    ]

    kind_options: Annotated[SelectOptionsLookupParam, PropertyInfo(alias="kindOptions")]

    morta_synced: Annotated[int, PropertyInfo(alias="mortaSynced")]

    name: str

    procore_synced: Annotated[int, PropertyInfo(alias="procoreSynced")]

    public_id: Annotated[str, PropertyInfo(alias="publicId")]

    revizto_issues_synced: Annotated[int, PropertyInfo(alias="reviztoIssuesSynced")]

    script: Optional[str]

    script_enabled: Annotated[bool, PropertyInfo(alias="scriptEnabled")]

    thousand_separator: Annotated[bool, PropertyInfo(alias="thousandSeparator")]

    viewpoint_rfis_synced: Annotated[int, PropertyInfo(alias="viewpointRfisSynced")]

    viewpoint_synced: Annotated[int, PropertyInfo(alias="viewpointSynced")]

    width: int


AlterOptions: TypeAlias = Union[TableColumnAlterParam, Optional[object]]

Description: TypeAlias = Union[DraftjsParam, Optional[object]]

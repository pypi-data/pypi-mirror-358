# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..project import Project
from ..._models import BaseModel
from ..table_join import TableJoin
from .table_column import TableColumn

__all__ = ["Table", "SyncUser"]


class SyncUser(BaseModel):
    name: Optional[str] = None

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)


class Table(BaseModel):
    allow_comments: Optional[bool] = FieldInfo(alias="allowComments", default=None)

    autodesk_bim360_model_properties: Optional[object] = FieldInfo(alias="autodeskBim360ModelProperties", default=None)

    columns: Optional[List[TableColumn]] = None

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    default_view_id: Optional[str] = FieldInfo(alias="defaultViewId", default=None)

    deleted_at: Optional[datetime] = FieldInfo(alias="deletedAt", default=None)

    failed_sync_attempts: Optional[int] = FieldInfo(alias="failedSyncAttempts", default=None)

    is_aconex_synced: Optional[bool] = FieldInfo(alias="isAconexSynced", default=None)

    is_aconex_workflows_synced: Optional[bool] = FieldInfo(alias="isAconexWorkflowsSynced", default=None)

    is_asite_documents_synced: Optional[bool] = FieldInfo(alias="isAsiteDocumentsSynced", default=None)

    is_asite_forms_synced: Optional[bool] = FieldInfo(alias="isAsiteFormsSynced", default=None)

    is_autodesk_bim360_checklists_synced: Optional[bool] = FieldInfo(
        alias="isAutodeskBim360ChecklistsSynced", default=None
    )

    is_autodesk_bim360_issues_synced: Optional[bool] = FieldInfo(alias="isAutodeskBim360IssuesSynced", default=None)

    is_autodesk_bim360_models_synced: Optional[bool] = FieldInfo(alias="isAutodeskBim360ModelsSynced", default=None)

    is_autodesk_bim360_synced: Optional[bool] = FieldInfo(alias="isAutodeskBim360Synced", default=None)

    is_autodesk_bim360_users_synced: Optional[bool] = FieldInfo(alias="isAutodeskBim360UsersSynced", default=None)

    is_deleted: Optional[bool] = FieldInfo(alias="isDeleted", default=None)

    is_morta_columns_synced: Optional[bool] = FieldInfo(alias="isMortaColumnsSynced", default=None)

    is_morta_comments_synced: Optional[bool] = FieldInfo(alias="isMortaCommentsSynced", default=None)

    is_morta_projects_synced: Optional[bool] = FieldInfo(alias="isMortaProjectsSynced", default=None)

    is_morta_resources_synced: Optional[bool] = FieldInfo(alias="isMortaResourcesSynced", default=None)

    is_morta_synced: Optional[bool] = FieldInfo(alias="isMortaSynced", default=None)

    is_morta_users_synced: Optional[bool] = FieldInfo(alias="isMortaUsersSynced", default=None)

    is_procore_synced: Optional[bool] = FieldInfo(alias="isProcoreSynced", default=None)

    is_reference_table: Optional[bool] = FieldInfo(alias="isReferenceTable", default=None)

    is_revizto_issues_synced: Optional[bool] = FieldInfo(alias="isReviztoIssuesSynced", default=None)

    is_synced: Optional[bool] = FieldInfo(alias="isSynced", default=None)

    is_syncing: Optional[bool] = FieldInfo(alias="isSyncing", default=None)

    is_viewpoint_rfis_synced: Optional[bool] = FieldInfo(alias="isViewpointRfisSynced", default=None)

    is_viewpoint_synced: Optional[bool] = FieldInfo(alias="isViewpointSynced", default=None)

    joins: Optional[List[TableJoin]] = None

    keep_colours_in_sync: Optional[bool] = FieldInfo(alias="keepColoursInSync", default=None)

    keep_validations_in_sync: Optional[bool] = FieldInfo(alias="keepValidationsInSync", default=None)

    last_sync: Optional[datetime] = FieldInfo(alias="lastSync", default=None)

    locked_from_duplication: Optional[bool] = FieldInfo(alias="lockedFromDuplication", default=None)

    logo: Optional[str] = None

    name: Optional[str] = None

    project_name: Optional[str] = FieldInfo(alias="projectName", default=None)

    project_public_id: Optional[str] = FieldInfo(alias="projectPublicId", default=None)

    projects: Optional[List[Project]] = None

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)

    sync_hourly_frequency: Optional[int] = FieldInfo(alias="syncHourlyFrequency", default=None)

    sync_user: Optional[SyncUser] = FieldInfo(alias="syncUser", default=None)

    type: Optional[str] = None

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)

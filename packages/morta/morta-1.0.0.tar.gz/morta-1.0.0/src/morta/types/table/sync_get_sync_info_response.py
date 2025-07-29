# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["SyncGetSyncInfoResponse", "Data"]


class Data(BaseModel):
    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

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

    is_revizto_issues_synced: Optional[bool] = FieldInfo(alias="isReviztoIssuesSynced", default=None)

    is_synced: Optional[bool] = FieldInfo(alias="isSynced", default=None)

    is_syncing: Optional[bool] = FieldInfo(alias="isSyncing", default=None)

    is_viewpoint_rfis_synced: Optional[bool] = FieldInfo(alias="isViewpointRfisSynced", default=None)

    is_viewpoint_synced: Optional[bool] = FieldInfo(alias="isViewpointSynced", default=None)

    last_sync: Optional[datetime] = FieldInfo(alias="lastSync", default=None)

    name: Optional[str] = None

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)

    sync_hourly_frequency: Optional[int] = FieldInfo(alias="syncHourlyFrequency", default=None)

    type: Optional[str] = None

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)


class SyncGetSyncInfoResponse(BaseModel):
    data: Optional[Data] = None

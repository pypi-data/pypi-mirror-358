# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .action import Action
from .table1 import Table1
from .trigger import Trigger
from .._models import BaseModel
from .summary_user import SummaryUser
from .document.document import Document

__all__ = ["Notification"]


class Notification(BaseModel):
    actions: List[Action]

    public_id: str = FieldInfo(alias="publicId")

    triggers: List[Trigger]

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    description: Optional[str] = None

    processes: Optional[List[Document]] = None

    tables: Optional[List[Table1]] = None

    user: Optional[SummaryUser] = None

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .simple_hub import SimpleHub

__all__ = ["HubRetrieveResponse", "Data", "DataFolder", "DataFolderChildFolder"]


class DataFolderChildFolder(BaseModel):
    name: Optional[str] = None


class DataFolder(BaseModel):
    child_folders: Optional[List[DataFolderChildFolder]] = FieldInfo(alias="childFolders", default=None)

    name: Optional[str] = None


class Data(BaseModel):
    folders: Optional[List[DataFolder]] = None

    project_details: Optional[SimpleHub] = FieldInfo(alias="projectDetails", default=None)

    role: Optional[str] = None
    """User's role in the hub"""


class HubRetrieveResponse(BaseModel):
    data: Optional[Data] = None

    metadata: Optional[object] = None

from typing import Dict, List, Optional, Union
import bleach
import re
from bson import ObjectId
from pydantic import (
    BaseModel,
    Field,
    validator,
)

from depictio.api.v1.models.base import MongoModel, PyObjectId

class DashboardData(MongoModel):
    dashboard_id: str
    # id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    version: str
    tmp_children_data: Optional[List]
    stored_layout_data: Dict
    stored_metadata: List
    stored_edit_dashboard_mode_button: List
    stored_add_button: Dict

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: lambda oid: str(oid),  # or `str` for simplicity
        }
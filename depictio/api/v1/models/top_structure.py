import re
from typing import List
from pydantic import (
    BaseModel,
    validator,
)
from depictio.api.v1.endpoints.workflow_endpoints.models import Workflow


class RootConfig(BaseModel):
    depictio_version: str
    workflows: List[Workflow]

    @validator("depictio_version")
    def validate_version(cls, v):
        # Using a simple regex pattern to validate semantic versioning
        pattern = r"^\d+\.\d+\.\d+$"
        if not re.match(pattern, v):
            raise ValueError("Invalid version number, must be in format X.Y.Z where X, Y, Z are integers")
        return v

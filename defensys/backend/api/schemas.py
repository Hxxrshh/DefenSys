from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from typing import List, Optional
import datetime

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    repository_url: str = Field(..., min_length=1)

class ProjectCreate(ProjectBase):
    description: Optional[str] = Field(None, max_length=500)

class Project(ProjectBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class ScanBase(BaseModel):
    project_id: int
    status: str
    scan_type: Optional[str] = Field(None, max_length=100, description="Type of scan performed")

class ScanCreate(ScanBase):
    pass

class Scan(ScanBase):
    id: int
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

# User-friendly scan request schemas
class SimpleScanRequest(BaseModel):
    repository_url: str = Field(..., description="Repository URL to scan")
    scan_category: str = Field(..., description="User-friendly scan category")
    project_name: Optional[str] = Field(None, description="Optional project name")

class ScanRecommendationRequest(BaseModel):
    repository_url: Optional[str] = Field(None, description="Repository URL for analysis")
    path: Optional[str] = Field(None, description="Local path for analysis")

class VulnerabilityBase(BaseModel):
    scan_id: int
    type: str
    severity: str
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None

class VulnerabilityCreate(VulnerabilityBase):
    pass

class Vulnerability(VulnerabilityBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

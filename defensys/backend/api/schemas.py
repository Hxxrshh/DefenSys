from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from typing import List, Optional, Dict, Any
import datetime

# ==================== TARGET SCHEMAS ====================

class TargetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    target_type: str = Field(..., description="Type: domain, ip, cidr, url")
    value: str = Field(..., description="Target value (IP, domain, URL, etc.)")
    description: Optional[str] = None

class TargetCreate(TargetBase):
    pass

class Target(TargetBase):
    id: int
    created_at: datetime.datetime
    last_scanned: Optional[datetime.datetime] = None
    is_active: bool = True
    enumeration_data: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

# ==================== PROJECT SCHEMAS ====================

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    repository_url: str = Field(..., min_length=1)

class ProjectCreate(ProjectBase):
    description: Optional[str] = Field(None, max_length=500)

class Project(ProjectBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

# ==================== SCAN SCHEMAS ====================

class ScanBase(BaseModel):
    project_id: Optional[int] = None
    target_id: Optional[int] = None
    status: str
    scan_type: Optional[str] = Field(None, max_length=100, description="Type of scan performed")
    scan_tools: Optional[List[str]] = None
    progress: int = Field(0, ge=0, le=100)
    current_stage: Optional[str] = None

class ScanCreate(BaseModel):
    target_id: Optional[int] = Field(None, description="Target ID to scan")
    project_id: Optional[int] = Field(None, description="Associated project")
    scan_type: str = Field(..., description="Type: network, web, full, quick")
    scan_tools: Optional[List[str]] = Field(None, description="Specific tools to use")

class ScanStart(BaseModel):
    """Request to start a new scan"""
    target_value: str = Field(..., description="Target IP/domain/URL to scan")
    target_type: str = Field("ip", description="Target type: ip, domain, url, cidr")
    scan_type: str = Field("default", description="Scan type: quick, default, full, network, web")
    scan_tools: Optional[List[str]] = Field(None, description="Specific tools: nmap, nuclei, nikto, zap")
    target_name: Optional[str] = Field(None, description="Optional target name")

class Scan(ScanBase):
    id: int
    created_at: datetime.datetime
    started_at: Optional[datetime.datetime] = None
    completed_at: Optional[datetime.datetime] = None
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ScanProgress(BaseModel):
    """Real-time scan progress update"""
    scan_id: int
    status: str
    progress: int
    current_stage: str
    findings_count: int = 0
    vulnerabilities_count: int = 0

# ==================== VULNERABILITY SCHEMAS ====================

class VulnerabilityBase(BaseModel):
    scan_id: int
    scanner_name: str
    scanner_type: str
    severity: str
    title: str
    description: str
    target_host: Optional[str] = None
    target_port: Optional[int] = None
    url: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    cve_ids: Optional[List[str]] = None
    cvss_score: Optional[str] = None
    references: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    remediation: Optional[str] = None

class VulnerabilityCreate(VulnerabilityBase):
    pass

class Vulnerability(VulnerabilityBase):
    id: int
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

# ==================== FINDING SCHEMAS ====================

class FindingBase(BaseModel):
    scan_id: int
    finding_type: str
    scanner_name: str
    title: str
    description: str
    severity: str = "INFO"
    host: Optional[str] = None
    port: Optional[int] = None
    protocol: Optional[str] = None
    service: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class FindingCreate(FindingBase):
    pass

class Finding(FindingBase):
    id: int
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

# ==================== SCAN RESULTS SCHEMAS ====================

class ScanResults(BaseModel):
    """Complete scan results"""
    scan: Scan
    vulnerabilities: List[Vulnerability]
    findings: List[Finding]
    summary: Dict[str, Any]

# ==================== LEGACY SCHEMAS (for backward compatibility) ====================

class SimpleScanRequest(BaseModel):
    repository_url: str = Field(..., description="Repository URL to scan")
    scan_category: str = Field(..., description="User-friendly scan category")
    project_name: Optional[str] = Field(None, description="Optional project name")

class ScanRecommendationRequest(BaseModel):
    repository_url: Optional[str] = Field(None, description="Repository URL for analysis")
    path: Optional[str] = Field(None, description="Local path for analysis")

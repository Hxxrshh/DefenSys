from sqlalchemy.orm import Session
from sqlalchemy import desc
from . import models, schemas
import datetime
from typing import List, Optional, Dict, Any

# ==================== TARGET CRUD ====================

def create_target(db: Session, target: schemas.TargetCreate):
    """Create a new target"""
    db_target = models.Target(**target.model_dump())
    db.add(db_target)
    db.commit()
    db.refresh(db_target)
    return db_target

def get_target(db: Session, target_id: int):
    """Get target by ID"""
    return db.query(models.Target).filter(models.Target.id == target_id).first()

def get_target_by_value(db: Session, value: str):
    """Get target by its value (IP, domain, etc.)"""
    return db.query(models.Target).filter(models.Target.value == value).first()

def get_targets(db: Session, skip: int = 0, limit: int = 100, active_only: bool = True):
    """Get list of targets"""
    query = db.query(models.Target)
    if active_only:
        query = query.filter(models.Target.is_active == True)
    return query.order_by(desc(models.Target.created_at)).offset(skip).limit(limit).all()

def update_target(db: Session, target_id: int, updates: Dict[str, Any]):
    """Update target fields"""
    db_target = get_target(db, target_id)
    if db_target:
        for key, value in updates.items():
            setattr(db_target, key, value)
        db.commit()
        db.refresh(db_target)
    return db_target

def update_target_enumeration(db: Session, target_id: int, enumeration_data: Dict[str, Any]):
    """Update enumeration data for target"""
    return update_target(db, target_id, {
        "enumeration_data": enumeration_data,
        "last_scanned": datetime.datetime.utcnow()
    })

def delete_target(db: Session, target_id: int):
    """Soft delete target"""
    return update_target(db, target_id, {"is_active": False})

# ==================== PROJECT CRUD ====================

def get_project(db: Session, project_id: int):
    return db.query(models.Project).filter(models.Project.id == project_id).first()

def get_projects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Project).offset(skip).limit(limit).all()

def create_project(db: Session, project: schemas.ProjectCreate):
    db_project = models.Project(name=project.name, repository_url=project.repository_url)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def get_project_by_repository_url(db: Session, repository_url: str):
    return db.query(models.Project).filter(models.Project.repository_url == repository_url).first()

# ==================== SCAN CRUD ====================

def create_scan(db: Session, scan: schemas.ScanCreate):
    """Create a new scan"""
    db_scan = models.Scan(**scan.model_dump())
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)
    return db_scan

def get_scan(db: Session, scan_id: int):
    """Get scan by ID"""
    return db.query(models.Scan).filter(models.Scan.id == scan_id).first()

def get_scans(db: Session, skip: int = 0, limit: int = 100, target_id: Optional[int] = None):
    """Get list of scans"""
    query = db.query(models.Scan)
    if target_id:
        query = query.filter(models.Scan.target_id == target_id)
    return query.order_by(desc(models.Scan.created_at)).offset(skip).limit(limit).all()

def update_scan_status(db: Session, scan_id: int, status: str):
    """Update scan status"""
    db_scan = get_scan(db, scan_id)
    if db_scan:
        db_scan.status = status
        if status == "running" and not db_scan.started_at:
            db_scan.started_at = datetime.datetime.utcnow()
        elif status in ["completed", "failed"]:
            db_scan.completed_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(db_scan)
    return db_scan

def update_scan_progress(db: Session, scan_id: int, progress: int, current_stage: str = None):
    """Update scan progress"""
    db_scan = get_scan(db, scan_id)
    if db_scan:
        db_scan.progress = progress
        if current_stage:
            db_scan.current_stage = current_stage
        db.commit()
        db.refresh(db_scan)
    return db_scan

def update_scan_error(db: Session, scan_id: int, error_message: str):
    """Update scan with error"""
    db_scan = get_scan(db, scan_id)
    if db_scan:
        db_scan.status = "failed"
        db_scan.error_message = error_message
        db_scan.completed_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(db_scan)
    return db_scan

# ==================== VULNERABILITY CRUD ====================

def create_vulnerability(db: Session, vulnerability: schemas.VulnerabilityCreate):
    """Create a vulnerability"""
    db_vulnerability = models.Vulnerability(**vulnerability.model_dump())
    db.add(db_vulnerability)
    db.commit()
    db.refresh(db_vulnerability)
    return db_vulnerability

def create_vulnerabilities_bulk(db: Session, vulnerabilities: List[schemas.VulnerabilityCreate]):
    """Create multiple vulnerabilities at once"""
    db_vulnerabilities = [models.Vulnerability(**v.model_dump()) for v in vulnerabilities]
    db.add_all(db_vulnerabilities)
    db.commit()
    return db_vulnerabilities

def get_vulnerabilities(db: Session, skip: int = 0, limit: int = 100, scan_id: Optional[int] = None):
    """Get vulnerabilities"""
    query = db.query(models.Vulnerability)
    if scan_id:
        query = query.filter(models.Vulnerability.scan_id == scan_id)
    return query.offset(skip).limit(limit).all()

def get_vulnerabilities_by_severity(db: Session, scan_id: int, severity: str):
    """Get vulnerabilities filtered by severity"""
    return db.query(models.Vulnerability).filter(
        models.Vulnerability.scan_id == scan_id,
        models.Vulnerability.severity == severity
    ).all()

# ==================== FINDING CRUD ====================

def create_finding(db: Session, finding: schemas.FindingCreate):
    """Create a finding"""
    db_finding = models.Finding(**finding.model_dump())
    db.add(db_finding)
    db.commit()
    db.refresh(db_finding)
    return db_finding

def create_findings_bulk(db: Session, findings: List[schemas.FindingCreate]):
    """Create multiple findings at once"""
    db_findings = [models.Finding(**f.model_dump()) for f in findings]
    db.add_all(db_findings)
    db.commit()
    return db_findings

def get_findings(db: Session, skip: int = 0, limit: int = 100, scan_id: Optional[int] = None):
    """Get findings"""
    query = db.query(models.Finding)
    if scan_id:
        query = query.filter(models.Finding.scan_id == scan_id)
    return query.offset(skip).limit(limit).all()

def get_findings_by_type(db: Session, scan_id: int, finding_type: str):
    """Get findings filtered by type"""
    return db.query(models.Finding).filter(
        models.Finding.scan_id == scan_id,
        models.Finding.finding_type == finding_type
    ).all()

# ==================== SCAN RESULTS ====================

def get_scan_results(db: Session, scan_id: int):
    """Get complete scan results including vulnerabilities and findings"""
    scan = get_scan(db, scan_id)
    if not scan:
        return None
    
    vulnerabilities = get_vulnerabilities(db, scan_id=scan_id, limit=10000)
    findings = get_findings(db, scan_id=scan_id, limit=10000)
    
    # Calculate summary statistics
    vuln_by_severity = {}
    for vuln in vulnerabilities:
        vuln_by_severity[vuln.severity] = vuln_by_severity.get(vuln.severity, 0) + 1
    
    findings_by_type = {}
    for finding in findings:
        findings_by_type[finding.finding_type] = findings_by_type.get(finding.finding_type, 0) + 1
    
    summary = {
        "total_vulnerabilities": len(vulnerabilities),
        "total_findings": len(findings),
        "vulnerabilities_by_severity": vuln_by_severity,
        "findings_by_type": findings_by_type,
        "scan_duration": None
    }
    
    if scan.started_at and scan.completed_at:
        duration = (scan.completed_at - scan.started_at).total_seconds()
        summary["scan_duration"] = f"{duration:.2f} seconds"
    
    return {
        "scan": scan,
        "vulnerabilities": vulnerabilities,
        "findings": findings,
        "summary": summary
    }

from sqlalchemy.orm import Session
from . import models, schemas

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

def get_scans(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Scan).offset(skip).limit(limit).all()

def create_scan(db: Session, scan: schemas.ScanCreate):
    db_scan = models.Scan(**scan.model_dump())
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)
    return db_scan

def get_vulnerabilities(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Vulnerability).offset(skip).limit(limit).all()

def get_project_by_repository_url(db: Session, repository_url: str):
    return db.query(models.Project).filter(models.Project.repository_url == repository_url).first()

def create_vulnerability(db: Session, vulnerability: schemas.VulnerabilityCreate):
    db_vulnerability = models.Vulnerability(**vulnerability.model_dump())
    db.add(db_vulnerability)
    db.commit()
    db.refresh(db_vulnerability)
    return db_vulnerability

def update_scan_status(db: Session, scan_id: int, status: str):
    db_scan = db.query(models.Scan).filter(models.Scan.id == scan_id).first()
    if db_scan:
        db_scan.status = status
        db.commit()
        db.refresh(db_scan)
    return db_scan

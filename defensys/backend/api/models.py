from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    repository_url = Column(String, unique=True, index=True)
    scans = relationship("Scan", back_populates="project")

class Scan(Base):
    __tablename__ = "scans"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    scan_type = Column(String, nullable=True)  # Added scan_type field
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    project = relationship("Project", back_populates="scans")
    vulnerabilities = relationship("Vulnerability", back_populates="scan")

class Vulnerability(Base):
    __tablename__ = "vulnerabilities"
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"))
    type = Column(String) # e.g., SAST, Dependency, Secret
    severity = Column(String)
    description = Column(String)
    file_path = Column(String, nullable=True)
    line_number = Column(Integer, nullable=True)
    scan = relationship("Scan", back_populates="vulnerabilities")

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class Target(Base):
    """Target hosts/domains for scanning"""
    __tablename__ = "targets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)  # User-friendly name
    target_type = Column(String)  # 'domain', 'ip', 'cidr', 'url'
    value = Column(String, index=True)  # The actual target (e.g., "192.168.1.1", "example.com")
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_scanned = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Enumeration results stored as JSON
    enumeration_data = Column(JSON, nullable=True)  # Stores discovered hosts, ports, services
    
    # Relationships
    scans = relationship("Scan", back_populates="target")

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    repository_url = Column(String, unique=True, index=True)
    scans = relationship("Scan", back_populates="project")

class Scan(Base):
    __tablename__ = "scans"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    target_id = Column(Integer, ForeignKey("targets.id"), nullable=True)
    scan_type = Column(String, nullable=True)  # e.g., "network", "web", "full"
    scan_tools = Column(JSON, nullable=True)  # List of tools used: ["nmap", "nuclei", etc]
    status = Column(String, default="pending")  # pending, running, completed, failed
    progress = Column(Integer, default=0)  # 0-100
    current_stage = Column(String, nullable=True)  # e.g., "Running Nmap", "Analyzing results"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="scans")
    target = relationship("Target", back_populates="scans")
    vulnerabilities = relationship("Vulnerability", back_populates="scan", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="scan", cascade="all, delete-orphan")

class Vulnerability(Base):
    __tablename__ = "vulnerabilities"
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"))
    
    # Vulnerability details
    scanner_name = Column(String)  # "Nmap", "Nuclei", "ZAP", etc.
    scanner_type = Column(String)  # "network", "web", "code", etc.
    severity = Column(String)  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    title = Column(String)
    description = Column(Text)
    
    # Location information
    target_host = Column(String, nullable=True)
    target_port = Column(Integer, nullable=True)
    url = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    line_number = Column(Integer, nullable=True)
    
    # CVE and references
    cve_ids = Column(JSON, nullable=True)  # List of CVE IDs
    cvss_score = Column(String, nullable=True)
    references = Column(JSON, nullable=True)  # List of reference URLs
    
    # Additional metadata
    scan_metadata = Column(JSON, nullable=True)  # Store any scanner-specific data
    remediation = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    scan = relationship("Scan", back_populates="vulnerabilities")

class Finding(Base):
    """General findings from scans (ports, services, hosts, etc.)"""
    __tablename__ = "findings"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"))
    
    finding_type = Column(String)  # "open_port", "service", "host", "os_detection"
    scanner_name = Column(String)
    
    # Finding details
    title = Column(String)
    description = Column(Text)
    severity = Column(String, default="INFO")
    
    # Network details
    host = Column(String, nullable=True)
    port = Column(Integer, nullable=True)
    protocol = Column(String, nullable=True)
    service = Column(String, nullable=True)
    
    # Additional data
    data = Column(JSON, nullable=True)  # Flexible storage for any finding data
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    scan = relationship("Scan", back_populates="findings")

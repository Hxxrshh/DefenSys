"""
DefenSys Phase 1 API Routes
Complete API endpoints for target management, scanning, and results
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import asyncio

from . import crud, schemas, models
from .database import get_db
from .scan_orchestrator import ScanOrchestrator

# Create router
router = APIRouter()

# ==================== TARGET ENDPOINTS ====================

@router.post("/targets", response_model=schemas.Target, tags=["Targets"])
def create_target(target: schemas.TargetCreate, db: Session = Depends(get_db)):
    """
    Create a new scan target
    
    Example:
    ```json
    {
        "name": "Production Server",
        "target_type": "ip",
        "value": "192.168.1.100",
        "description": "Main production server"
    }
    ```
    """
    # Check if target already exists
    existing = crud.get_target_by_value(db, target.value)
    if existing:
        raise HTTPException(status_code=400, detail="Target already exists")
    
    return crud.create_target(db, target)

@router.get("/targets", response_model=List[schemas.Target], tags=["Targets"])
def list_targets(
    skip: int = 0, 
    limit: int = 100, 
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get list of all targets"""
    return crud.get_targets(db, skip=skip, limit=limit, active_only=active_only)

@router.get("/targets/{target_id}", response_model=schemas.Target, tags=["Targets"])
def get_target(target_id: int, db: Session = Depends(get_db)):
    """Get specific target by ID"""
    target = crud.get_target(db, target_id)
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    return target

@router.put("/targets/{target_id}", response_model=schemas.Target, tags=["Targets"])
def update_target(target_id: int, updates: dict, db: Session = Depends(get_db)):
    """Update target information"""
    target = crud.update_target(db, target_id, updates)
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    return target

@router.delete("/targets/{target_id}", tags=["Targets"])
def delete_target(target_id: int, db: Session = Depends(get_db)):
    """Soft delete a target"""
    target = crud.delete_target(db, target_id)
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    return {"message": "Target deleted successfully"}

# ==================== SCAN ENDPOINTS ====================

@router.post("/scans/start", response_model=schemas.Scan, tags=["Scans"])
async def start_scan(scan_request: schemas.ScanStart, db: Session = Depends(get_db)):
    """
    Start a new security scan
    
    Example requests:
    
    **Quick network scan:**
    ```json
    {
        "target_value": "192.168.1.100",
        "target_type": "ip",
        "scan_type": "quick",
        "target_name": "Web Server"
    }
    ```
    
    **Full web application scan:**
    ```json
    {
        "target_value": "https://example.com",
        "target_type": "url",
        "scan_type": "full",
        "scan_tools": ["nuclei", "nikto", "zap"]
    }
    ```
    
    **Network range scan:**
    ```json
    {
        "target_value": "192.168.1.0/24",
        "target_type": "cidr",
        "scan_type": "network"
    }
    ```
    
    Scan types: quick, default, full, network, web
    Target types: ip, domain, url, cidr
    Available tools: nmap, nuclei, nikto, zap
    """
    orchestrator = ScanOrchestrator(db)
    scan = await orchestrator.start_scan(scan_request)
    return scan

@router.get("/scans", response_model=List[schemas.Scan], tags=["Scans"])
def list_scans(
    skip: int = 0,
    limit: int = 100,
    target_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get list of all scans, optionally filtered by target"""
    return crud.get_scans(db, skip=skip, limit=limit, target_id=target_id)

@router.get("/scans/{scan_id}", response_model=schemas.Scan, tags=["Scans"])
def get_scan(scan_id: int, db: Session = Depends(get_db)):
    """Get specific scan by ID"""
    scan = crud.get_scan(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan

@router.get("/scans/{scan_id}/progress", response_model=schemas.ScanProgress, tags=["Scans"])
def get_scan_progress(scan_id: int, db: Session = Depends(get_db)):
    """Get real-time scan progress"""
    scan = crud.get_scan(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Count vulnerabilities and findings
    vulnerabilities = crud.get_vulnerabilities(db, scan_id=scan_id, limit=10000)
    findings = crud.get_findings(db, scan_id=scan_id, limit=10000)
    
    return schemas.ScanProgress(
        scan_id=scan.id,
        status=scan.status,
        progress=scan.progress,
        current_stage=scan.current_stage or "Initializing",
        findings_count=len(findings),
        vulnerabilities_count=len(vulnerabilities)
    )

@router.get("/scans/{scan_id}/results", response_model=schemas.ScanResults, tags=["Scans"])
def get_scan_results(scan_id: int, db: Session = Depends(get_db)):
    """
    Get complete scan results including all vulnerabilities and findings
    
    Returns:
    - Scan metadata
    - All vulnerabilities found
    - All findings (ports, services, hosts)
    - Summary statistics
    """
    results = crud.get_scan_results(db, scan_id)
    if not results:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return schemas.ScanResults(**results)

# ==================== VULNERABILITY ENDPOINTS ====================

@router.get("/vulnerabilities", response_model=List[schemas.Vulnerability], tags=["Vulnerabilities"])
def list_vulnerabilities(
    skip: int = 0,
    limit: int = 100,
    scan_id: Optional[int] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of vulnerabilities, optionally filtered"""
    if severity:
        if not scan_id:
            raise HTTPException(status_code=400, detail="scan_id required when filtering by severity")
        return crud.get_vulnerabilities_by_severity(db, scan_id, severity)
    
    return crud.get_vulnerabilities(db, skip=skip, limit=limit, scan_id=scan_id)

@router.get("/scans/{scan_id}/vulnerabilities", response_model=List[schemas.Vulnerability], tags=["Vulnerabilities"])
def get_scan_vulnerabilities(
    scan_id: int,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all vulnerabilities for a specific scan"""
    scan = crud.get_scan(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    if severity:
        return crud.get_vulnerabilities_by_severity(db, scan_id, severity)
    
    return crud.get_vulnerabilities(db, scan_id=scan_id, limit=10000)

# ==================== FINDINGS ENDPOINTS ====================

@router.get("/findings", response_model=List[schemas.Finding], tags=["Findings"])
def list_findings(
    skip: int = 0,
    limit: int = 100,
    scan_id: Optional[int] = None,
    finding_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of findings, optionally filtered"""
    if finding_type:
        if not scan_id:
            raise HTTPException(status_code=400, detail="scan_id required when filtering by type")
        return crud.get_findings_by_type(db, scan_id, finding_type)
    
    return crud.get_findings(db, skip=skip, limit=limit, scan_id=scan_id)

@router.get("/scans/{scan_id}/findings", response_model=List[schemas.Finding], tags=["Findings"])
def get_scan_findings(
    scan_id: int,
    finding_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all findings for a specific scan"""
    scan = crud.get_scan(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    if finding_type:
        return crud.get_findings_by_type(db, scan_id, finding_type)
    
    return crud.get_findings(db, scan_id=scan_id, limit=10000)

# ==================== SCANNER INFO ENDPOINTS ====================

@router.get("/scanners/available", tags=["Scanners"])
def get_available_scanners():
    """Get list of available scanners and their status"""
    try:
        from scanners.nmap import NmapScanner
        from scanners.dast import ZapScanner, NucleiScanner, NiktoScanner
        
        scanners = {
            "nmap": NmapScanner(),
            "zap": ZapScanner(),
            "nuclei": NucleiScanner(),
            "nikto": NiktoScanner()
        }
        
        scanner_status = []
        for name, scanner in scanners.items():
            scanner_status.append({
                "name": scanner.name,
                "type": scanner.scanner_type if hasattr(scanner, 'scanner_type') else 'unknown',
                "available": scanner.is_available(),
                "description": _get_scanner_description(name)
            })
        
        return {
            "scanners": scanner_status,
            "total_scanners": len(scanners),
            "available_scanners": sum(1 for s in scanner_status if s["available"])
        }
    except Exception as e:
        # Return a fallback response if scanner import fails
        print(f"Error loading scanners: {e}")
        return {
            "scanners": [
                {"name": "Nmap", "type": "network", "available": False, "description": "Network mapper for port scanning"},
                {"name": "Nuclei", "type": "vulnerability", "available": False, "description": "Vulnerability scanner"},
                {"name": "Nikto", "type": "web", "available": False, "description": "Web server scanner"},
                {"name": "ZAP", "type": "web", "available": False, "description": "Web application security scanner"}
            ],
            "total_scanners": 4,
            "available_scanners": 0
        }

def _get_scanner_description(name: str) -> str:
    """Get description for scanner"""
    descriptions = {
        "nmap": "Network mapper for port scanning and service detection",
        "zap": "OWASP ZAP web application security scanner",
        "nuclei": "Template-based vulnerability scanner",
        "nikto": "Web server vulnerability scanner"
    }
    return descriptions.get(name, "Security scanner")

# ==================== ENUMERATION ENDPOINTS ====================

@router.post("/enumerate/discover", tags=["Enumeration"])
async def discover_hosts(network: str, db: Session = Depends(get_db)):
    """
    Discover active hosts in a network range
    
    Example:
    ```json
    {
        "network": "192.168.1.0/24"
    }
    ```
    """
    from ..scanners.nmap import NmapScanner
    
    scanner = NmapScanner()
    if not scanner.is_available():
        raise HTTPException(status_code=503, detail="Nmap scanner not available")
    
    # Run quick ping sweep
    results = await asyncio.to_thread(scanner.quick_ping_sweep, network)
    
    # Extract active hosts
    active_hosts = []
    for result in results:
        if result.get('state') == 'up':
            active_hosts.append({
                "ip": result.get('ip_address'),
                "hostname": result.get('hostname'),
                "state": result.get('state')
            })
    
    return {
        "network": network,
        "active_hosts": active_hosts,
        "total_found": len(active_hosts)
    }

@router.post("/enumerate/ports", tags=["Enumeration"])
async def enumerate_ports(target: str, ports: str = "1-1000", db: Session = Depends(get_db)):
    """
    Enumerate open ports on a target
    
    Example:
    ```
    POST /enumerate/ports?target=192.168.1.100&ports=1-1000
    ```
    """
    from ..scanners.nmap import NmapScanner
    
    scanner = NmapScanner()
    if not scanner.is_available():
        raise HTTPException(status_code=503, detail="Nmap scanner not available")
    
    # Run port scan
    results = await asyncio.to_thread(scanner.port_scan, target, ports)
    
    # Extract open ports
    open_ports = []
    for result in results:
        if result.get('port') and result.get('state') == 'open':
            open_ports.append({
                "port": result.get('port'),
                "protocol": result.get('protocol'),
                "service": result.get('service'),
                "version": result.get('service_version')
            })
    
    return {
        "target": target,
        "ports_scanned": ports,
        "open_ports": open_ports,
        "total_open": len(open_ports)
    }

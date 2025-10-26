"""
DefenSys Phase 1 Scan Orchestrator
Manages complete scanning workflow with multiple tools and real-time progress
"""

import asyncio
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
import datetime

from . import crud, schemas, models
from scanners.nmap import NmapScanner
from scanners.dast import ZapScanner, NucleiScanner, NiktoScanner
from .real_time_monitoring import real_time_monitor

class ScanOrchestrator:
    """Orchestrates multi-tool scanning with progress tracking"""
    
    def __init__(self, db: Session):
        self.db = db
        self.scanners = {
            "nmap": NmapScanner(),
            "zap": ZapScanner(),
            "nuclei": NucleiScanner(),
            "nikto": NiktoScanner()
        }
    
    async def start_scan(self, scan_request: schemas.ScanStart) -> models.Scan:
        """
        Start a comprehensive scan
        
        Args:
            scan_request: Scan configuration
            
        Returns:
            Created scan object
        """
        # Create or get target
        target = await self._get_or_create_target(
            scan_request.target_value,
            scan_request.target_type,
            scan_request.target_name
        )
        
        # Determine which tools to use
        tools_to_use = self._determine_scan_tools(
            scan_request.scan_type,
            scan_request.target_type,
            scan_request.scan_tools
        )
        
        # Create scan record
        scan = crud.create_scan(self.db, schemas.ScanCreate(
            target_id=target.id,
            scan_type=scan_request.scan_type,
            scan_tools=tools_to_use,
            status="pending",
            progress=0
        ))
        
        # Start scanning in background
        asyncio.create_task(self._execute_scan(scan.id, target, tools_to_use))
        
        return scan
    
    async def _get_or_create_target(self, value: str, target_type: str, 
                                    name: Optional[str] = None) -> models.Target:
        """Get existing target or create new one"""
        existing_target = crud.get_target_by_value(self.db, value)
        
        if existing_target:
            return existing_target
        
        # Create new target
        target_name = name or f"{target_type.upper()}: {value}"
        target = crud.create_target(self.db, schemas.TargetCreate(
            name=target_name,
            target_type=target_type,
            value=value,
            description=f"Auto-created target for {target_type} scan"
        ))
        
        return target
    
    def _determine_scan_tools(self, scan_type: str, target_type: str, 
                             requested_tools: Optional[List[str]]) -> List[str]:
        """Determine which tools to use based on scan type and target"""
        if requested_tools:
            # Use explicitly requested tools
            return [tool for tool in requested_tools if tool in self.scanners]
        
        # Auto-select tools based on scan type and target type
        tool_map = {
            "quick": {
                "ip": ["nmap"],
                "domain": ["nmap", "nuclei"],
                "url": ["nuclei"],
                "cidr": ["nmap"]
            },
            "default": {
                "ip": ["nmap", "nuclei"],
                "domain": ["nmap", "nuclei", "nikto"],
                "url": ["nuclei", "nikto"],
                "cidr": ["nmap"]
            },
            "full": {
                "ip": ["nmap", "nuclei", "nikto", "zap"],
                "domain": ["nmap", "nuclei", "nikto", "zap"],
                "url": ["nuclei", "nikto", "zap"],
                "cidr": ["nmap"]
            },
            "network": {
                "ip": ["nmap"],
                "domain": ["nmap"],
                "url": [],
                "cidr": ["nmap"]
            },
            "web": {
                "ip": ["nuclei", "nikto"],
                "domain": ["nuclei", "nikto", "zap"],
                "url": ["nuclei", "nikto", "zap"],
                "cidr": []
            }
        }
        
        return tool_map.get(scan_type, {}).get(target_type, ["nmap"])
    
    async def _execute_scan(self, scan_id: int, target: models.Target, tools: List[str]):
        """Execute the actual scan with progress tracking"""
        try:
            # Update to running
            crud.update_scan_status(self.db, scan_id, "running")
            self._broadcast_progress(scan_id, 0, "Starting scan")
            
            all_vulnerabilities = []
            all_findings = []
            total_tools = len(tools)
            
            # Execute each tool
            for idx, tool_name in enumerate(tools):
                progress = int((idx / total_tools) * 90)  # Reserve 10% for processing
                stage = f"Running {tool_name.upper()}"
                
                crud.update_scan_progress(self.db, scan_id, progress, stage)
                self._broadcast_progress(scan_id, progress, stage)
                
                try:
                    scanner = self.scanners.get(tool_name)
                    if not scanner:
                        continue
                    
                    # Run scanner
                    results = await self._run_scanner(scanner, target, tool_name)
                    
                    # Process results
                    vulns, findings = self._process_scanner_results(scan_id, results)
                    all_vulnerabilities.extend(vulns)
                    all_findings.extend(findings)
                    
                except Exception as e:
                    print(f"Error running {tool_name}: {e}")
                    # Continue with other tools
            
            # Save results to database
            stage = "Saving results"
            crud.update_scan_progress(self.db, scan_id, 95, stage)
            self._broadcast_progress(scan_id, 95, stage)
            
            if all_vulnerabilities:
                crud.create_vulnerabilities_bulk(self.db, all_vulnerabilities)
            
            if all_findings:
                crud.create_findings_bulk(self.db, all_findings)
            
            # Mark as completed
            crud.update_scan_status(self.db, scan_id, "completed")
            crud.update_scan_progress(self.db, scan_id, 100, "Completed")
            self._broadcast_progress(scan_id, 100, "Completed", 
                                    len(all_vulnerabilities), len(all_findings))
            
            # Update target last_scanned
            crud.update_target(self.db, target.id, {
                "last_scanned": datetime.datetime.utcnow()
            })
            
        except Exception as e:
            error_msg = f"Scan failed: {str(e)}"
            print(f"❌ {error_msg}")
            crud.update_scan_error(self.db, scan_id, error_msg)
            self._broadcast_progress(scan_id, 0, f"Failed: {error_msg}")
    
    async def _run_scanner(self, scanner, target: models.Target, tool_name: str) -> List[Dict]:
        """Run a specific scanner tool"""
        if not scanner.is_available():
            print(f"⚠️ {tool_name} is not available, skipping")
            return []
        
        try:
            # Network scanners (Nmap)
            if tool_name == "nmap":
                if target.target_type in ["ip", "cidr", "domain"]:
                    return await asyncio.to_thread(scanner.scan, target.value)
                return []
            
            # Web scanners (need URL)
            elif tool_name in ["nuclei", "nikto", "zap"]:
                target_url = self._get_target_url(target)
                if target_url:
                    return await asyncio.to_thread(scanner.scan, target_url)
                return []
            
            return []
            
        except Exception as e:
            print(f"Scanner {tool_name} error: {e}")
            return []
    
    def _get_target_url(self, target: models.Target) -> Optional[str]:
        """Convert target to URL format for web scanners"""
        if target.target_type == "url":
            return target.value
        elif target.target_type == "domain":
            return f"https://{target.value}"
        elif target.target_type == "ip":
            return f"http://{target.value}"
        return None
    
    def _process_scanner_results(self, scan_id: int, results: List[Dict]) -> tuple:
        """Process scanner results into vulnerabilities and findings"""
        vulnerabilities = []
        findings = []
        
        for result in results:
            # Determine if it's a vulnerability or just a finding
            severity = result.get('severity', 'INFO')
            
            if severity in ['CRITICAL', 'HIGH', 'MEDIUM'] and 'vulnerability' in str(result).lower():
                # It's a vulnerability
                vuln = schemas.VulnerabilityCreate(
                    scan_id=scan_id,
                    scanner_name=result.get('scanner_name', 'Unknown'),
                    scanner_type=result.get('scanner_type', 'unknown'),
                    severity=severity,
                    title=result.get('title', 'Unknown Vulnerability'),
                    description=result.get('description', ''),
                    target_host=result.get('target', result.get('ip_address')),
                    target_port=result.get('port'),
                    url=result.get('url'),
                    file_path=result.get('file_path'),
                    line_number=result.get('line_number'),
                    cve_ids=result.get('cve_ids'),
                    cvss_score=result.get('cvss_score'),
                    references=result.get('references', result.get('reference')),
                    metadata=result.get('metadata', {}),
                    remediation=result.get('remediation')
                )
                vulnerabilities.append(vuln)
            else:
                # It's a general finding (port, service, etc.)
                finding_type = self._determine_finding_type(result)
                
                finding = schemas.FindingCreate(
                    scan_id=scan_id,
                    finding_type=finding_type,
                    scanner_name=result.get('scanner_name', 'Unknown'),
                    title=result.get('title', 'Finding'),
                    description=result.get('description', ''),
                    severity=severity,
                    host=result.get('target', result.get('ip_address')),
                    port=result.get('port'),
                    protocol=result.get('protocol'),
                    service=result.get('service'),
                    data=result
                )
                findings.append(finding)
        
        return vulnerabilities, findings
    
    def _determine_finding_type(self, result: Dict) -> str:
        """Determine the type of finding"""
        if 'port' in result and result.get('state') == 'open':
            return 'open_port'
        elif 'service' in result:
            return 'service'
        elif 'os_name' in result:
            return 'os_detection'
        elif 'hostname' in result:
            return 'host'
        else:
            return 'info'
    
    def _broadcast_progress(self, scan_id: int, progress: int, stage: str, 
                           vuln_count: int = 0, findings_count: int = 0):
        """Broadcast progress update via WebSocket"""
        try:
            progress_data = {
                "scan_id": scan_id,
                "status": "running" if progress < 100 else "completed",
                "progress": progress,
                "current_stage": stage,
                "findings_count": findings_count,
                "vulnerabilities_count": vuln_count
            }
            
            # Publish to RabbitMQ for WebSocket broadcast
            if real_time_monitor:
                # Convert progress to 0-1 range and provide required parameters
                real_time_monitor.publish_scan_progress(
                    scan_id=scan_id,
                    project_id=1,  # Default project ID
                    progress=progress / 100.0,  # Convert to 0-1 range
                    current_scanner=stage,
                    vulnerabilities_found=vuln_count
                )
                
        except Exception as e:
            print(f"Error broadcasting progress: {e}")

"""
DefenSys Nmap Network Scanner
Complete network enumeration and port scanning with structured output
"""

import subprocess
import json
import tempfile
import os
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from .base import Scanner

class NmapScanner(Scanner):
    """Nmap Network Scanner with structured output parsing"""
    
    def __init__(self):
        super().__init__()
        self.name = "Nmap"
        self.scanner_type = "network"
        self.tool_command = "nmap"
    
    def scan(self, target: str, scan_type: str = "default", ports: Optional[str] = None, 
             service_detection: bool = True, os_detection: bool = False) -> List[dict]:
        """
        Perform Nmap network scan
        
        Args:
            target: IP address, hostname, or CIDR range
            scan_type: Type of scan - 'quick', 'default', 'intensive', 'stealth'
            ports: Port specification (e.g., "1-1000", "22,80,443")
            service_detection: Enable service version detection
            os_detection: Enable OS detection (requires root)
            
        Returns:
            List of findings with host information and vulnerabilities
        """
        if not self.is_available():
            return [{
                "scanner_name": self.name,
                "error": "Nmap is not installed or not available in PATH"
            }]
        
        findings = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "nmap_scan.xml")
            
            try:
                cmd = self._build_command(target, scan_type, ports, 
                                         service_detection, os_detection, output_file)
                
                print(f"🌐 Running Nmap scan on {target}")
                print(f"   Command: {' '.join(cmd)}")
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=600  # 10 minute timeout
                )
                
                if result.returncode == 0 and os.path.exists(output_file):
                    findings = self._parse_xml_output(output_file, target)
                else:
                    error_msg = result.stderr or "Nmap scan failed"
                    print(f"❌ Nmap error: {error_msg}")
                    findings.append({
                        "scanner_name": self.name,
                        "scanner_type": self.scanner_type,
                        "target": target,
                        "error": error_msg,
                        "severity": "INFO"
                    })
                    
            except subprocess.TimeoutExpired:
                print(f"⏰ Nmap scan timed out after 10 minutes")
                findings.append({
                    "scanner_name": self.name,
                    "scanner_type": self.scanner_type,
                    "target": target,
                    "error": "Scan timed out",
                    "severity": "INFO"
                })
            except Exception as e:
                print(f"❌ Nmap scan exception: {e}")
                findings.append({
                    "scanner_name": self.name,
                    "scanner_type": self.scanner_type,
                    "target": target,
                    "error": str(e),
                    "severity": "INFO"
                })
        
        return findings
    
    def _build_command(self, target: str, scan_type: str, ports: Optional[str],
                      service_detection: bool, os_detection: bool, output_file: str) -> List[str]:
        """Build Nmap command based on parameters"""
        cmd = [self.tool_command]
        
        # Scan type configurations
        scan_profiles = {
            "quick": ["-T4", "-F"],  # Fast scan, top 100 ports
            "default": ["-T3"],  # Default timing
            "intensive": ["-T4", "-A", "-v"],  # Aggressive, all features
            "stealth": ["-sS", "-T2"],  # SYN stealth scan, slower
            "ping_sweep": ["-sn"],  # Ping scan only, no port scan
            "full": ["-p-", "-T4"]  # All 65535 ports
        }
        
        # Add scan profile options
        cmd.extend(scan_profiles.get(scan_type, scan_profiles["default"]))
        
        # Port specification
        if ports and scan_type not in ["ping_sweep"]:
            cmd.extend(["-p", ports])
        
        # Service version detection
        if service_detection and scan_type not in ["ping_sweep"]:
            cmd.append("-sV")
        
        # OS detection
        if os_detection:
            cmd.append("-O")
        
        # Output format
        cmd.extend(["-oX", output_file])
        
        # Script scanning for vulnerability detection
        if scan_type in ["intensive", "full"]:
            cmd.extend(["--script", "vuln,safe,discovery"])
        
        # Target
        cmd.append(target)
        
        return cmd
    
    def _parse_xml_output(self, xml_file: str, target: str) -> List[dict]:
        """Parse Nmap XML output into structured findings"""
        findings = []
        
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Parse each host
            for host in root.findall('host'):
                host_findings = self._parse_host(host, target)
                findings.extend(host_findings)
                
        except Exception as e:
            print(f"❌ Error parsing Nmap XML: {e}")
            findings.append({
                "scanner_name": self.name,
                "scanner_type": self.scanner_type,
                "target": target,
                "error": f"XML parsing error: {str(e)}",
                "severity": "INFO"
            })
        
        return findings
    
    def _parse_host(self, host_elem, target: str) -> List[dict]:
        """Parse individual host information"""
        findings = []
        
        # Get host address
        address_elem = host_elem.find(".//address[@addrtype='ipv4']")
        if address_elem is None:
            address_elem = host_elem.find(".//address[@addrtype='ipv6']")
        
        ip_address = address_elem.get('addr') if address_elem is not None else target
        
        # Get hostname
        hostname_elem = host_elem.find(".//hostname")
        hostname = hostname_elem.get('name') if hostname_elem is not None else None
        
        # Host status
        status_elem = host_elem.find('status')
        host_state = status_elem.get('state') if status_elem is not None else 'unknown'
        
        # Base host info
        host_info = {
            "scanner_name": self.name,
            "scanner_type": self.scanner_type,
            "target": target,
            "ip_address": ip_address,
            "hostname": hostname,
            "state": host_state,
            "severity": "INFO",
            "title": f"Host Discovery: {ip_address}",
            "description": f"Host {ip_address} is {host_state}"
        }
        
        # Add hostname if available
        if hostname:
            host_info["description"] += f" (hostname: {hostname})"
        
        findings.append(host_info)
        
        # Parse open ports
        ports_elem = host_elem.find('ports')
        if ports_elem is not None:
            for port_elem in ports_elem.findall('port'):
                port_finding = self._parse_port(port_elem, ip_address, hostname)
                if port_finding:
                    findings.append(port_finding)
        
        # Parse OS detection
        os_elem = host_elem.find('os')
        if os_elem is not None:
            os_finding = self._parse_os(os_elem, ip_address, hostname)
            if os_finding:
                findings.append(os_finding)
        
        # Parse script results (vulnerabilities)
        for script_elem in host_elem.findall(".//script"):
            script_finding = self._parse_script(script_elem, ip_address, hostname)
            if script_finding:
                findings.append(script_finding)
        
        return findings
    
    def _parse_port(self, port_elem, ip_address: str, hostname: Optional[str]) -> Optional[dict]:
        """Parse port information"""
        port_id = port_elem.get('portid')
        protocol = port_elem.get('protocol', 'tcp')
        
        state_elem = port_elem.find('state')
        port_state = state_elem.get('state') if state_elem is not None else 'unknown'
        
        if port_state != 'open':
            return None  # Only report open ports
        
        service_elem = port_elem.find('service')
        service_name = service_elem.get('name', 'unknown') if service_elem is not None else 'unknown'
        service_product = service_elem.get('product', '') if service_elem is not None else ''
        service_version = service_elem.get('version', '') if service_elem is not None else ''
        
        # Determine severity based on well-known vulnerable ports
        severity = self._assess_port_severity(int(port_id), service_name)
        
        service_info = f"{service_name}"
        if service_product:
            service_info += f" ({service_product}"
            if service_version:
                service_info += f" {service_version}"
            service_info += ")"
        
        finding = {
            "scanner_name": self.name,
            "scanner_type": self.scanner_type,
            "target": ip_address,
            "hostname": hostname,
            "severity": severity,
            "title": f"Open Port: {port_id}/{protocol}",
            "description": f"Port {port_id}/{protocol} is open - Service: {service_info}",
            "port": int(port_id),
            "protocol": protocol,
            "service": service_name,
            "service_product": service_product,
            "service_version": service_version,
            "state": port_state
        }
        
        return finding
    
    def _parse_os(self, os_elem, ip_address: str, hostname: Optional[str]) -> Optional[dict]:
        """Parse OS detection results"""
        osmatch = os_elem.find('osmatch')
        if osmatch is None:
            return None
        
        os_name = osmatch.get('name', 'Unknown OS')
        accuracy = osmatch.get('accuracy', '0')
        
        finding = {
            "scanner_name": self.name,
            "scanner_type": self.scanner_type,
            "target": ip_address,
            "hostname": hostname,
            "severity": "INFO",
            "title": "OS Detection",
            "description": f"Detected OS: {os_name} (Accuracy: {accuracy}%)",
            "os_name": os_name,
            "os_accuracy": accuracy
        }
        
        return finding
    
    def _parse_script(self, script_elem, ip_address: str, hostname: Optional[str]) -> Optional[dict]:
        """Parse NSE script results for vulnerabilities"""
        script_id = script_elem.get('id', 'unknown')
        script_output = script_elem.get('output', '')
        
        # Only report vulnerability scripts
        if 'vuln' not in script_id and 'CVE' not in script_output:
            return None
        
        # Determine severity from script output
        severity = "MEDIUM"
        if "CRITICAL" in script_output or "VULNERABLE" in script_output.upper():
            severity = "HIGH"
        elif "CVE" in script_output:
            severity = "MEDIUM"
        elif "low" in script_output.lower():
            severity = "LOW"
        
        finding = {
            "scanner_name": self.name,
            "scanner_type": self.scanner_type,
            "target": ip_address,
            "hostname": hostname,
            "severity": severity,
            "title": f"NSE Script: {script_id}",
            "description": script_output.strip(),
            "script_id": script_id
        }
        
        # Extract CVE IDs if present
        import re
        cve_pattern = r'CVE-\d{4}-\d+' 
        cves = re.findall(cve_pattern, script_output)
        if cves:
            finding["cve_ids"] = cves
        
        return finding
    
    def _assess_port_severity(self, port: int, service: str) -> str:
        """Assess severity based on port and service"""
        # High-risk ports
        high_risk_ports = [
            23,    # Telnet (unencrypted)
            445,   # SMB (often exploited)
            3389,  # RDP (brute-force target)
            5900,  # VNC (weak auth)
            1433,  # MSSQL
            3306,  # MySQL
            5432,  # PostgreSQL
        ]
        
        # Medium-risk ports
        medium_risk_ports = [
            21,    # FTP
            25,    # SMTP
            110,   # POP3
            143,   # IMAP
            139,   # NetBIOS
            161,   # SNMP
            8080,  # HTTP alternate
        ]
        
        # Known vulnerable services
        vulnerable_services = ['telnet', 'ftp', 'smb', 'rdp', 'vnc']
        
        if port in high_risk_ports or service in vulnerable_services:
            return "HIGH"
        elif port in medium_risk_ports:
            return "MEDIUM"
        else:
            return "LOW"
    
    def is_available(self) -> bool:
        """Check if Nmap is installed"""
        try:
            result = subprocess.run(
                [self.tool_command, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def quick_ping_sweep(self, network: str) -> List[dict]:
        """Quick ping sweep to discover active hosts"""
        return self.scan(network, scan_type="ping_sweep")
    
    def port_scan(self, target: str, ports: str = "1-1000") -> List[dict]:
        """Scan specific ports on target"""
        return self.scan(target, scan_type="default", ports=ports)
    
    def vulnerability_scan(self, target: str) -> List[dict]:
        """Deep vulnerability scan with NSE scripts"""
        return self.scan(target, scan_type="intensive")

"""
DefenSys DAST Scanner Implementation
Dynamic Application Security Testing integration
"""

import subprocess
import json
import tempfile
import os
import time
from typing import List, Dict, Optional
from urllib.parse import urlparse

class DastScanner:
    """Base class for Dynamic Application Security Testing tools"""
    
    def __init__(self):
        self.scanner_type = "dast"
        self.name = "DAST Scanner"
    
    def scan(self, target_url: str, **kwargs) -> List[Dict]:
        """
        Scan a target URL for vulnerabilities
        
        Args:
            target_url: The URL to scan
            **kwargs: Additional scanner-specific options
            
        Returns:
            List of vulnerability findings
        """
        raise NotImplementedError
    
    def is_available(self) -> bool:
        """Check if the scanner tool is installed and available"""
        raise NotImplementedError

class ZapScanner(DastScanner):
    """OWASP ZAP Dynamic Scanner"""
    
    def __init__(self):
        super().__init__()
        self.name = "OWASP ZAP"
        self.tool_command = "zap.sh"  # or "zap.cmd" on Windows
    
    def is_available(self) -> bool:
        """Check if ZAP is installed"""
        try:
            result = subprocess.run([self.tool_command, "-version"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def scan(self, target_url: str, scan_timeout: int = 300, **kwargs) -> List[Dict]:
        """
        Run OWASP ZAP scan
        
        Args:
            target_url: Target URL to scan
            scan_timeout: Maximum scan time in seconds
            
        Returns:
            List of vulnerability findings
        """
        findings = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            report_file = os.path.join(temp_dir, "zap_report.json")
            
            try:
                # ZAP quick scan command
                cmd = [
                    self.tool_command, "-cmd",
                    "-quickurl", target_url,
                    "-quickout", report_file
                ]
                
                print(f"🕷️ Running ZAP scan on {target_url}")
                result = subprocess.run(cmd, capture_output=True, text=True, 
                                      timeout=scan_timeout)
                
                if result.returncode == 0 and os.path.exists(report_file):
                    findings = self._parse_zap_report(report_file, target_url)
                else:
                    print(f"ZAP scan failed: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                print(f"ZAP scan timed out after {scan_timeout} seconds")
            except Exception as e:
                print(f"ZAP scan error: {e}")
        
        return findings
    
    def _parse_zap_report(self, report_file: str, target_url: str) -> List[Dict]:
        """Parse ZAP JSON report"""
        findings = []
        
        try:
            with open(report_file, 'r') as f:
                data = json.load(f)
            
            # Parse ZAP alerts
            for alert in data.get('site', [{}])[0].get('alerts', []):
                finding = {
                    "scanner_type": "dast",
                    "scanner_name": "OWASP ZAP",
                    "severity": self._map_zap_severity(alert.get('riskdesc', 'Low')),
                    "title": alert.get('name', 'Unknown Vulnerability'),
                    "description": alert.get('desc', 'No description available'),
                    "url": target_url,
                    "method": alert.get('method', 'GET'),
                    "param": alert.get('param', ''),
                    "evidence": alert.get('evidence', ''),
                    "solution": alert.get('solution', 'No solution provided'),
                    "reference": alert.get('reference', ''),
                    "cwe_id": alert.get('cweid', ''),
                    "wasc_id": alert.get('wascid', ''),
                    "confidence": alert.get('confidence', 'Unknown')
                }
                findings.append(finding)
                
        except Exception as e:
            print(f"Error parsing ZAP report: {e}")
        
        return findings
    
    def _map_zap_severity(self, zap_risk: str) -> str:
        """Map ZAP risk levels to standard severity"""
        mapping = {
            'High': 'HIGH',
            'Medium': 'MEDIUM', 
            'Low': 'LOW',
            'Informational': 'INFO'
        }
        
        # Extract severity from "High (Confidence: High)" format
        severity = zap_risk.split('(')[0].strip()
        return mapping.get(severity, 'UNKNOWN')

class NucleiScanner(DastScanner):
    """Nuclei Template-based Vulnerability Scanner"""
    
    def __init__(self):
        super().__init__()
        self.name = "Nuclei"
        self.tool_command = "nuclei"
    
    def is_available(self) -> bool:
        """Check if Nuclei is installed"""
        try:
            result = subprocess.run([self.tool_command, "-version"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def scan(self, target_url: str, scan_timeout: int = 300, 
             templates: Optional[str] = None, **kwargs) -> List[Dict]:
        """
        Run Nuclei scan
        
        Args:
            target_url: Target URL to scan
            scan_timeout: Maximum scan time in seconds
            templates: Specific templates to use (e.g., "cves,exposures")
            
        Returns:
            List of vulnerability findings
        """
        findings = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            report_file = os.path.join(temp_dir, "nuclei_results.json")
            
            try:
                cmd = [
                    self.tool_command,
                    "-u", target_url,
                    "-json-export", report_file,
                    "-silent"
                ]
                
                # Add template specification if provided
                if templates:
                    cmd.extend(["-tags", templates])
                
                print(f"🎯 Running Nuclei scan on {target_url}")
                result = subprocess.run(cmd, capture_output=True, text=True, 
                                      timeout=scan_timeout)
                
                if os.path.exists(report_file):
                    findings = self._parse_nuclei_report(report_file, target_url)
                    
            except subprocess.TimeoutExpired:
                print(f"Nuclei scan timed out after {scan_timeout} seconds")
            except Exception as e:
                print(f"Nuclei scan error: {e}")
        
        return findings
    
    def _parse_nuclei_report(self, report_file: str, target_url: str) -> List[Dict]:
        """Parse Nuclei JSONL report"""
        findings = []
        
        try:
            with open(report_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        
                        finding = {
                            "scanner_type": "dast",
                            "scanner_name": "Nuclei",
                            "severity": self._map_nuclei_severity(data.get('info', {}).get('severity', 'info')),
                            "title": data.get('info', {}).get('name', 'Unknown Vulnerability'),
                            "description": data.get('info', {}).get('description', 'No description available'),
                            "url": data.get('matched-at', target_url),
                            "template_id": data.get('template-id', ''),
                            "template_url": data.get('template-url', ''),
                            "matcher_name": data.get('matcher-name', ''),
                            "extracted_results": data.get('extracted-results', []),
                            "tags": data.get('info', {}).get('tags', []),
                            "reference": data.get('info', {}).get('reference', [])
                        }
                        findings.append(finding)
                        
        except Exception as e:
            print(f"Error parsing Nuclei report: {e}")
        
        return findings
    
    def _map_nuclei_severity(self, nuclei_severity: str) -> str:
        """Map Nuclei severity to standard levels"""
        mapping = {
            'critical': 'CRITICAL',
            'high': 'HIGH',
            'medium': 'MEDIUM',
            'low': 'LOW',
            'info': 'INFO'
        }
        return mapping.get(nuclei_severity.lower(), 'UNKNOWN')

class NiktoScanner(DastScanner):
    """Nikto Web Server Scanner"""
    
    def __init__(self):
        super().__init__()
        self.name = "Nikto"
        self.tool_command = "nikto"
    
    def is_available(self) -> bool:
        """Check if Nikto is installed"""
        try:
            result = subprocess.run([self.tool_command, "-Version"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def scan(self, target_url: str, scan_timeout: int = 300, **kwargs) -> List[Dict]:
        """Run Nikto scan"""
        findings = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            report_file = os.path.join(temp_dir, "nikto_results.json")
            
            try:
                cmd = [
                    self.tool_command,
                    "-h", target_url,
                    "-Format", "json",
                    "-output", report_file
                ]
                
                print(f"🔍 Running Nikto scan on {target_url}")
                result = subprocess.run(cmd, capture_output=True, text=True, 
                                      timeout=scan_timeout)
                
                if os.path.exists(report_file):
                    findings = self._parse_nikto_report(report_file, target_url)
                    
            except subprocess.TimeoutExpired:
                print(f"Nikto scan timed out after {scan_timeout} seconds")
            except Exception as e:
                print(f"Nikto scan error: {e}")
        
        return findings
    
    def _parse_nikto_report(self, report_file: str, target_url: str) -> List[Dict]:
        """Parse Nikto JSON report"""
        findings = []
        
        try:
            with open(report_file, 'r') as f:
                data = json.load(f)
            
            for vuln in data.get('vulnerabilities', []):
                finding = {
                    "scanner_type": "dast",
                    "scanner_name": "Nikto",
                    "severity": "MEDIUM",  # Nikto doesn't provide severity
                    "title": vuln.get('msg', 'Web Server Issue'),
                    "description": vuln.get('msg', 'No description available'),
                    "url": target_url,
                    "uri": vuln.get('uri', ''),
                    "method": vuln.get('method', 'GET'),
                    "nikto_id": vuln.get('id', ''),
                    "osvdb_id": vuln.get('osvdb', ''),
                    "references": vuln.get('refs', [])
                }
                findings.append(finding)
                
        except Exception as e:
            print(f"Error parsing Nikto report: {e}")
        
        return findings


class SqlmapScanner(DastScanner):
    """SQLMap SQL Injection Scanner"""
    
    def __init__(self):
        super().__init__()
        self.name = "SQLMap"
        self.tool_command = "sqlmap"
    
    def is_available(self) -> bool:
        """Check if SQLMap is installed"""
        try:
            result = subprocess.run([self.tool_command, "--version"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def scan(self, target_url: str, scan_timeout: int = 600, 
             scan_type: str = "basic", **kwargs) -> List[Dict]:
        """
        Run SQLMap scan for SQL injection vulnerabilities
        
        Args:
            target_url: Target URL to scan
            scan_timeout: Maximum scan time in seconds
            scan_type: Type of scan ("basic", "aggressive", "forms")
        """
        findings = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = os.path.join(temp_dir, "sqlmap_output")
            os.makedirs(output_dir, exist_ok=True)
            
            try:
                # Base SQLMap command
                cmd = [
                    self.tool_command,
                    "-u", target_url,
                    "--batch",  # Non-interactive mode
                    "--output-dir", output_dir,
                    "--technique", "BEUSTQ",  # All SQL injection techniques
                    "--timeout", "30",
                    "--retries", "2"
                ]
                
                # Add scan type specific options
                if scan_type == "aggressive":
                    cmd.extend(["--level", "3", "--risk", "2"])
                elif scan_type == "forms":
                    cmd.extend(["--forms", "--crawl", "2"])
                else:  # basic
                    cmd.extend(["--level", "1", "--risk", "1"])
                
                print(f"💉 Running SQLMap scan on {target_url}")
                result = subprocess.run(cmd, capture_output=True, text=True, 
                                      timeout=scan_timeout)
                
                # Parse SQLMap output
                findings = self._parse_sqlmap_output(output_dir, target_url, result.stdout)
                
            except subprocess.TimeoutExpired:
                print(f"SQLMap scan timed out after {scan_timeout} seconds")
            except Exception as e:
                print(f"SQLMap scan error: {e}")
        
        return findings
    
    def _parse_sqlmap_output(self, output_dir: str, target_url: str, stdout: str) -> List[Dict]:
        """Parse SQLMap output for vulnerabilities"""
        findings = []
        
        try:
            # Check for SQL injection indicators in stdout
            if "sqlmap identified the following injection point" in stdout.lower():
                # Parse injection points
                lines = stdout.split('\n')
                current_finding = {}
                
                for line in lines:
                    line = line.strip()
                    
                    if "Parameter:" in line:
                        current_finding["parameter"] = line.split("Parameter:")[1].strip()
                    elif "Type:" in line:
                        current_finding["injection_type"] = line.split("Type:")[1].strip()
                    elif "Title:" in line:
                        current_finding["title"] = line.split("Title:")[1].strip()
                    elif "Payload:" in line:
                        current_finding["payload"] = line.split("Payload:")[1].strip()
                        
                        # Create finding when we have a complete set
                        if all(k in current_finding for k in ["parameter", "injection_type", "title"]):
                            findings.append({
                                "tool": "sqlmap",
                                "type": "sql_injection",
                                "severity": "HIGH",
                                "title": current_finding.get("title", "SQL Injection Vulnerability"),
                                "description": f"SQL injection found in parameter '{current_finding.get('parameter', 'unknown')}'",
                                "parameter": current_finding.get("parameter", ""),
                                "injection_type": current_finding.get("injection_type", ""),
                                "payload": current_finding.get("payload", ""),
                                "url": target_url,
                                "impact": "Critical - Potential data extraction, authentication bypass, or data manipulation",
                                "recommendation": "Use parameterized queries and input validation"
                            })
                            current_finding = {}
            
            # Check log files in output directory
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith('.log'):
                        log_path = os.path.join(root, file)
                        try:
                            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                                log_content = f.read()
                                if "vulnerable" in log_content.lower():
                                    findings.append({
                                        "tool": "sqlmap",
                                        "type": "sql_injection",
                                        "severity": "HIGH",
                                        "title": "SQL Injection Detected",
                                        "description": "SQLMap detected potential SQL injection vulnerability",
                                        "url": target_url,
                                        "log_file": log_path,
                                        "impact": "Critical - Database access vulnerability",
                                        "recommendation": "Implement proper input validation and parameterized queries"
                                    })
                        except Exception as e:
                            print(f"Error reading log file {log_path}: {e}")
        
        except Exception as e:
            print(f"Error parsing SQLMap output: {e}")
        
        return findings


class NmapScanner(DastScanner):
    """Nmap Network Discovery and Security Scanner"""
    
    def __init__(self):
        super().__init__()
        self.name = "Nmap"
        self.tool_command = "nmap"
    
    def is_available(self) -> bool:
        """Check if Nmap is installed"""
        try:
            result = subprocess.run([self.tool_command, "--version"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def scan(self, target_url: str, scan_timeout: int = 300, 
             scan_type: str = "basic", **kwargs) -> List[Dict]:
        """
        Run Nmap scan for network discovery and security assessment
        
        Args:
            target_url: Target URL/IP to scan
            scan_timeout: Maximum scan time in seconds
            scan_type: Type of scan ("basic", "service", "vuln", "full")
        """
        findings = []
        
        # Extract hostname/IP from URL
        from urllib.parse import urlparse
        parsed = urlparse(target_url if target_url.startswith('http') else f'http://{target_url}')
        target = parsed.hostname or target_url
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "nmap_output.xml")
            
            try:
                # Build Nmap command based on scan type
                cmd = [self.tool_command, "-oX", output_file]
                
                if scan_type == "basic":
                    cmd.extend(["-sS", "-F"])  # TCP SYN scan, fast mode
                elif scan_type == "service":
                    cmd.extend(["-sS", "-sV", "-O"])  # Service detection + OS detection
                elif scan_type == "vuln":
                    cmd.extend(["-sS", "-sV", "--script", "vuln"])  # Vulnerability scripts
                elif scan_type == "full":
                    cmd.extend(["-sS", "-sV", "-O", "-A", "--script", "default,vuln"])
                else:
                    cmd.extend(["-sS", "-F"])  # Default to basic
                
                cmd.append(target)
                
                print(f"🔍 Running Nmap scan on {target}")
                result = subprocess.run(cmd, capture_output=True, text=True, 
                                      timeout=scan_timeout)
                
                # Parse Nmap output
                if os.path.exists(output_file):
                    findings = self._parse_nmap_output(output_file, target_url)
                
            except subprocess.TimeoutExpired:
                print(f"Nmap scan timed out after {scan_timeout} seconds")
            except Exception as e:
                print(f"Nmap scan error: {e}")
        
        return findings
    
    def _parse_nmap_output(self, output_file: str, target_url: str) -> List[Dict]:
        """Parse Nmap XML output"""
        findings = []
        
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(output_file)
            root = tree.getroot()
            
            for host in root.findall('host'):
                # Get host IP
                address = host.find('address')
                host_ip = address.get('addr') if address is not None else 'unknown'
                
                # Check host status
                status = host.find('status')
                if status is not None and status.get('state') == 'up':
                    
                    # Parse open ports
                    ports = host.find('ports')
                    if ports is not None:
                        for port in ports.findall('port'):
                            port_id = port.get('portid')
                            protocol = port.get('protocol')
                            
                            state = port.find('state')
                            service = port.find('service')
                            
                            if state is not None and state.get('state') == 'open':
                                service_name = service.get('name') if service is not None else 'unknown'
                                service_version = service.get('version') if service is not None else ''
                                
                                # Determine severity based on service
                                severity = self._assess_port_risk(port_id, service_name)
                                
                                findings.append({
                                    "tool": "nmap",
                                    "type": "open_port",
                                    "severity": severity,
                                    "title": f"Open Port {port_id}/{protocol}",
                                    "description": f"Open {service_name} service on port {port_id}",
                                    "host": host_ip,
                                    "port": port_id,
                                    "protocol": protocol,
                                    "service": service_name,
                                    "version": service_version,
                                    "url": target_url,
                                    "impact": f"Exposed {service_name} service may be vulnerable to attacks",
                                    "recommendation": "Review if this service needs to be publicly accessible"
                                })
                
                # Parse script results (vulnerabilities)
                hostscript = host.find('hostscript')
                if hostscript is not None:
                    for script in hostscript.findall('script'):
                        script_id = script.get('id')
                        script_output = script.get('output')
                        
                        if 'vuln' in script_id.lower() or 'exploit' in script_output.lower():
                            findings.append({
                                "tool": "nmap",
                                "type": "vulnerability",
                                "severity": "HIGH",
                                "title": f"Vulnerability detected: {script_id}",
                                "description": script_output,
                                "host": host_ip,
                                "script": script_id,
                                "url": target_url,
                                "impact": "Potential security vulnerability detected",
                                "recommendation": "Investigate and remediate the identified vulnerability"
                            })
                            
        except Exception as e:
            print(f"Error parsing Nmap output: {e}")
        
        return findings
    
    def _assess_port_risk(self, port: str, service: str) -> str:
        """Assess risk level based on port and service"""
        high_risk_ports = ['21', '22', '23', '25', '53', '80', '110', '143', '443', '993', '995']
        high_risk_services = ['ftp', 'ssh', 'telnet', 'smtp', 'dns', 'http', 'https', 'pop3', 'imap']
        
        if port in high_risk_ports or service.lower() in high_risk_services:
            return "MEDIUM"
        else:
            return "LOW"


# Integration with existing DefenSys architecture
class DastScannerManager:
    """Manager for all DAST scanners"""
    
    def __init__(self):
        self.scanners = {
            "zap": ZapScanner(),
            "nuclei": NucleiScanner(), 
            "nikto": NiktoScanner(),
            "sqlmap": SqlmapScanner(),
            "nmap": NmapScanner()
        }
    
    def get_available_scanners(self) -> Dict[str, bool]:
        """Check which DAST tools are available"""
        availability = {}
        for name, scanner in self.scanners.items():
            availability[name] = scanner.is_available()
        return availability
    
    def run_dast_scan(self, target_url: str, scanner_types: List[str] = None, 
                      **kwargs) -> List[Dict]:
        """
        Run DAST scans on target URL
        
        Args:
            target_url: URL to scan
            scanner_types: List of scanners to use (default: all available)
            
        Returns:
            Combined results from all scanners
        """
        if not scanner_types:
            scanner_types = list(self.scanners.keys())
        
        all_findings = []
        
        for scanner_type in scanner_types:
            if scanner_type in self.scanners:
                scanner = self.scanners[scanner_type]
                if scanner.is_available():
                    print(f"🚀 Running {scanner.name} scan...")
                    findings = scanner.scan(target_url, **kwargs)
                    all_findings.extend(findings)
                    print(f"✅ {scanner.name} found {len(findings)} issues")
                else:
                    print(f"❌ {scanner.name} is not available")
        
        return all_findings
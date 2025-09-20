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

# Integration with existing DefenSys architecture
class DastScannerManager:
    """Manager for all DAST scanners"""
    
    def __init__(self):
        self.scanners = {
            "zap": ZapScanner(),
            "nuclei": NucleiScanner(), 
            "nikto": NiktoScanner()
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
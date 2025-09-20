import subprocess
import json
import os
from typing import List, Dict, Optional
from .base import Scanner

class SnykScanner(Scanner):
    """
    Snyk scanner for vulnerability detection in dependencies, containers, and code.
    Requires Snyk CLI to be installed and authenticated.
    """
    
    def __init__(self, auth_token: Optional[str] = None):
        self.auth_token = auth_token or os.getenv('SNYK_TOKEN')
        
    def scan(self, path: str, scan_type: str = "all") -> List[dict]:
        """
        Scan for vulnerabilities using Snyk
        
        Args:
            path: Path to scan
            scan_type: Type of scan ("code", "oss", "container", "iac", "all")
        """
        if not os.path.exists(path):
            print(f"Path does not exist: {path}")
            return []
            
        vulnerabilities = []
        
        if scan_type in ["all", "oss"]:
            vulnerabilities.extend(self._scan_dependencies(path))
            
        if scan_type in ["all", "code"]:
            vulnerabilities.extend(self._scan_code(path))
            
        if scan_type in ["all", "container"]:
            vulnerabilities.extend(self._scan_container(path))
            
        if scan_type in ["all", "iac"]:
            vulnerabilities.extend(self._scan_infrastructure(path))
            
        return vulnerabilities
    
    def _scan_dependencies(self, path: str) -> List[dict]:
        """Scan for vulnerabilities in dependencies (npm, pip, etc.)"""
        try:
            cmd = ["snyk", "test", "--json", "--all-projects"]
            if self.auth_token:
                cmd.extend(["--auth", self.auth_token])
                
            result = subprocess.run(
                cmd,
                cwd=path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Snyk returns exit code 1 when vulnerabilities are found
            if result.returncode not in [0, 1]:
                print(f"Snyk dependencies scan failed: {result.stderr}")
                return []
                
            if result.stdout:
                data = json.loads(result.stdout)
                return self._parse_snyk_vulnerabilities(data, "dependencies")
                
        except subprocess.TimeoutExpired:
            print("Snyk dependencies scan timed out")
        except json.JSONDecodeError as e:
            print(f"Error parsing Snyk dependencies output: {e}")
        except FileNotFoundError:
            print("Snyk CLI not found. Please install it: npm install -g snyk")
        except Exception as e:
            print(f"Error running Snyk dependencies scan: {e}")
            
        return []
    
    def _scan_code(self, path: str) -> List[dict]:
        """Scan for code vulnerabilities using Snyk Code"""
        try:
            cmd = ["snyk", "code", "test", "--json"]
            if self.auth_token:
                cmd.extend(["--auth", self.auth_token])
                
            result = subprocess.run(
                cmd,
                cwd=path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode not in [0, 1]:
                print(f"Snyk code scan failed: {result.stderr}")
                return []
                
            if result.stdout:
                data = json.loads(result.stdout)
                return self._parse_snyk_vulnerabilities(data, "code")
                
        except subprocess.TimeoutExpired:
            print("Snyk code scan timed out")
        except json.JSONDecodeError as e:
            print(f"Error parsing Snyk code output: {e}")
        except FileNotFoundError:
            print("Snyk CLI not found. Please install it: npm install -g snyk")
        except Exception as e:
            print(f"Error running Snyk code scan: {e}")
            
        return []
    
    def _scan_container(self, path: str) -> List[dict]:
        """Scan container images for vulnerabilities"""
        try:
            # Look for Dockerfile or container images
            dockerfile_path = os.path.join(path, "Dockerfile")
            if not os.path.exists(dockerfile_path):
                return []
                
            cmd = ["snyk", "container", "test", dockerfile_path, "--json"]
            if self.auth_token:
                cmd.extend(["--auth", self.auth_token])
                
            result = subprocess.run(
                cmd,
                cwd=path,
                capture_output=True,
                text=True,
                timeout=600  # Container scans can take longer
            )
            
            if result.returncode not in [0, 1]:
                print(f"Snyk container scan failed: {result.stderr}")
                return []
                
            if result.stdout:
                data = json.loads(result.stdout)
                return self._parse_snyk_vulnerabilities(data, "container")
                
        except subprocess.TimeoutExpired:
            print("Snyk container scan timed out")
        except json.JSONDecodeError as e:
            print(f"Error parsing Snyk container output: {e}")
        except Exception as e:
            print(f"Error running Snyk container scan: {e}")
            
        return []
    
    def _scan_infrastructure(self, path: str) -> List[dict]:
        """Scan Infrastructure as Code files (Terraform, K8s, etc.)"""
        try:
            cmd = ["snyk", "iac", "test", "--json"]
            if self.auth_token:
                cmd.extend(["--auth", self.auth_token])
                
            result = subprocess.run(
                cmd,
                cwd=path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode not in [0, 1]:
                print(f"Snyk IaC scan failed: {result.stderr}")
                return []
                
            if result.stdout:
                data = json.loads(result.stdout)
                return self._parse_snyk_vulnerabilities(data, "infrastructure")
                
        except subprocess.TimeoutExpired:
            print("Snyk IaC scan timed out")
        except json.JSONDecodeError as e:
            print(f"Error parsing Snyk IaC output: {e}")
        except Exception as e:
            print(f"Error running Snyk IaC scan: {e}")
            
        return []
    
    def _parse_snyk_vulnerabilities(self, data: Dict, scan_type: str) -> List[dict]:
        """Parse Snyk JSON output into standardized vulnerability format"""
        vulnerabilities = []
        
        if isinstance(data, list):
            # Multiple projects
            for project_data in data:
                vulnerabilities.extend(self._parse_single_project(project_data, scan_type))
        else:
            # Single project
            vulnerabilities.extend(self._parse_single_project(data, scan_type))
            
        return vulnerabilities
    
    def _parse_single_project(self, data: Dict, scan_type: str) -> List[dict]:
        """Parse vulnerability data from a single project"""
        vulnerabilities = []
        
        # Handle different Snyk output formats
        issues = data.get('vulnerabilities', [])
        if not issues:
            issues = data.get('issues', [])
        if not issues and 'runs' in data:
            # SARIF format (Snyk Code)
            for run in data['runs']:
                for result in run.get('results', []):
                    vulnerabilities.append(self._parse_sarif_result(result, scan_type))
            return vulnerabilities
            
        for issue in issues:
            vuln = {
                "type": "snyk_vulnerability",
                "scanner": "snyk",
                "scan_type": scan_type,
                "id": issue.get('id', 'unknown'),
                "title": issue.get('title', 'Unknown vulnerability'),
                "description": issue.get('description', ''),
                "severity": self._normalize_severity(issue.get('severity', 'unknown')),
                "cvss_score": issue.get('cvssScore'),
                "cve": issue.get('identifiers', {}).get('CVE', []),
                "cwe": issue.get('identifiers', {}).get('CWE', []),
                "package_name": issue.get('packageName'),
                "package_version": issue.get('version'),
                "fixed_in": issue.get('fixedIn', []),
                "exploit_maturity": issue.get('exploitMaturity'),
                "is_malicious": issue.get('isMaliciousPackage', False),
                "file_path": issue.get('from', [''])[0] if issue.get('from') else '',
                "upgrade_path": issue.get('upgradePath', []),
                "patches": issue.get('patches', []),
                "references": issue.get('references', [])
            }
            vulnerabilities.append(vuln)
            
        return vulnerabilities
    
    def _parse_sarif_result(self, result: Dict, scan_type: str) -> dict:
        """Parse SARIF format result (used by Snyk Code)"""
        location = result.get('locations', [{}])[0]
        physical_location = location.get('physicalLocation', {})
        
        return {
            "type": "snyk_vulnerability",
            "scanner": "snyk",
            "scan_type": scan_type,
            "id": result.get('ruleId', 'unknown'),
            "title": result.get('message', {}).get('text', 'Code vulnerability'),
            "description": result.get('message', {}).get('text', ''),
            "severity": self._normalize_severity(result.get('level', 'unknown')),
            "file_path": physical_location.get('artifactLocation', {}).get('uri', ''),
            "line": physical_location.get('region', {}).get('startLine'),
            "column": physical_location.get('region', {}).get('startColumn'),
            "rule_id": result.get('ruleId'),
            "help_uri": result.get('helpUri', ''),
            "fingerprints": result.get('fingerprints', {})
        }
    
    def _normalize_severity(self, severity: str) -> str:
        """Normalize severity levels to standard format"""
        severity_map = {
            'critical': 'CRITICAL',
            'high': 'HIGH', 
            'medium': 'MEDIUM',
            'low': 'LOW',
            'info': 'INFO',
            'note': 'INFO',
            'warning': 'MEDIUM',
            'error': 'HIGH'
        }
        return severity_map.get(severity.lower(), 'UNKNOWN')
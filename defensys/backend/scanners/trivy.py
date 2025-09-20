import subprocess
import json
import os
from typing import List, Dict, Optional
from .base import Scanner

class TrivyScanner(Scanner):
    """
    Trivy scanner for comprehensive vulnerability detection in:
    - Container images
    - Filesystems 
    - Git repositories
    - Kubernetes manifests
    - Infrastructure as Code
    """
    
    def __init__(self):
        self.supported_targets = ['fs', 'image', 'repo', 'config']
        
    def scan(self, path: str, target_type: str = "fs", image_name: Optional[str] = None) -> List[dict]:
        """
        Scan for vulnerabilities using Trivy
        
        Args:
            path: Path to scan
            target_type: Type of target ("fs", "image", "repo", "config")
            image_name: Docker image name (required for image scans)
        """
        if not os.path.exists(path) and target_type != "image":
            print(f"Path does not exist: {path}")
            return []
            
        vulnerabilities = []
        
        if target_type == "fs":
            vulnerabilities.extend(self._scan_filesystem(path))
        elif target_type == "image":
            if image_name:
                vulnerabilities.extend(self._scan_image(image_name))
            else:
                # Try to find Dockerfile and build/scan
                vulnerabilities.extend(self._scan_dockerfile(path))
        elif target_type == "repo":
            vulnerabilities.extend(self._scan_repository(path))
        elif target_type == "config":
            vulnerabilities.extend(self._scan_config(path))
        else:
            print(f"Unsupported target type: {target_type}")
            
        return vulnerabilities
    
    def _scan_filesystem(self, path: str) -> List[dict]:
        """Scan filesystem for vulnerabilities"""
        try:
            cmd = [
                "trivy", "fs",
                "--format", "json",
                "--security-checks", "vuln,secret,config",
                "--timeout", "10m",
                path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode != 0:
                print(f"Trivy filesystem scan failed: {result.stderr}")
                return []
                
            if result.stdout:
                data = json.loads(result.stdout)
                return self._parse_trivy_results(data, "filesystem")
                
        except subprocess.TimeoutExpired:
            print("Trivy filesystem scan timed out")
        except json.JSONDecodeError as e:
            print(f"Error parsing Trivy filesystem output: {e}")
        except FileNotFoundError:
            print("Trivy not found. Please install it: https://aquasecurity.github.io/trivy/")
        except Exception as e:
            print(f"Error running Trivy filesystem scan: {e}")
            
        return []
    
    def _scan_image(self, image_name: str) -> List[dict]:
        """Scan Docker image for vulnerabilities"""
        try:
            cmd = [
                "trivy", "image",
                "--format", "json",
                "--security-checks", "vuln,secret,config",
                "--timeout", "15m",
                image_name
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=900  # 15 minute timeout
            )
            
            if result.returncode != 0:
                print(f"Trivy image scan failed: {result.stderr}")
                return []
                
            if result.stdout:
                data = json.loads(result.stdout)
                return self._parse_trivy_results(data, "image")
                
        except subprocess.TimeoutExpired:
            print("Trivy image scan timed out")
        except json.JSONDecodeError as e:
            print(f"Error parsing Trivy image output: {e}")
        except Exception as e:
            print(f"Error running Trivy image scan: {e}")
            
        return []
    
    def _scan_dockerfile(self, path: str) -> List[dict]:
        """Build and scan Dockerfile in the given path"""
        dockerfile_path = os.path.join(path, "Dockerfile")
        if not os.path.exists(dockerfile_path):
            print(f"No Dockerfile found in {path}")
            return []
            
        try:
            # Build image first
            image_tag = "trivy-scan:latest"
            build_cmd = ["docker", "build", "-t", image_tag, path]
            
            build_result = subprocess.run(
                build_cmd,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if build_result.returncode != 0:
                print(f"Docker build failed: {build_result.stderr}")
                return []
                
            # Scan the built image
            return self._scan_image(image_tag)
            
        except subprocess.TimeoutExpired:
            print("Docker build timed out")
        except Exception as e:
            print(f"Error building/scanning Dockerfile: {e}")
            
        return []
    
    def _scan_repository(self, path: str) -> List[dict]:
        """Scan Git repository for vulnerabilities"""
        try:
            cmd = [
                "trivy", "repo",
                "--format", "json",
                "--security-checks", "vuln,secret,config",
                "--timeout", "10m",
                path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode != 0:
                print(f"Trivy repository scan failed: {result.stderr}")
                return []
                
            if result.stdout:
                data = json.loads(result.stdout)
                return self._parse_trivy_results(data, "repository")
                
        except subprocess.TimeoutExpired:
            print("Trivy repository scan timed out")
        except json.JSONDecodeError as e:
            print(f"Error parsing Trivy repository output: {e}")
        except Exception as e:
            print(f"Error running Trivy repository scan: {e}")
            
        return []
    
    def _scan_config(self, path: str) -> List[dict]:
        """Scan configuration files (IaC) for misconfigurations"""
        try:
            cmd = [
                "trivy", "config",
                "--format", "json",
                "--timeout", "5m",
                path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                print(f"Trivy config scan failed: {result.stderr}")
                return []
                
            if result.stdout:
                data = json.loads(result.stdout)
                return self._parse_trivy_results(data, "config")
                
        except subprocess.TimeoutExpired:
            print("Trivy config scan timed out")
        except json.JSONDecodeError as e:
            print(f"Error parsing Trivy config output: {e}")
        except Exception as e:
            print(f"Error running Trivy config scan: {e}")
            
        return []
    
    def _parse_trivy_results(self, data: Dict, scan_type: str) -> List[dict]:
        """Parse Trivy JSON output into standardized vulnerability format"""
        vulnerabilities = []
        
        # Trivy can return either a single result or a list of results
        results = data.get('Results', [])
        if not results and 'Target' in data:
            # Single result format
            results = [data]
            
        for result in results:
            target = result.get('Target', 'unknown')
            result_class = result.get('Class', 'unknown')
            
            # Parse vulnerabilities
            for vuln in result.get('Vulnerabilities', []):
                vulnerability = {
                    "type": "trivy_vulnerability",
                    "scanner": "trivy",
                    "scan_type": scan_type,
                    "target": target,
                    "class": result_class,
                    "vulnerability_id": vuln.get('VulnerabilityID', 'unknown'),
                    "pkg_id": vuln.get('PkgID', ''),
                    "pkg_name": vuln.get('PkgName', ''),
                    "pkg_path": vuln.get('PkgPath', ''),
                    "installed_version": vuln.get('InstalledVersion', ''),
                    "fixed_version": vuln.get('FixedVersion', ''),
                    "status": vuln.get('Status', ''),
                    "title": vuln.get('Title', ''),
                    "description": vuln.get('Description', ''),
                    "severity": self._normalize_severity(vuln.get('Severity', 'unknown')),
                    "cvss": vuln.get('CVSS', {}),
                    "cwe_ids": vuln.get('CweIDs', []),
                    "references": vuln.get('References', []),
                    "published_date": vuln.get('PublishedDate', ''),
                    "last_modified_date": vuln.get('LastModifiedDate', ''),
                    "primary_url": vuln.get('PrimaryURL', ''),
                    "data_source": vuln.get('DataSource', {})
                }
                vulnerabilities.append(vulnerability)
            
            # Parse secrets
            for secret in result.get('Secrets', []):
                secret_vuln = {
                    "type": "trivy_secret",
                    "scanner": "trivy",
                    "scan_type": scan_type,
                    "target": target,
                    "rule_id": secret.get('RuleID', ''),
                    "category": secret.get('Category', ''),
                    "severity": self._normalize_severity(secret.get('Severity', 'unknown')),
                    "title": secret.get('Title', ''),
                    "start_line": secret.get('StartLine', 0),
                    "end_line": secret.get('EndLine', 0),
                    "code": secret.get('Code', {}),
                    "match": secret.get('Match', ''),
                    "layer": secret.get('Layer', {})
                }
                vulnerabilities.append(secret_vuln)
            
            # Parse misconfigurations
            for misconfig in result.get('Misconfigurations', []):
                misconfig_vuln = {
                    "type": "trivy_misconfiguration",
                    "scanner": "trivy",
                    "scan_type": scan_type,
                    "target": target,
                    "rule_id": misconfig.get('ID', ''),
                    "avd_id": misconfig.get('AVDID', ''),
                    "rule_type": misconfig.get('Type', ''),
                    "title": misconfig.get('Title', ''),
                    "description": misconfig.get('Description', ''),
                    "message": misconfig.get('Message', ''),
                    "namespace": misconfig.get('Namespace', ''),
                    "query": misconfig.get('Query', ''),
                    "resolution": misconfig.get('Resolution', ''),
                    "severity": self._normalize_severity(misconfig.get('Severity', 'unknown')),
                    "primary_url": misconfig.get('PrimaryURL', ''),
                    "references": misconfig.get('References', []),
                    "status": misconfig.get('Status', ''),
                    "layer": misconfig.get('Layer', {}),
                    "cause_metadata": misconfig.get('CauseMetadata', {})
                }
                vulnerabilities.append(misconfig_vuln)
                
        return vulnerabilities
    
    def _normalize_severity(self, severity: str) -> str:
        """Normalize severity levels to standard format"""
        severity_map = {
            'critical': 'CRITICAL',
            'high': 'HIGH',
            'medium': 'MEDIUM', 
            'low': 'LOW',
            'info': 'INFO',
            'unknown': 'UNKNOWN'
        }
        return severity_map.get(severity.lower(), 'UNKNOWN')
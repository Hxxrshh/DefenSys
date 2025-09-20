"""
Additional Security Scanners for DefenSys
Enhanced security tool implementations
"""

import subprocess
import json
import os
import tempfile
from typing import List, Dict, Optional
from .base import Scanner


class GitLeaksScanner(Scanner):
    """Gitleaks scanner for detecting secrets in git repositories"""
    
    def __init__(self):
        self.name = "GitLeaks"
    
    def scan(self, path: str, scan_type: str = "detect") -> List[dict]:
        """
        Scan git repository for secrets using Gitleaks
        
        Args:
            path: Path to git repository
            scan_type: Type of scan ("detect", "protect")
        """
        if not os.path.exists(path):
            print(f"Path does not exist: {path}")
            return []
        
        vulnerabilities = []
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                report_file = temp_file.name
            
            cmd = [
                "gitleaks", scan_type,
                "--source", path,
                "--report-format", "json",
                "--report-path", report_file,
                "--verbose"
            ]
            
            print(f"🔍 Running GitLeaks scan on {path}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if os.path.exists(report_file) and os.path.getsize(report_file) > 0:
                with open(report_file, 'r') as f:
                    data = json.load(f)
                    
                for finding in data:
                    vulnerabilities.append({
                        "tool": "gitleaks",
                        "type": "secret_exposure",
                        "severity": "HIGH",
                        "description": f"Secret detected: {finding.get('Description', 'Unknown')}",
                        "file": finding.get('File', ''),
                        "line": finding.get('StartLine', 0),
                        "rule": finding.get('RuleID', ''),
                        "match": finding.get('Match', ''),
                        "commit": finding.get('Commit', ''),
                        "author": finding.get('Author', ''),
                        "email": finding.get('Email', ''),
                        "date": finding.get('Date', '')
                    })
            
            # Clean up
            if os.path.exists(report_file):
                os.unlink(report_file)
                
        except subprocess.TimeoutExpired:
            print("GitLeaks scan timed out")
        except json.JSONDecodeError as e:
            print(f"Error parsing GitLeaks output: {e}")
        except Exception as e:
            print(f"Error running GitLeaks: {e}")
        
        return vulnerabilities
    
    def is_available(self) -> bool:
        """Check if GitLeaks is installed"""
        try:
            result = subprocess.run(["gitleaks", "version"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False


class SafetyScanner(Scanner):
    """Safety scanner for Python dependency vulnerabilities"""
    
    def __init__(self):
        self.name = "Safety"
    
    def scan(self, path: str) -> List[dict]:
        """
        Scan Python dependencies for known vulnerabilities
        
        Args:
            path: Path to scan (should contain requirements.txt or setup.py)
        """
        if not os.path.exists(path):
            print(f"Path does not exist: {path}")
            return []
        
        vulnerabilities = []
        
        try:
            # Try different file locations
            requirements_files = [
                os.path.join(path, "requirements.txt"),
                os.path.join(path, "requirements-dev.txt"),
                os.path.join(path, "setup.py"),
                os.path.join(path, "pyproject.toml")
            ]
            
            for req_file in requirements_files:
                if os.path.exists(req_file):
                    vulnerabilities.extend(self._scan_requirements_file(req_file))
            
            # If no requirements files found, scan current environment
            if not vulnerabilities:
                vulnerabilities.extend(self._scan_current_environment())
                
        except Exception as e:
            print(f"Error running Safety scanner: {e}")
        
        return vulnerabilities
    
    def _scan_requirements_file(self, requirements_file: str) -> List[dict]:
        """Scan a specific requirements file"""
        vulnerabilities = []
        
        try:
            cmd = ["safety", "check", "-r", requirements_file, "--json"]
            
            print(f"🔍 Running Safety scan on {requirements_file}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.stdout:
                data = json.loads(result.stdout)
                
                for vuln in data:
                    vulnerabilities.append({
                        "tool": "safety",
                        "type": "dependency_vulnerability",
                        "severity": self._map_safety_severity(vuln.get("vulnerability_id", "")),
                        "description": vuln.get("advisory", "Unknown vulnerability"),
                        "package": vuln.get("package_name", ""),
                        "installed_version": vuln.get("installed_version", ""),
                        "affected_versions": vuln.get("affected_versions", ""),
                        "safe_versions": vuln.get("safe_versions", ""),
                        "vulnerability_id": vuln.get("vulnerability_id", ""),
                        "more_info_url": vuln.get("more_info_url", ""),
                        "file": requirements_file
                    })
                    
        except json.JSONDecodeError as e:
            print(f"Error parsing Safety output: {e}")
        except Exception as e:
            print(f"Error scanning {requirements_file}: {e}")
        
        return vulnerabilities
    
    def _scan_current_environment(self) -> List[dict]:
        """Scan current Python environment"""
        vulnerabilities = []
        
        try:
            cmd = ["safety", "check", "--json"]
            
            print("🔍 Running Safety scan on current environment")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.stdout:
                data = json.loads(result.stdout)
                
                for vuln in data:
                    vulnerabilities.append({
                        "tool": "safety",
                        "type": "dependency_vulnerability",
                        "severity": self._map_safety_severity(vuln.get("vulnerability_id", "")),
                        "description": vuln.get("advisory", "Unknown vulnerability"),
                        "package": vuln.get("package_name", ""),
                        "installed_version": vuln.get("installed_version", ""),
                        "affected_versions": vuln.get("affected_versions", ""),
                        "safe_versions": vuln.get("safe_versions", ""),
                        "vulnerability_id": vuln.get("vulnerability_id", ""),
                        "more_info_url": vuln.get("more_info_url", ""),
                        "file": "current_environment"
                    })
                    
        except json.JSONDecodeError as e:
            print(f"Error parsing Safety output: {e}")
        except Exception as e:
            print(f"Error scanning current environment: {e}")
        
        return vulnerabilities
    
    def _map_safety_severity(self, vuln_id: str) -> str:
        """Map Safety vulnerability to severity level"""
        # Safety doesn't provide severity directly, so we'll infer it
        if not vuln_id:
            return "MEDIUM"
        
        # CVE-based vulnerabilities are typically higher severity
        if vuln_id.startswith("CVE-"):
            return "HIGH"
        elif vuln_id.startswith("GHSA-"):  # GitHub Security Advisory
            return "MEDIUM"
        else:
            return "MEDIUM"
    
    def is_available(self) -> bool:
        """Check if Safety is installed"""
        try:
            result = subprocess.run(["safety", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False


class NpmAuditScanner(Scanner):
    """npm audit scanner for Node.js dependency vulnerabilities"""
    
    def __init__(self):
        self.name = "npm audit"
    
    def scan(self, path: str) -> List[dict]:
        """
        Scan Node.js dependencies for vulnerabilities using npm audit
        
        Args:
            path: Path to scan (should contain package.json)
        """
        if not os.path.exists(path):
            print(f"Path does not exist: {path}")
            return []
        
        package_json = os.path.join(path, "package.json")
        if not os.path.exists(package_json):
            print(f"No package.json found in {path}")
            return []
        
        vulnerabilities = []
        
        try:
            # Change to the project directory
            original_cwd = os.getcwd()
            os.chdir(path)
            
            cmd = ["npm", "audit", "--json"]
            
            print(f"🔍 Running npm audit scan on {path}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            if result.stdout:
                data = json.loads(result.stdout)
                
                # Parse npm audit output (format can vary)
                if "vulnerabilities" in data:
                    for vuln_name, vuln_info in data["vulnerabilities"].items():
                        vulnerabilities.append({
                            "tool": "npm_audit",
                            "type": "dependency_vulnerability",
                            "severity": vuln_info.get("severity", "UNKNOWN").upper(),
                            "description": f"Vulnerability in {vuln_name}: {vuln_info.get('title', 'Unknown')}",
                            "package": vuln_name,
                            "current_version": vuln_info.get("range", ""),
                            "vulnerable_versions": vuln_info.get("range", ""),
                            "patched_versions": vuln_info.get("fixAvailable", ""),
                            "cwe": vuln_info.get("cwe", []),
                            "cvss_score": vuln_info.get("cvss", {}).get("score", 0),
                            "references": vuln_info.get("references", []),
                            "file": "package.json"
                        })
                
        except json.JSONDecodeError as e:
            print(f"Error parsing npm audit output: {e}")
        except Exception as e:
            print(f"Error running npm audit: {e}")
        finally:
            os.chdir(original_cwd)
        
        return vulnerabilities
    
    def is_available(self) -> bool:
        """Check if npm is installed"""
        try:
            result = subprocess.run(["npm", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False


class YarnAuditScanner(Scanner):
    """Yarn audit scanner for Node.js dependency vulnerabilities"""
    
    def __init__(self):
        self.name = "yarn audit"
    
    def scan(self, path: str) -> List[dict]:
        """
        Scan Node.js dependencies for vulnerabilities using yarn audit
        
        Args:
            path: Path to scan (should contain package.json and yarn.lock)
        """
        if not os.path.exists(path):
            print(f"Path does not exist: {path}")
            return []
        
        package_json = os.path.join(path, "package.json")
        yarn_lock = os.path.join(path, "yarn.lock")
        
        if not os.path.exists(package_json):
            print(f"No package.json found in {path}")
            return []
        
        if not os.path.exists(yarn_lock):
            print(f"No yarn.lock found in {path}")
            return []
        
        vulnerabilities = []
        
        try:
            # Change to the project directory
            original_cwd = os.getcwd()
            os.chdir(path)
            
            cmd = ["yarn", "audit", "--json"]
            
            print(f"🔍 Running yarn audit scan on {path}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            if result.stdout:
                # Yarn audit outputs JSONL (JSON Lines)
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        try:
                            data = json.loads(line)
                            
                            if data.get("type") == "auditAdvisory":
                                advisory = data.get("data", {}).get("advisory", {})
                                
                                vulnerabilities.append({
                                    "tool": "yarn_audit",
                                    "type": "dependency_vulnerability",
                                    "severity": advisory.get("severity", "UNKNOWN").upper(),
                                    "description": advisory.get("title", "Unknown vulnerability"),
                                    "package": advisory.get("module_name", ""),
                                    "current_version": advisory.get("findings", [{}])[0].get("version", ""),
                                    "vulnerable_versions": advisory.get("vulnerable_versions", ""),
                                    "patched_versions": advisory.get("patched_versions", ""),
                                    "cwe": advisory.get("cwe", ""),
                                    "cvss_score": advisory.get("cvss", {}).get("score", 0),
                                    "references": advisory.get("references", []),
                                    "recommendation": advisory.get("recommendation", ""),
                                    "file": "package.json"
                                })
                        except json.JSONDecodeError:
                            continue
                
        except Exception as e:
            print(f"Error running yarn audit: {e}")
        finally:
            os.chdir(original_cwd)
        
        return vulnerabilities
    
    def is_available(self) -> bool:
        """Check if yarn is installed"""
        try:
            result = subprocess.run(["yarn", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
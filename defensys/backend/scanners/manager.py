from .sast import BanditScanner
from .dependency import PipAuditScanner
from .secret import SecretScanner
from .snyk import SnykScanner
from .trivy import TrivyScanner
from .semgrep import SemgrepScanner
from .additional import GitLeaksScanner, SafetyScanner, NpmAuditScanner, YarnAuditScanner
from typing import Dict, List, Optional
import asyncio
import concurrent.futures
import os

class ScannerManager:
    def __init__(self):
        self.basic_scanners = {
            "sast": BanditScanner(),
            "dependency": PipAuditScanner(),
            "secret": SecretScanner(),
        }
        
        self.advanced_scanners = {
            "snyk": SnykScanner(),
            "trivy": TrivyScanner(),
            "semgrep": SemgrepScanner(),
        }
        
        self.additional_scanners = {
            "gitleaks": GitLeaksScanner(),
            "safety": SafetyScanner(),
            "npm_audit": NpmAuditScanner(),
            "yarn_audit": YarnAuditScanner(),
        }
        
        self.all_scanners = {
            **self.basic_scanners, 
            **self.advanced_scanners,
            **self.additional_scanners
        }

    def run_scan(self, scan_type: str, path: str, **kwargs) -> List[dict]:
        """
        Run security scans based on scan type
        
        Args:
            scan_type: Type of scan to run
            path: Path to scan
            **kwargs: Additional scanner-specific arguments
        """
        if scan_type == "full":
            return self._run_full_scan(path, **kwargs)
        elif scan_type == "basic":
            return self._run_basic_scan(path, **kwargs)
        elif scan_type == "advanced":
            return self._run_advanced_scan(path, **kwargs)
        elif scan_type in self.all_scanners:
            return self._run_single_scanner(scan_type, path, **kwargs)
        else:
            raise ValueError(f"Unknown scan type: {scan_type}")

    def _run_full_scan(self, path: str, **kwargs) -> List[dict]:
        """Run all available scanners"""
        results = []
        parallel_execution = kwargs.get('parallel', True)
        
        if parallel_execution:
            results = self._run_scanners_parallel(self.all_scanners, path, **kwargs)
        else:
            results = self._run_scanners_sequential(self.all_scanners, path, **kwargs)
            
        return results

    def _run_basic_scan(self, path: str, **kwargs) -> List[dict]:
        """Run basic scanners (Bandit, pip-audit, secret scanner)"""
        parallel_execution = kwargs.get('parallel', True)
        
        if parallel_execution:
            return self._run_scanners_parallel(self.basic_scanners, path, **kwargs)
        else:
            return self._run_scanners_sequential(self.basic_scanners, path, **kwargs)

    def _run_advanced_scan(self, path: str, **kwargs) -> List[dict]:
        """Run advanced scanners (Snyk, Trivy, Semgrep)"""
        parallel_execution = kwargs.get('parallel', True)
        
        if parallel_execution:
            return self._run_scanners_parallel(self.advanced_scanners, path, **kwargs)
        else:
            return self._run_scanners_sequential(self.advanced_scanners, path, **kwargs)

    def _run_single_scanner(self, scanner_name: str, path: str, **kwargs) -> List[dict]:
        """Run a single scanner with custom parameters"""
        scanner = self.all_scanners[scanner_name]
        
        # Handle scanner-specific parameters
        if scanner_name == "snyk":
            scan_type = kwargs.get('snyk_scan_type', 'all')
            results = scanner.scan(path, scan_type)
        elif scanner_name == "trivy":
            target_type = kwargs.get('trivy_target_type', 'fs')
            image_name = kwargs.get('image_name')
            results = scanner.scan(path, target_type, image_name)
        elif scanner_name == "semgrep":
            config = kwargs.get('semgrep_config')
            exclude_patterns = kwargs.get('exclude_patterns')
            language = kwargs.get('language')
            
            if language:
                results = scanner.scan_specific_language(path, language, exclude_patterns)
            else:
                results = scanner.scan(path, config, exclude_patterns)
        else:
            results = scanner.scan(path)
            
        # Add scanner metadata
        for result in results:
            result["scanner_type"] = scanner_name
            result["scan_timestamp"] = kwargs.get('timestamp')
            
        return results

    def _run_scanners_parallel(self, scanners: Dict, path: str, **kwargs) -> List[dict]:
        """Run scanners in parallel using ThreadPoolExecutor"""
        results = []
        max_workers = kwargs.get('max_workers', min(len(scanners), 4))
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_scanner = {
                executor.submit(self._run_single_scanner, name, path, **kwargs): name
                for name in scanners.keys()
            }
            
            for future in concurrent.futures.as_completed(future_to_scanner):
                scanner_name = future_to_scanner[future]
                try:
                    scanner_results = future.result(timeout=kwargs.get('scanner_timeout', 600))
                    results.extend(scanner_results)
                    print(f"✅ {scanner_name} scan completed")
                except Exception as e:
                    print(f"❌ {scanner_name} scan failed: {e}")
                    
        return results

    def _run_scanners_sequential(self, scanners: Dict, path: str, **kwargs) -> List[dict]:
        """Run scanners sequentially"""
        results = []
        
        for scanner_name in scanners.keys():
            try:
                print(f"🔍 Running {scanner_name} scan...")
                scanner_results = self._run_single_scanner(scanner_name, path, **kwargs)
                results.extend(scanner_results)
                print(f"✅ {scanner_name} scan completed with {len(scanner_results)} findings")
            except Exception as e:
                print(f"❌ {scanner_name} scan failed: {e}")
                
        return results

    def get_available_scanners(self) -> Dict[str, List[str]]:
        """Get available scanners grouped by category"""
        return {
            "basic": list(self.basic_scanners.keys()),
            "advanced": list(self.advanced_scanners.keys()),
            "scan_types": ["basic", "advanced", "full"] + list(self.all_scanners.keys())
        }

    def get_scanner_info(self, scanner_name: str) -> Dict:
        """Get information about a specific scanner"""
        scanner_info = {
            "sast": {
                "name": "Bandit",
                "description": "Python security linter for common security issues",
                "language": "Python",
                "type": "SAST"
            },
            "dependency": {
                "name": "pip-audit", 
                "description": "Python package vulnerability scanner",
                "language": "Python",
                "type": "Dependency"
            },
            "secret": {
                "name": "Secret Scanner",
                "description": "Custom secret detection scanner",
                "language": "All",
                "type": "Secret"
            },
            "snyk": {
                "name": "Snyk",
                "description": "Commercial security platform for code, dependencies, containers, and IaC",
                "language": "Multiple",
                "type": "Multi-purpose"
            },
            "trivy": {
                "name": "Trivy",
                "description": "Comprehensive vulnerability scanner for containers and filesystems",
                "language": "Multiple", 
                "type": "Multi-purpose"
            },
            "semgrep": {
                "name": "Semgrep",
                "description": "Advanced SAST tool with custom rule support",
                "language": "Multiple",
                "type": "SAST"
            }
        }
        
        return scanner_info.get(scanner_name, {})

    def check_scanner_availability(self) -> Dict[str, bool]:
        """Check which scanners are available on the system"""
        availability = {}
        
        # Check basic scanners
        for name in self.basic_scanners.keys():
            availability[name] = True  # These are always available
            
        # Check advanced scanners by trying to run them
        try:
            import subprocess
            
            # Check Snyk
            try:
                subprocess.run(["snyk", "--version"], capture_output=True, timeout=10)
                availability["snyk"] = True
            except:
                availability["snyk"] = False
                
            # Check Trivy
            try:
                subprocess.run(["trivy", "--version"], capture_output=True, timeout=10)
                availability["trivy"] = True
            except:
                availability["trivy"] = False
                
            # Check Semgrep
            try:
                subprocess.run(["semgrep", "--version"], capture_output=True, timeout=10)
                availability["semgrep"] = True
            except:
                availability["semgrep"] = False
                
        except Exception as e:
            print(f"Error checking scanner availability: {e}")
            
        return availability

    def get_scan_recommendations(self, path: str) -> Dict[str, List[str]]:
        """Get scanner recommendations based on project characteristics"""
        recommendations = {
            "recommended": [],
            "optional": [],
            "reasons": []
        }
        
        # Always recommend basic scanners
        recommendations["recommended"].extend(["secret", "dependency"])
        
        # Check for specific file types and technologies
        if self._has_python_files(path):
            recommendations["recommended"].append("sast")  # Bandit
            recommendations["recommended"].append("semgrep")
            recommendations["reasons"].append("Python files detected")
            
        if self._has_dockerfile(path):
            recommendations["recommended"].extend(["trivy", "snyk"])
            recommendations["reasons"].append("Dockerfile detected")
            
        if self._has_package_files(path):
            recommendations["recommended"].extend(["snyk", "trivy"])
            recommendations["reasons"].append("Package files detected")
            
        if self._has_iac_files(path):
            recommendations["recommended"].extend(["trivy", "semgrep"])
            recommendations["reasons"].append("Infrastructure as Code files detected")
            
        # Remove duplicates
        recommendations["recommended"] = list(set(recommendations["recommended"]))
        
        return recommendations

    def _has_python_files(self, path: str) -> bool:
        """Check if path contains Python files"""
        for root, dirs, files in os.walk(path):
            if any(f.endswith('.py') for f in files):
                return True
        return False

    def _has_dockerfile(self, path: str) -> bool:
        """Check if path contains Dockerfile"""
        dockerfile_names = ['Dockerfile', 'dockerfile', 'Dockerfile.dev', 'Dockerfile.prod']
        for root, dirs, files in os.walk(path):
            if any(f in dockerfile_names for f in files):
                return True
        return False

    def _has_package_files(self, path: str) -> bool:
        """Check if path contains package files"""
        package_files = [
            'requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile',
            'package.json', 'yarn.lock', 'pom.xml', 'build.gradle',
            'go.mod', 'Cargo.toml', 'composer.json'
        ]
        for root, dirs, files in os.walk(path):
            if any(f in package_files for f in files):
                return True
        return False

    def _has_iac_files(self, path: str) -> bool:
        """Check if path contains Infrastructure as Code files"""
        iac_extensions = ['.tf', '.yml', '.yaml']
        iac_patterns = ['terraform', 'kubernetes', 'k8s', 'helm', 'ansible']
        
        for root, dirs, files in os.walk(path):
            # Check file extensions
            if any(any(f.endswith(ext) for ext in iac_extensions) for f in files):
                return True
            # Check directory names
            if any(any(pattern in d.lower() for pattern in iac_patterns) for d in dirs):
                return True
                
        return False


import subprocess
import json
import os
from typing import List, Dict, Optional
from .base import Scanner

class SemgrepScanner(Scanner):
    """
    Semgrep scanner for advanced Static Application Security Testing (SAST).
    Supports custom rules and multiple programming languages.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.default_rulesets = [
            "p/security-audit",
            "p/owasp-top-ten", 
            "p/cwe-top-25",
            "p/secrets",
            "p/dockerfile",
            "p/kubernetes"
        ]
        
    def scan(self, path: str, config: Optional[str] = None, exclude_patterns: Optional[List[str]] = None) -> List[dict]:
        """
        Scan for security issues using Semgrep
        
        Args:
            path: Path to scan
            config: Semgrep config/ruleset to use (defaults to security-focused rulesets)
            exclude_patterns: List of patterns to exclude from scanning
        """
        if not os.path.exists(path):
            print(f"Path does not exist: {path}")
            return []
            
        vulnerabilities = []
        config_to_use = config or self.config_path
        
        if config_to_use:
            # Use specific config
            vulnerabilities.extend(self._scan_with_config(path, config_to_use, exclude_patterns))
        else:
            # Use default security rulesets
            for ruleset in self.default_rulesets:
                vulnerabilities.extend(self._scan_with_config(path, ruleset, exclude_patterns))
                
        return vulnerabilities
    
    def _scan_with_config(self, path: str, config: str, exclude_patterns: Optional[List[str]] = None) -> List[dict]:
        """Scan with a specific Semgrep config/ruleset"""
        try:
            cmd = [
                "semgrep",
                "--config", config,
                "--json",
                "--verbose",
                "--timeout", "300",
                "--max-memory", "2000"
            ]
            
            # Add exclude patterns
            if exclude_patterns:
                for pattern in exclude_patterns:
                    cmd.extend(["--exclude", pattern])
            else:
                # Default exclusions
                default_excludes = [
                    "*.min.js",
                    "*.min.css", 
                    "node_modules/",
                    ".git/",
                    "__pycache__/",
                    ".venv/",
                    "venv/",
                    "vendor/",
                    "*.log"
                ]
                for pattern in default_excludes:
                    cmd.extend(["--exclude", pattern])
            
            cmd.append(path)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=400  # Slightly longer than semgrep timeout
            )
            
            # Semgrep returns exit code 1 when findings are present
            if result.returncode not in [0, 1]:
                print(f"Semgrep scan failed with config {config}: {result.stderr}")
                return []
                
            if result.stdout:
                data = json.loads(result.stdout)
                return self._parse_semgrep_results(data, config)
                
        except subprocess.TimeoutExpired:
            print(f"Semgrep scan timed out with config {config}")
        except json.JSONDecodeError as e:
            print(f"Error parsing Semgrep output for config {config}: {e}")
        except FileNotFoundError:
            print("Semgrep not found. Please install it: pip install semgrep")
        except Exception as e:
            print(f"Error running Semgrep scan with config {config}: {e}")
            
        return []
    
    def scan_with_custom_rules(self, path: str, rules_path: str, exclude_patterns: Optional[List[str]] = None) -> List[dict]:
        """Scan with custom Semgrep rules from a local file or directory"""
        if not os.path.exists(rules_path):
            print(f"Custom rules path does not exist: {rules_path}")
            return []
            
        return self._scan_with_config(path, rules_path, exclude_patterns)
    
    def scan_specific_language(self, path: str, language: str, exclude_patterns: Optional[List[str]] = None) -> List[dict]:
        """Scan for language-specific security issues"""
        language_configs = {
            "python": ["p/python", "p/bandit", "p/django", "p/flask"],
            "javascript": ["p/javascript", "p/nodejs", "p/react", "p/express"],
            "typescript": ["p/typescript", "p/nodejs", "p/react"],
            "java": ["p/java", "p/spring", "p/android"],
            "go": ["p/golang", "p/gosec"],
            "php": ["p/php", "p/laravel", "p/symfony"],
            "ruby": ["p/ruby", "p/rails"],
            "csharp": ["p/csharp", "p/dotnet"],
            "cpp": ["p/cpp", "p/c"],
            "rust": ["p/rust"],
            "kotlin": ["p/kotlin", "p/android"],
            "swift": ["p/swift"],
            "terraform": ["p/terraform", "p/hashicorp"],
            "dockerfile": ["p/dockerfile"],
            "kubernetes": ["p/kubernetes"]
        }
        
        configs = language_configs.get(language.lower(), [])
        if not configs:
            print(f"No specific configs found for language: {language}")
            return []
            
        vulnerabilities = []
        for config in configs:
            vulnerabilities.extend(self._scan_with_config(path, config, exclude_patterns))
            
        return vulnerabilities
    
    def _parse_semgrep_results(self, data: Dict, config: str) -> List[dict]:
        """Parse Semgrep JSON output into standardized vulnerability format"""
        vulnerabilities = []
        
        results = data.get('results', [])
        
        for result in results:
            # Extract location information
            start = result.get('start', {})
            end = result.get('end', {})
            
            vulnerability = {
                "type": "semgrep_finding",
                "scanner": "semgrep",
                "config": config,
                "rule_id": result.get('check_id', 'unknown'),
                "message": result.get('message', ''),
                "severity": self._normalize_severity(result.get('metadata', {}).get('severity', 'info')),
                "confidence": self._normalize_confidence(result.get('metadata', {}).get('confidence', 'medium')),
                "file_path": result.get('path', ''),
                "start_line": start.get('line', 0),
                "start_col": start.get('col', 0),
                "end_line": end.get('line', 0), 
                "end_col": end.get('col', 0),
                "code_snippet": result.get('extra', {}).get('lines', ''),
                "fix_suggestions": result.get('extra', {}).get('fix', ''),
                
                # Metadata from rule
                "category": result.get('metadata', {}).get('category', ''),
                "subcategory": result.get('metadata', {}).get('subcategory', ''),
                "cwe": result.get('metadata', {}).get('cwe', []),
                "owasp": result.get('metadata', {}).get('owasp', []),
                "asvs": result.get('metadata', {}).get('asvs', {}),
                "technology": result.get('metadata', {}).get('technology', []),
                "license": result.get('metadata', {}).get('license', ''),
                "vulnerability_class": result.get('metadata', {}).get('vulnerability_class', []),
                "impact": result.get('metadata', {}).get('impact', ''),
                "likelihood": result.get('metadata', {}).get('likelihood', ''),
                
                # References and documentation
                "references": result.get('metadata', {}).get('references', []),
                "semgrep_url": result.get('metadata', {}).get('semgrep.url', ''),
                
                # Additional context
                "languages": result.get('metadata', {}).get('languages', []),
                "source": result.get('metadata', {}).get('source', ''),
                "shortlink": result.get('metadata', {}).get('shortlink', ''),
                
                # Engine details
                "is_blocking": result.get('extra', {}).get('is_blocking', False),
                "fingerprint": result.get('extra', {}).get('fingerprint', ''),
                "fix_regex": result.get('extra', {}).get('fix_regex', {}),
                "dependency_match_only": result.get('extra', {}).get('dependency_match_only', False)
            }
            
            vulnerabilities.append(vulnerability)
            
        return vulnerabilities
    
    def _normalize_severity(self, severity: str) -> str:
        """Normalize severity levels to standard format"""
        severity_map = {
            'error': 'HIGH',
            'warning': 'MEDIUM',
            'info': 'LOW',
            'critical': 'CRITICAL',
            'high': 'HIGH',
            'medium': 'MEDIUM',
            'low': 'LOW'
        }
        return severity_map.get(severity.lower(), 'INFO')
    
    def _normalize_confidence(self, confidence: str) -> str:
        """Normalize confidence levels"""
        confidence_map = {
            'high': 'HIGH',
            'medium': 'MEDIUM', 
            'low': 'LOW'
        }
        return confidence_map.get(confidence.lower(), 'MEDIUM')
    
    def get_available_rulesets(self) -> List[str]:
        """Get list of available Semgrep rulesets"""
        try:
            result = subprocess.run(
                ["semgrep", "--list-configs"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout.strip().split('\n')
                
        except Exception as e:
            print(f"Error getting available rulesets: {e}")
            
        return self.default_rulesets
    
    def validate_rules(self, rules_path: str) -> bool:
        """Validate custom Semgrep rules"""
        try:
            result = subprocess.run(
                ["semgrep", "--validate", "--config", rules_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error validating rules: {e}")
            return False
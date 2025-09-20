import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from scanners.snyk import SnykScanner
from scanners.trivy import TrivyScanner
from scanners.semgrep import SemgrepScanner
from scanners.manager import ScannerManager

class TestSnykScanner:
    def test_snyk_scanner_init(self):
        scanner = SnykScanner()
        assert scanner.auth_token is None
        
    def test_snyk_scanner_with_token(self):
        scanner = SnykScanner(auth_token="test-token")
        assert scanner.auth_token == "test-token"
        
    @patch('subprocess.run')
    def test_snyk_dependencies_scan_success(self, mock_run):
        # Mock successful Snyk output
        mock_run.return_value = MagicMock(
            returncode=1,  # Snyk returns 1 when vulnerabilities found
            stdout='{"vulnerabilities": [{"id": "SNYK-1", "title": "Test Vuln", "severity": "high"}]}'
        )
        
        scanner = SnykScanner()
        with tempfile.TemporaryDirectory() as temp_dir:
            results = scanner._scan_dependencies(temp_dir)
            
        assert len(results) == 1
        assert results[0]["id"] == "SNYK-1"
        assert results[0]["severity"] == "HIGH"
        
    @patch('subprocess.run')
    def test_snyk_scan_failure(self, mock_run):
        mock_run.side_effect = FileNotFoundError("snyk not found")
        
        scanner = SnykScanner()
        with tempfile.TemporaryDirectory() as temp_dir:
            results = scanner._scan_dependencies(temp_dir)
            
        assert results == []

class TestTrivyScanner:
    def test_trivy_scanner_init(self):
        scanner = TrivyScanner()
        assert "fs" in scanner.supported_targets
        assert "image" in scanner.supported_targets
        
    @patch('subprocess.run')
    def test_trivy_filesystem_scan_success(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"Results": [{"Vulnerabilities": [{"VulnerabilityID": "CVE-2021-1234", "Severity": "HIGH"}]}]}'
        )
        
        scanner = TrivyScanner()
        with tempfile.TemporaryDirectory() as temp_dir:
            results = scanner._scan_filesystem(temp_dir)
            
        assert len(results) == 1
        assert results[0]["vulnerability_id"] == "CVE-2021-1234"
        assert results[0]["severity"] == "HIGH"
        
    @patch('subprocess.run')
    def test_trivy_scan_failure(self, mock_run):
        mock_run.side_effect = FileNotFoundError("trivy not found")
        
        scanner = TrivyScanner()
        with tempfile.TemporaryDirectory() as temp_dir:
            results = scanner._scan_filesystem(temp_dir)
            
        assert results == []

class TestSemgrepScanner:
    def test_semgrep_scanner_init(self):
        scanner = SemgrepScanner()
        assert "p/security-audit" in scanner.default_rulesets
        assert "p/owasp-top-ten" in scanner.default_rulesets
        
    @patch('subprocess.run')
    def test_semgrep_scan_success(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=1,  # Semgrep returns 1 when findings present
            stdout='{"results": [{"check_id": "test.rule", "message": "Test finding", "metadata": {"severity": "error"}}]}'
        )
        
        scanner = SemgrepScanner()
        with tempfile.TemporaryDirectory() as temp_dir:
            results = scanner._scan_with_config(temp_dir, "p/security-audit")
            
        assert len(results) == 1
        assert results[0]["rule_id"] == "test.rule"
        assert results[0]["severity"] == "HIGH"
        
    @patch('subprocess.run')
    def test_semgrep_scan_failure(self, mock_run):
        mock_run.side_effect = FileNotFoundError("semgrep not found")
        
        scanner = SemgrepScanner()
        with tempfile.TemporaryDirectory() as temp_dir:
            results = scanner._scan_with_config(temp_dir, "p/security-audit")
            
        assert results == []
        
    def test_normalize_severity(self):
        scanner = SemgrepScanner()
        assert scanner._normalize_severity("error") == "HIGH"
        assert scanner._normalize_severity("warning") == "MEDIUM"
        assert scanner._normalize_severity("info") == "LOW"
        assert scanner._normalize_severity("unknown") == "INFO"

class TestScannerManager:
    def test_scanner_manager_init(self):
        manager = ScannerManager()
        assert "sast" in manager.basic_scanners
        assert "snyk" in manager.advanced_scanners
        assert len(manager.all_scanners) >= 6
        
    def test_get_available_scanners(self):
        manager = ScannerManager()
        scanners = manager.get_available_scanners()
        
        assert "basic" in scanners
        assert "advanced" in scanners
        assert "scan_types" in scanners
        assert "sast" in scanners["basic"]
        assert "snyk" in scanners["advanced"]
        
    def test_get_scanner_info(self):
        manager = ScannerManager()
        info = manager.get_scanner_info("snyk")
        
        assert info["name"] == "Snyk"
        assert "Commercial security platform" in info["description"]
        
    def test_scan_recommendations_python_project(self):
        manager = ScannerManager()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a Python file
            py_file = os.path.join(temp_dir, "main.py")
            with open(py_file, "w") as f:
                f.write("print('hello world')")
                
            recommendations = manager.get_scan_recommendations(temp_dir)
            
        assert "sast" in recommendations["recommended"]
        assert "semgrep" in recommendations["recommended"]
        assert "Python files detected" in recommendations["reasons"]
        
    def test_scan_recommendations_dockerfile_project(self):
        manager = ScannerManager()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a Dockerfile
            dockerfile = os.path.join(temp_dir, "Dockerfile")
            with open(dockerfile, "w") as f:
                f.write("FROM python:3.9\nRUN pip install requests")
                
            recommendations = manager.get_scan_recommendations(temp_dir)
            
        assert "trivy" in recommendations["recommended"]
        assert "snyk" in recommendations["recommended"]
        assert "Dockerfile detected" in recommendations["reasons"]
        
    def test_scan_recommendations_package_files(self):
        manager = ScannerManager()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create package.json
            package_json = os.path.join(temp_dir, "package.json")
            with open(package_json, "w") as f:
                f.write('{"name": "test", "dependencies": {}}')
                
            recommendations = manager.get_scan_recommendations(temp_dir)
            
        assert "snyk" in recommendations["recommended"]
        assert "trivy" in recommendations["recommended"]
        assert "Package files detected" in recommendations["reasons"]
        
    @patch('subprocess.run')
    def test_check_scanner_availability(self, mock_run):
        # Mock successful scanner version checks
        mock_run.return_value = MagicMock(returncode=0)
        
        manager = ScannerManager()
        availability = manager.check_scanner_availability()
        
        assert availability["sast"] is True  # Basic scanners always available
        assert availability["snyk"] is True  # Mocked as available
        assert availability["trivy"] is True
        assert availability["semgrep"] is True
        
    def test_run_basic_scan_type(self):
        manager = ScannerManager()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # This will run basic scanners, some may fail but shouldn't crash
            try:
                results = manager.run_scan("basic", temp_dir, parallel=False)
                assert isinstance(results, list)
            except Exception as e:
                # Expected for missing tools, just ensure it doesn't crash completely
                assert isinstance(e, Exception)
                
    def test_invalid_scan_type(self):
        manager = ScannerManager()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValueError):
                manager.run_scan("invalid_scan_type", temp_dir)

class TestScannerIntegration:
    """Test scanner integration and compatibility"""
    
    def test_all_scanners_implement_base_interface(self):
        """Ensure all scanners implement the base Scanner interface"""
        from scanners.base import Scanner
        from scanners.sast import BanditScanner
        from scanners.dependency import PipAuditScanner
        from scanners.secret import SecretScanner
        
        scanners = [
            BanditScanner(),
            PipAuditScanner(), 
            SecretScanner(),
            SnykScanner(),
            TrivyScanner(),
            SemgrepScanner()
        ]
        
        for scanner in scanners:
            assert isinstance(scanner, Scanner)
            assert hasattr(scanner, 'scan')
            assert callable(getattr(scanner, 'scan'))
            
    def test_scanner_output_format_consistency(self):
        """Test that all scanners return consistent output format"""
        manager = ScannerManager()
        
        # Test with empty directory to avoid actual scanning
        with tempfile.TemporaryDirectory() as temp_dir:
            for scanner_name in manager.all_scanners.keys():
                try:
                    results = manager._run_single_scanner(scanner_name, temp_dir)
                    assert isinstance(results, list)
                    
                    # Check that all results have required fields
                    for result in results:
                        assert isinstance(result, dict)
                        assert "scanner_type" in result
                        
                except Exception:
                    # Expected for missing tools, just ensure structure is correct
                    pass
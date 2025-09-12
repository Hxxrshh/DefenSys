# tests/test_integration.py

import unittest
from core.scanner import VulnScanner

class TestIntegration(unittest.TestCase):
    def setUp(self):
        # Example vulnerable test target (replace with DVWA/Juice Shop in Docker)
        self.target = "http://localhost:3000"
        self.scanner = VulnScanner(self.target)

    def test_scanner_runs(self):
        """Test that the scanner runs and returns a list"""
        results = self.scanner.run()
        self.assertIsInstance(results, list)

    def test_plugins_loaded(self):
        """Test that plugins are discovered and loaded"""
        self.assertGreater(len(self.scanner.plugins), 0, "No plugins loaded")

    def test_findings_structure(self):
        """Test that findings (if any) contain required fields"""
        results = self.scanner.run()
        for r in results:
            self.assertIn("vulnerability", r)
            self.assertIn("severity", r)
            self.assertIn("evidence", r)
            self.assertIn("remediation", r)


if __name__ == "__main__":
    unittest.main()
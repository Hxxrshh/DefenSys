# tests/test_scanner.py

import unittest
from core.scanner import VulnScanner

class TestScanner(unittest.TestCase):
    def setUp(self):
        self.target = "http://example.com"  # Replace with test environment like DVWA/JuiceShop later
        self.scanner = VulnScanner(self.target)

    def test_scanner_initialization(self):
        self.assertEqual(self.scanner.target, self.target)
        self.assertIsInstance(self.scanner.plugins, dict)

    def test_plugins_are_loaded(self):
        self.assertGreater(len(self.scanner.plugins), 0, "No plugins loaded by scanner")

    def test_scanner_run_returns_list(self):
        results = self.scanner.run()
        self.assertIsInstance(results, list)

    def test_findings_have_required_fields(self):
        results = self.scanner.run()
        for r in results:
            self.assertIn("vulnerability", r)
            self.assertIn("severity", r)
            self.assertIn("evidence", r)
            self.assertIn("remediation", r)


if __name__ == "__main__":
    unittest.main()
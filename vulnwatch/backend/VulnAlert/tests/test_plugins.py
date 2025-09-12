# tests/test_plugins.py

import unittest
from core.plugins import sql_injection, xss, csrf, headers, cookies, directory_exposure

class TestPlugins(unittest.TestCase):
    def setUp(self):
        self.target = "http://example.com"  # Replace with test environment later

    def test_sql_injection_plugin(self):
        plugin = sql_injection.Plugin()
        result = plugin.run(self.target)
        self.assertTrue(result is None or "vulnerability" in result)

    def test_xss_plugin(self):
        plugin = xss.Plugin()
        result = plugin.run(self.target)
        self.assertTrue(result is None or "vulnerability" in result)

    def test_csrf_plugin(self):
        plugin = csrf.Plugin()
        result = plugin.run(self.target)
        self.assertTrue(result is None or "vulnerability" in result)

    def test_headers_plugin(self):
        plugin = headers.Plugin()
        result = plugin.run(self.target)
        self.assertTrue(result is None or "vulnerability" in result)

    def test_cookies_plugin(self):
        plugin = cookies.Plugin()
        result = plugin.run(self.target)
        self.assertTrue(result is None or "vulnerability" in result)

    def test_directory_exposure_plugin(self):
        plugin = directory_exposure.Plugin()
        result = plugin.run(self.target)
        self.assertTrue(result is None or "vulnerability" in result)


if __name__ == "__main__":
    unittest.main()
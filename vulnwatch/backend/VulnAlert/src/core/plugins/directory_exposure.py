# src/core/plugins/directory_exposure.py

from utils.payloads import DIR_TRAVERSAL_PAYLOADS
import requests

class Plugin:
    name = "Directory and File Exposure"
    description = "Checks for directory listing and file traversal vulnerabilities"

    def run(self, target_url):
        try:
            issues = []

            # Check for directory listing (basic check for index of)
            resp = requests.get(target_url)
            if "Index of /" in resp.text or "Directory listing" in resp.text:
                issues.append("Directory listing enabled")

            # Check for path traversal attempts
            for payload in DIR_TRAVERSAL_PAYLOADS:
                test_url = f"{target_url}/{payload}"
                r = requests.get(test_url)
                if "root:x:" in r.text or "[extensions]" in r.text.lower():
                    return {
                        "vulnerability": self.name,
                        "severity": "High",
                        "evidence": f"Payload {payload} exposed sensitive file contents",
                        "remediation": "Disable directory listing and validate user inputs to prevent path traversal"
                    }

            if issues:
                return {
                    "vulnerability": self.name,
                    "severity": "Medium",
                    "evidence": ", ".join(issues),
                    "remediation": "Disable autoindexing and restrict file access"
                }

            return None
        except Exception as e:
            print(f"[!] Directory exposure check failed: {e}")
            return None


# Example usage
if __name__ == "__main__":
    plugin = Plugin()
    result = plugin.run("http://example.com")
    print(result)
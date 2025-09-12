# src/core/plugins/xss.py

from utils.payloads import XSS_PAYLOADS
import requests

class Plugin:
    name = "Cross-Site Scripting (XSS)"
    description = "Checks for reflected XSS vulnerabilities using common payloads"

    def run(self, target_url):
        try:
            for payload in XSS_PAYLOADS:
                test_url = f"{target_url}?q={payload}"
                response = requests.get(test_url)

                # If the payload is reflected back in the response body
                if payload.lower() in response.text.lower():
                    return {
                        "vulnerability": self.name,
                        "severity": "Medium",
                        "evidence": f"Payload {payload} reflected in response",
                        "remediation": "Sanitize and escape user inputs, implement CSP"
                    }

            return None
        except Exception as e:
            print(f"[!] XSS check failed: {e}")
            return None


# Example usage
if __name__ == "__main__":
    plugin = Plugin()
    result = plugin.run("http://example.com/search")
    print(result)
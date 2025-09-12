# src/core/plugins/csrf.py

from utils.payloads import CSRF_TOKENS
import requests

class Plugin:
    name = "Cross-Site Request Forgery (CSRF)"
    description = "Checks for presence of CSRF protection tokens in forms"

    def run(self, target_url):
        try:
            response = requests.get(target_url)
            html = response.text.lower()

            # Check if any known CSRF tokens appear in the form
            token_found = any(token.lower() in html for token in CSRF_TOKENS)

            if not token_found:
                return {
                    "vulnerability": self.name,
                    "severity": "High",
                    "evidence": "No CSRF tokens detected in forms",
                    "remediation": "Include unique anti-CSRF tokens in forms and validate them server-side"
                }

            return None
        except Exception as e:
            print(f"[!] CSRF check failed: {e}")
            return None


# Example usage
if __name__ == "__main__":
    plugin = Plugin()
    result = plugin.run("http://example.com")
    print(result)

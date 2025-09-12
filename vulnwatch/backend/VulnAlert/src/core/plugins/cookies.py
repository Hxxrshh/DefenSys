# src/core/plugins/cookies.py

from http import cookies as http_cookies

class Plugin:
    name = "Insecure Cookie Flags"
    description = "Checks for missing Secure, HttpOnly, or SameSite cookie flags"

    def run(self, target_url):
        import requests
        try:
            response = requests.get(target_url)
            if "set-cookie" not in response.headers:
                return None

            issues = []
            cookies = response.headers.get("set-cookie")

            # Simple checks for cookie flags
            if "Secure" not in cookies:
                issues.append("Missing Secure flag")
            if "HttpOnly" not in cookies:
                issues.append("Missing HttpOnly flag")
            if "SameSite" not in cookies:
                issues.append("Missing SameSite attribute")

            if issues:
                return {
                    "vulnerability": self.name,
                    "severity": "Medium",
                    "evidence": f"Cookies set without: {', '.join(issues)}",
                    "remediation": "Set Secure, HttpOnly, and SameSite flags for cookies"
                }

            return None
        except Exception as e:
            print(f"[!] Cookie check failed: {e}")
            return None


# Example usage
if __name__ == "__main__":
    plugin = Plugin()
    result = plugin.run("http://example.com")
    print(result)
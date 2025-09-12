# src/core/plugins/headers.py

import requests

class Plugin:
    name = "Missing Security Headers"
    description = "Checks for missing HTTP security headers (HSTS, CSP, X-Frame-Options)"

    REQUIRED_HEADERS = [
        ("Strict-Transport-Security", "High", "Enable HSTS to enforce secure connections"),
        ("Content-Security-Policy", "High", "Define a CSP to mitigate XSS and data injection"),
        ("X-Frame-Options", "Medium", "Use DENY or SAMEORIGIN to prevent clickjacking"),
        ("X-Content-Type-Options", "Low", "Set to 'nosniff' to prevent MIME sniffing")
    ]

    def run(self, target_url):
        try:
            response = requests.get(target_url)
            issues = []

            for header, severity, remediation in self.REQUIRED_HEADERS:
                if header not in response.headers:
                    issues.append({
                        "vulnerability": self.name,
                        "severity": severity,
                        "evidence": f"Missing header: {header}",
                        "remediation": remediation
                    })

            if issues:
                # Return the first issue if multiple found (scanner already collects all findings)
                return issues[0]
            return None

        except Exception as e:
            print(f"[!] Header check failed: {e}")
            return None


# Example usage
if __name__ == "__main__":
    plugin = Plugin()
    result = plugin.run("http://example.com")
    print(result)
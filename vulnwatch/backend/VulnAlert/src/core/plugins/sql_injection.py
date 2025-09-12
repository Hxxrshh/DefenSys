# src/core/plugins/sql_injection.py

from utils.payloads import SQLI_PAYLOADS
import requests

class Plugin:
    name = "SQL Injection"
    description = "Checks for SQL Injection vulnerabilities using common payloads"

    def run(self, target_url):
        try:
            for payload in SQLI_PAYLOADS:
                # Append payload as query parameter "id"
                test_url = f"{target_url}?id={payload}"
                response = requests.get(test_url)

                # Basic error-based SQLi detection
                sql_errors = [
                    "you have an error in your sql syntax",
                    "unclosed quotation mark",
                    "quoted string not properly terminated",
                    "mysql_fetch",
                    "sqlstate"
                ]

                if any(err in response.text.lower() for err in sql_errors):
                    return {
                        "vulnerability": self.name,
                        "severity": "High",
                        "evidence": f"Payload {payload} triggered SQL error",
                        "remediation": "Use parameterized queries (prepared statements) and ORM frameworks"
                    }

            return None
        except Exception as e:
            print(f"[!] SQL Injection check failed: {e}")
            return None


# Example usage
if __name__ == "__main__":
    plugin = Plugin()
    result = plugin.run("http://example.com/product")
    print(result)
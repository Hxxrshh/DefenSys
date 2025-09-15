# src/core/reporter.py

from core.alerts import AlertManager
from core.db import DatabaseManager

class Reporter:
    """
    Reporter integrates alerts and database for generating reports.
    """

    def __init__(self, db_path="defensys.db"):
        self.alert_manager = AlertManager()
        self.db = DatabaseManager(db_path)

    def log_finding(self, target, vulnerability, severity, evidence, remediation):
        # Store in alerts manager
        self.alert_manager.add_alert(vulnerability, severity, evidence, remediation)
        # Store in database
        self.db.insert_alert(target, vulnerability, severity, evidence, remediation)

    def generate_json_report(self):
        return self.alert_manager.to_json()

    def generate_html_report(self):
        return self.alert_manager.to_html()

    def fetch_all_db_records(self, target=None):
        return self.db.fetch_alerts(target)


# Example usage
if __name__ == "__main__":
    reporter = Reporter()
    reporter.log_finding(
        "http://localhost:3000",
        "Cross-Site Scripting",
        "Medium",
        "<script>alert(1)</script> reflected in response",
        "Sanitize user inputs with escaping"
    )
    print("[JSON Report]\n", reporter.generate_json_report())
    print("\n[HTML Report]\n", reporter.generate_html_report())
    print("\n[DB Records]\n", reporter.fetch_all_db_records())
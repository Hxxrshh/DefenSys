# src/core/db.py

import sqlite3
from datetime import datetime

DB_NAME = "vulnalert.db"

class DatabaseManager:
    """
    SQLite manager for storing vulnerability scan results.
    """

    def __init__(self, db_path=DB_NAME):
        self.db_path = db_path
        self._create_table()

    def _create_table(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                target TEXT NOT NULL,
                vulnerability TEXT NOT NULL,
                severity TEXT NOT NULL,
                evidence TEXT,
                remediation TEXT
            )
            """
        )
        conn.commit()
        conn.close()

    def insert_alert(self, target, vulnerability, severity, evidence, remediation):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO alerts (timestamp, target, vulnerability, severity, evidence, remediation)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (datetime.utcnow().isoformat() + "Z", target, vulnerability, severity, evidence, remediation)
        )
        conn.commit()
        conn.close()

    def fetch_alerts(self, target=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if target:
            cursor.execute("SELECT * FROM alerts WHERE target=?", (target,))
        else:
            cursor.execute("SELECT * FROM alerts")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def clear_alerts(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM alerts")
        conn.commit()
        conn.close()


# Example usage
if __name__ == "__main__":
    db = DatabaseManager()
    db.insert_alert(
        "http://localhost:3000",
        "SQL Injection",
        "High",
        "Payload ' OR '1'='1 triggered error",
        "Use parameterized queries"
    )
    print("[DB Alerts]", db.fetch_alerts())
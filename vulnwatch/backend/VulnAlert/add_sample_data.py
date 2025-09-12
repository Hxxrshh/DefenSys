#!/usr/bin/env python3

import sys
import os
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, '/app/src')

from server import app, db, Threat, Log

def add_sample_data():
    """Add sample data to the database."""
    with app.app_context():
        print("Adding sample data...")
        
        # Add sample threats
        threats = [
            Threat(
                package="django",
                cve_id="CVE-2024-0001",
                severity="CRITICAL",
                description="SQL injection vulnerability in Django ORM"
            ),
            Threat(
                package="requests",
                cve_id="CVE-2024-0002", 
                severity="HIGH",
                description="Remote code execution in requests library"
            ),
            Threat(
                package="flask",
                cve_id="CVE-2024-0003",
                severity="MEDIUM", 
                description="Cross-site scripting vulnerability in Flask templates"
            ),
            Threat(
                package="numpy",
                cve_id="CVE-2024-0004",
                severity="LOW",
                description="Buffer overflow in numpy array processing"
            )
        ]
        
        # Add sample logs
        logs = [
            Log(
                service="auth-service",
                level="ERROR",
                message="Failed authentication attempt from IP 192.168.1.100"
            ),
            Log(
                service="api-gateway", 
                level="WARNING",
                message="Rate limit exceeded for user ID 12345"
            ),
            Log(
                service="database",
                level="INFO", 
                message="Database backup completed successfully"
            ),
            Log(
                service="payment-service",
                level="CRITICAL",
                message="Payment processing service is down"
            )
        ]
        
        # Add all data to database
        for threat in threats:
            db.session.add(threat)
        
        for log in logs:
            db.session.add(log)
        
        db.session.commit()
        print("Sample data added successfully!")

if __name__ == "__main__":
    add_sample_data()

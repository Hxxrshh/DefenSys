#!/usr/bin/env python3

import os
import sys
import uuid
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the src directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_server import app, db, Scan, Vulnerability, SBOM, Log

def create_sample_data():
    """Create comprehensive sample data for DefenSys"""
    print("Creating sample scans...")
    
    # Sample repositories
    repos = [
        'https://github.com/example/vulnerable-app',
        'https://github.com/example/nodejs-project',
        'https://github.com/example/python-microservice',
        'https://github.com/example/react-frontend'
    ]
    
    scan_ids = []
    
    # Create sample scans
    for i, repo in enumerate(repos):
        scan_id = str(uuid.uuid4())
        scan_ids.append(scan_id)
        
        status = 'COMPLETED' if i < 3 else 'IN_PROGRESS'
        created_time = datetime.utcnow() - timedelta(days=i+1)
        completed_time = created_time + timedelta(hours=2) if status == 'COMPLETED' else None
        
        scan = Scan(
            id=scan_id,
            repo_url=repo,
            scan_types=['SAST', 'SECRET', 'DEPENDENCY'],
            status=status,
            created_at=created_time,
            completed_at=completed_time,
            total_vulnerabilities=0
        )
        db.session.add(scan)
    
    print("Creating sample vulnerabilities...")
    
    # Sample vulnerabilities for completed scans
    sample_vulnerabilities = [
        # SAST vulnerabilities
        {
            'scanner': 'bandit',
            'severity': 'HIGH',
            'title': 'Hardcoded Password',
            'description': 'Hardcoded password detected in source code',
            'file_path': 'src/config.py',
            'line_number': 25,
            'vulnerability_id': 'CWE-259',
            'confidence': 'HIGH'
        },
        {
            'scanner': 'semgrep',
            'severity': 'CRITICAL',
            'title': 'SQL Injection',
            'description': 'Potential SQL injection vulnerability detected',
            'file_path': 'src/database.py',
            'line_number': 142,
            'vulnerability_id': 'CWE-89',
            'confidence': 'HIGH'
        },
        {
            'scanner': 'bandit',
            'severity': 'MEDIUM',
            'title': 'Weak Cryptographic Hash',
            'description': 'Use of MD5 hash function detected',
            'file_path': 'src/utils.py',
            'line_number': 67,
            'vulnerability_id': 'CWE-327',
            'confidence': 'MEDIUM'
        },
        
        # Secret vulnerabilities
        {
            'scanner': 'trufflehog',
            'severity': 'CRITICAL',
            'title': 'AWS Access Key Exposed',
            'description': 'AWS access key found in source code',
            'file_path': '.env.example',
            'line_number': 5,
            'vulnerability_id': 'SECRET-001'
        },
        {
            'scanner': 'secret_patterns',
            'severity': 'HIGH',
            'title': 'GitHub Token Exposed',
            'description': 'GitHub personal access token detected',
            'file_path': 'scripts/deploy.sh',
            'line_number': 12,
            'vulnerability_id': 'SECRET-002'
        },
        
        # Dependency vulnerabilities
        {
            'scanner': 'pip-audit',
            'severity': 'HIGH',
            'title': 'Known Vulnerability in requests',
            'description': 'requests package has a known security vulnerability',
            'package_name': 'requests',
            'package_version': '2.25.1',
            'vulnerability_id': 'CVE-2023-32681',
            'file_path': 'requirements.txt'
        },
        {
            'scanner': 'npm-audit',
            'severity': 'CRITICAL',
            'title': 'Path Traversal in express',
            'description': 'express package vulnerable to path traversal attacks',
            'package_name': 'express',
            'package_version': '4.17.1',
            'vulnerability_id': 'CVE-2022-24999',
            'file_path': 'package.json'
        },
        {
            'scanner': 'safety',
            'severity': 'MEDIUM',
            'title': 'Outdated Package: urllib3',
            'description': 'urllib3 package version has known issues',
            'package_name': 'urllib3',
            'package_version': '1.26.5',
            'vulnerability_id': 'CVE-2023-43804',
            'file_path': 'requirements.txt'
        }
    ]
    
    # Distribute vulnerabilities across completed scans
    vuln_id = 1
    for scan_id in scan_ids[:3]:  # Only for completed scans
        scan_vulns = sample_vulnerabilities[vuln_id-1:vuln_id+2] if vuln_id <= len(sample_vulnerabilities)-2 else sample_vulnerabilities[vuln_id-1:]
        
        for vuln_data in scan_vulns:
            vulnerability = Vulnerability(
                scan_id=scan_id,
                scanner=vuln_data['scanner'],
                severity=vuln_data['severity'],
                title=vuln_data['title'],
                description=vuln_data['description'],
                file_path=vuln_data.get('file_path'),
                line_number=vuln_data.get('line_number'),
                vulnerability_id=vuln_data.get('vulnerability_id'),
                package_name=vuln_data.get('package_name'),
                package_version=vuln_data.get('package_version'),
                confidence=vuln_data.get('confidence'),
                created_at=datetime.utcnow() - timedelta(days=len(scan_ids)-scan_ids.index(scan_id))
            )
            db.session.add(vulnerability)
        vuln_id += len(scan_vulns)
    
    print("Creating sample SBOM data...")
    
    # Sample SBOM data
    sample_packages = [
        # Python packages
        {'name': 'requests', 'version': '2.25.1', 'type': 'python', 'file': 'requirements.txt'},
        {'name': 'flask', 'version': '2.0.1', 'type': 'python', 'file': 'requirements.txt'},
        {'name': 'sqlalchemy', 'version': '1.4.23', 'type': 'python', 'file': 'requirements.txt'},
        {'name': 'urllib3', 'version': '1.26.5', 'type': 'python', 'file': 'requirements.txt'},
        
        # Node.js packages
        {'name': 'express', 'version': '4.17.1', 'type': 'nodejs', 'file': 'package.json'},
        {'name': 'lodash', 'version': '4.17.21', 'type': 'nodejs', 'file': 'package.json'},
        {'name': 'axios', 'version': '0.21.1', 'type': 'nodejs', 'file': 'package.json'},
        {'name': 'react', 'version': '17.0.2', 'type': 'nodejs', 'file': 'package.json'},
    ]
    
    for scan_id in scan_ids[:3]:  # Only for completed scans
        for package in sample_packages:
            sbom_entry = SBOM(
                scan_id=scan_id,
                package_name=package['name'],
                package_version=package['version'],
                package_type=package['type'],
                file_path=package['file'],
                created_at=datetime.utcnow() - timedelta(days=len(scan_ids)-scan_ids.index(scan_id))
            )
            db.session.add(sbom_entry)
    
    print("Creating sample logs...")
    
    # Sample logs
    sample_logs = [
        {'service': 'defensys-api', 'level': 'INFO', 'message': 'Server started successfully'},
        {'service': 'sast-scanner', 'level': 'INFO', 'message': 'SAST scan completed for repository'},
        {'service': 'secret-scanner', 'level': 'WARN', 'message': 'Potential secret detected during scan'},
        {'service': 'dependency-scanner', 'level': 'INFO', 'message': 'Dependency scan completed, SBOM generated'},
        {'service': 'defensys-api', 'level': 'ERROR', 'message': 'Database connection timeout'},
        {'service': 'sast-scanner', 'level': 'INFO', 'message': 'Bandit scan completed with 3 findings'},
        {'service': 'secret-scanner', 'level': 'CRITICAL', 'message': 'AWS credentials exposed in repository'},
        {'service': 'dependency-scanner', 'level': 'WARN', 'message': 'Vulnerable package detected: requests 2.25.1'},
    ]
    
    for i, log_data in enumerate(sample_logs):
        log = Log(
            service=log_data['service'],
            level=log_data['level'],
            message=log_data['message'],
            timestamp=datetime.utcnow() - timedelta(hours=i*2)
        )
        db.session.add(log)
    
    # Update scan vulnerability counts
    for scan_id in scan_ids[:3]:
        scan = Scan.query.get(scan_id)
        if scan:
            scan.total_vulnerabilities = Vulnerability.query.filter_by(scan_id=scan_id).count()
    
    db.session.commit()
    print("Sample data created successfully!")

def main():
    """Initialize database with enhanced DefenSys schema and sample data"""
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/defensys')
    
    print(f"Connecting to database: {database_url}")
    
    # Create engine and session
    engine = create_engine(database_url)
    
    # Create tables within app context
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")
        
        # Check if data already exists
        existing_scans = Scan.query.count()
        if existing_scans == 0:
            print("No existing data found. Creating sample data...")
            create_sample_data()
        else:
            print(f"Found {existing_scans} existing scans. Skipping sample data creation.")
    
    print("Database initialization completed!")

if __name__ == "__main__":
    main()

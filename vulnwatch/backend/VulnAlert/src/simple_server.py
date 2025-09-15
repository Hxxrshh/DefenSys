#!/usr/bin/env python3

import os
import json
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    # Use SQLite for now since PostgreSQL requires Docker
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///defensys.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    return app

app = create_app()

# Enhanced database models
class Scan(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    repo_url = db.Column(db.String(500), nullable=False)
    scan_types = db.Column(db.JSON)  # ['SAST', 'SECRET', 'DEPENDENCY']
    status = db.Column(db.String(32), default='PENDING')  # PENDING, IN_PROGRESS, COMPLETED, FAILED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    total_vulnerabilities = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'repo_url': self.repo_url,
            'scan_types': self.scan_types,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'total_vulnerabilities': self.total_vulnerabilities
        }

class Vulnerability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.String(36), db.ForeignKey('scan.id'), nullable=False)
    scanner = db.Column(db.String(64), nullable=False)  # bandit, semgrep, trufflehog, etc.
    severity = db.Column(db.String(32), nullable=False)
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(512))
    line_number = db.Column(db.Integer)
    vulnerability_id = db.Column(db.String(128))  # CVE, CWE, etc.
    package_name = db.Column(db.String(128))
    package_version = db.Column(db.String(64))
    confidence = db.Column(db.String(32))
    status = db.Column(db.String(32), default='OPEN')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'scan_id': self.scan_id,
            'scanner': self.scanner,
            'severity': self.severity,
            'title': self.title,
            'description': self.description,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'vulnerability_id': self.vulnerability_id,
            'package_name': self.package_name,
            'package_version': self.package_version,
            'confidence': self.confidence,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service = db.Column(db.String(128))
    level = db.Column(db.String(32))
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'service': self.service,
            'level': self.level,
            'message': self.message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

def create_sample_data():
    """Create sample data for demonstration"""
    if Scan.query.count() > 0:
        return  # Data already exists
    
    print("Creating sample data...")
    
    # Sample scan
    scan = Scan(
        repo_url='https://github.com/example/demo-app',
        scan_types=['SAST', 'SECRET', 'DEPENDENCY'],
        status='COMPLETED',
        completed_at=datetime.utcnow(),
        total_vulnerabilities=7
    )
    db.session.add(scan)
    db.session.commit()
    
    # Sample vulnerabilities
    vulnerabilities = [
        {
            'scan_id': scan.id,
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
            'scan_id': scan.id,
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
            'scan_id': scan.id,
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
            'scan_id': scan.id,
            'scanner': 'trufflehog',
            'severity': 'CRITICAL',
            'title': 'AWS Secret Key Exposed',
            'description': 'AWS secret access key found in repository',
            'file_path': 'config/aws.py',
            'line_number': 12,
            'vulnerability_id': 'SECRET-001',
            'confidence': 'HIGH'
        },
        {
            'scan_id': scan.id,
            'scanner': 'bandit',
            'severity': 'MEDIUM',
            'title': 'Use of insecure MD5 hash',
            'description': 'MD5 hash algorithm is cryptographically insecure',
            'file_path': 'src/auth.py',
            'line_number': 89,
            'vulnerability_id': 'CWE-327',
            'confidence': 'MEDIUM'
        },
        {
            'scan_id': scan.id,
            'scanner': 'semgrep',
            'severity': 'LOW',
            'title': 'Missing input validation',
            'description': 'User input not properly validated',
            'file_path': 'src/forms.py',
            'line_number': 34,
            'vulnerability_id': 'CWE-20',
            'confidence': 'LOW'
        },
        {
            'scan_id': scan.id,
            'scanner': 'eslint',
            'severity': 'MEDIUM',
            'title': 'Potential XSS vulnerability',
            'description': 'Unescaped user input in DOM manipulation',
            'file_path': 'static/js/app.js',
            'line_number': 67,
            'vulnerability_id': 'CWE-79',
            'confidence': 'MEDIUM'
        }
    ]
    
    for vuln_data in vulnerabilities:
        vulnerability = Vulnerability(**vuln_data)
        db.session.add(vulnerability)
    
    # Sample logs
    logs = [
        {'service': 'defensys-api', 'level': 'INFO', 'message': 'Server started successfully'},
        {'service': 'sast-scanner', 'level': 'INFO', 'message': 'SAST scan completed for repository'},
        {'service': 'defensys-api', 'level': 'WARN', 'message': 'High severity vulnerability detected'},
    ]
    
    for log_data in logs:
        log = Log(**log_data)
        db.session.add(log)
    
    db.session.commit()
    print("Sample data created!")

# API Routes
@app.route("/api/scans", methods=["POST"])
def create_scan():
    """Create a new comprehensive scan"""
    data = request.get_json()
    repo_url = data.get('repo_url')
    scan_types = data.get('scan_types', ['SAST', 'SECRET', 'DEPENDENCY'])
    
    if not repo_url:
        return jsonify({"error": "Repository URL is required"}), 400
    
    # Create scan record
    scan = Scan(
        repo_url=repo_url,
        scan_types=scan_types,
        status='COMPLETED',  # Simulate immediate completion for demo
        completed_at=datetime.utcnow(),
        total_vulnerabilities=3  # Mock data
    )
    db.session.add(scan)
    db.session.commit()
    
    # Create mock vulnerabilities
    mock_vulnerabilities = [
        {
            'scan_id': scan.id,
            'scanner': 'bandit',
            'severity': 'MEDIUM',
            'title': 'Use of insecure MD5 hash',
            'description': 'MD5 hash algorithm is considered insecure',
            'file_path': 'src/utils.py',
            'line_number': 42,
            'vulnerability_id': 'CWE-327',
            'confidence': 'HIGH'
        },
        {
            'scan_id': scan.id,
            'scanner': 'secret-scanner',
            'severity': 'HIGH',
            'title': 'API Key Detected',
            'description': 'Potential API key found in source code',
            'file_path': '.env',
            'line_number': 5,
            'vulnerability_id': 'SECRET-001'
        }
    ]
    
    for vuln_data in mock_vulnerabilities:
        vulnerability = Vulnerability(**vuln_data)
        db.session.add(vulnerability)
    
    db.session.commit()
    
    return jsonify(scan.to_dict()), 201

@app.route("/api/scans", methods=["GET"])
def get_scans():
    """Get all scans"""
    scans = Scan.query.order_by(Scan.created_at.desc()).all()
    return jsonify([scan.to_dict() for scan in scans])

@app.route("/api/scans/<scan_id>", methods=["GET"])
def get_scan(scan_id):
    """Get specific scan details"""
    scan = Scan.query.get_or_404(scan_id)
    vulnerabilities = Vulnerability.query.filter_by(scan_id=scan_id).all()
    
    return jsonify({
        'scan': scan.to_dict(),
        'vulnerabilities': [vuln.to_dict() for vuln in vulnerabilities],
        'sbom': []  # Empty for now
    })

@app.route("/api/vulnerabilities", methods=["GET"])
def get_vulnerabilities():
    """Get all vulnerabilities with filtering"""
    severity = request.args.get('severity')
    scanner = request.args.get('scanner')
    status = request.args.get('status')
    
    query = Vulnerability.query
    
    if severity:
        query = query.filter(Vulnerability.severity == severity.upper())
    if scanner:
        query = query.filter(Vulnerability.scanner == scanner)
    if status:
        query = query.filter(Vulnerability.status == status.upper())
    
    vulnerabilities = query.order_by(Vulnerability.created_at.desc()).all()
    return jsonify([vuln.to_dict() for vuln in vulnerabilities])

@app.route("/api/overview", methods=["GET"])
def get_overview():
    """Get dashboard overview statistics"""
    total_scans = Scan.query.count()
    total_vulnerabilities = Vulnerability.query.count()
    critical_vulnerabilities = Vulnerability.query.filter_by(severity='CRITICAL').count()
    high_vulnerabilities = Vulnerability.query.filter_by(severity='HIGH').count()
    
    recent_scans = Scan.query.order_by(Scan.created_at.desc()).limit(5).all()
    
    return jsonify({
        "totalScans": total_scans,
        "totalVulnerabilities": total_vulnerabilities,
        "criticalVulns": critical_vulnerabilities,
        "highVulns": high_vulnerabilities,
        "recentScans": [scan.to_dict() for scan in recent_scans]
    })

@app.route("/api/logs", methods=["GET"])
def get_logs():
    """Get system logs"""
    logs = Log.query.order_by(Log.timestamp.desc()).limit(100).all()
    return jsonify({
        "logs": [log.to_dict() for log in logs],
        "total": len(logs)
    })

@app.route("/api/charts", methods=["GET"])
def get_charts():
    """Get chart data for dashboard"""
    # Severity distribution
    severity_counts = db.session.query(
        Vulnerability.severity,
        db.func.count(Vulnerability.id)
    ).group_by(Vulnerability.severity).all()
    
    severity_distribution = []
    colors = {
        'CRITICAL': 'hsl(0, 84%, 60%)',
        'HIGH': 'hsl(25, 95%, 53%)',
        'MEDIUM': 'hsl(45, 93%, 47%)',
        'LOW': 'hsl(142, 71%, 45%)'
    }
    
    for severity, count in severity_counts:
        severity_distribution.append({
            'name': severity.title(),
            'value': count,
            'color': colors.get(severity, 'hsl(200, 50%, 50%)')
        })
    
    # Scanner distribution
    scanner_counts = db.session.query(
        Vulnerability.scanner,
        db.func.count(Vulnerability.id)
    ).group_by(Vulnerability.scanner).all()
    
    scanner_distribution = [
        {'name': scanner, 'value': count}
        for scanner, count in scanner_counts
    ]
    
    return jsonify({
        "severityDistribution": severity_distribution,
        "scannerDistribution": scanner_distribution
    })

# Legacy endpoints for backward compatibility
@app.route("/api/threats", methods=["GET"])
def get_threats():
    """Legacy endpoint - maps to vulnerabilities"""
    vulnerabilities = Vulnerability.query.order_by(Vulnerability.created_at.desc()).limit(50).all()
    
    # Convert to legacy format
    threats = []
    for vuln in vulnerabilities:
        threat = {
            'id': vuln.id,
            'package': vuln.package_name or vuln.title,
            'cveId': vuln.vulnerability_id or f'VULN-{vuln.id}',
            'severity': vuln.severity,
            'status': vuln.status,
            'description': vuln.description,
            'timestamp': vuln.created_at.isoformat() if vuln.created_at else None
        }
        threats.append(threat)
    
    return jsonify(threats)

@app.route("/api/threats/<int:threat_id>/acknowledge", methods=["POST"])
def acknowledge_threat(threat_id):
    """Acknowledge a vulnerability"""
    vulnerability = Vulnerability.query.get_or_404(threat_id)
    vulnerability.status = 'ACKNOWLEDGED'
    db.session.commit()
    return jsonify({"success": True, "message": f"Vulnerability {threat_id} acknowledged."})

@app.route("/")
def health_check():
    """Health check endpoint"""
    return jsonify({
        "service": "DefenSys API",
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat()
    })

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        create_sample_data()
    
    print("🛡️ DefenSys API Server Starting...")
    print("📊 Dashboard: http://localhost:8081")
    print("🔗 API: http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)

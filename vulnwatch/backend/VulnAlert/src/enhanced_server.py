#!/usr/bin/env python3

import os
import json
import uuid
import pika
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
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
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

class SBOM(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.String(36), db.ForeignKey('scan.id'), nullable=False)
    package_name = db.Column(db.String(128), nullable=False)
    package_version = db.Column(db.String(64))
    package_type = db.Column(db.String(32))  # python, nodejs, java, etc.
    file_path = db.Column(db.String(512))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'scan_id': self.scan_id,
            'package_name': self.package_name,
            'package_version': self.package_version,
            'package_type': self.package_type,
            'file_path': self.file_path,
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

# RabbitMQ connection
def get_broker_connection():
    broker_url = os.environ.get('BROKER_URL', 'amqp://admin:admin123@localhost:5672/')
    connection = pika.BlockingConnection(pika.URLParameters(broker_url))
    return connection

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
        status='PENDING'
    )
    db.session.add(scan)
    db.session.commit()
    
    # Queue scan jobs
    try:
        connection = get_broker_connection()
        channel = connection.channel()
        
        # Declare queues
        channel.queue_declare(queue='sast_scan_queue', durable=True)
        channel.queue_declare(queue='secret_scan_queue', durable=True)
        channel.queue_declare(queue='dependency_scan_queue', durable=True)
        
        scan_request = {
            'scan_id': scan.id,
            'repo_url': repo_url
        }
        
        # Queue jobs based on scan types
        if 'SAST' in scan_types:
            channel.basic_publish(
                exchange='',
                routing_key='sast_scan_queue',
                body=json.dumps(scan_request),
                properties=pika.BasicProperties(delivery_mode=2)
            )
        
        if 'SECRET' in scan_types:
            channel.basic_publish(
                exchange='',
                routing_key='secret_scan_queue',
                body=json.dumps(scan_request),
                properties=pika.BasicProperties(delivery_mode=2)
            )
        
        if 'DEPENDENCY' in scan_types:
            channel.basic_publish(
                exchange='',
                routing_key='dependency_scan_queue',
                body=json.dumps(scan_request),
                properties=pika.BasicProperties(delivery_mode=2)
            )
        
        connection.close()
        
        # Update scan status
        scan.status = 'IN_PROGRESS'
        db.session.commit()
        
        return jsonify(scan.to_dict()), 201
        
    except Exception as e:
        return jsonify({"error": f"Failed to queue scan: {str(e)}"}), 500

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
    sbom = SBOM.query.filter_by(scan_id=scan_id).all()
    
    return jsonify({
        'scan': scan.to_dict(),
        'vulnerabilities': [vuln.to_dict() for vuln in vulnerabilities],
        'sbom': [item.to_dict() for item in sbom]
    })

@app.route("/api/scan-results", methods=["POST"])
def receive_scan_results():
    """Receive results from scanner services"""
    data = request.get_json()
    scan_id = data.get('scan_id')
    scan_type = data.get('scan_type')
    status = data.get('status')
    
    scan = Scan.query.get(scan_id)
    if not scan:
        return jsonify({"error": "Scan not found"}), 404
    
    if status == 'completed':
        vulnerabilities = data.get('vulnerabilities', [])
        sbom_data = data.get('sbom', {})
        
        # Save vulnerabilities
        for vuln_data in vulnerabilities:
            vulnerability = Vulnerability(
                scan_id=scan_id,
                scanner=vuln_data.get('scanner'),
                severity=vuln_data.get('severity'),
                title=vuln_data.get('title'),
                description=vuln_data.get('description'),
                file_path=vuln_data.get('file_path'),
                line_number=vuln_data.get('line_number'),
                vulnerability_id=vuln_data.get('vulnerability_id'),
                package_name=vuln_data.get('package_name'),
                package_version=vuln_data.get('package_version'),
                confidence=vuln_data.get('confidence')
            )
            db.session.add(vulnerability)
        
        # Save SBOM data
        for package_type, packages in sbom_data.items():
            for package in packages:
                sbom_entry = SBOM(
                    scan_id=scan_id,
                    package_name=package.get('name'),
                    package_version=package.get('version'),
                    package_type=package_type.replace('_packages', ''),
                    file_path=package.get('file')
                )
                db.session.add(sbom_entry)
        
        # Update scan statistics
        scan.total_vulnerabilities = Vulnerability.query.filter_by(scan_id=scan_id).count()
        
        # Check if all scans are complete
        remaining_scans = []
        if 'SAST' in scan.scan_types and not Vulnerability.query.filter_by(scan_id=scan_id, scanner='bandit').first() and not Vulnerability.query.filter_by(scan_id=scan_id, scanner='semgrep').first():
            remaining_scans.append('SAST')
        
        if len(remaining_scans) == 0:
            scan.status = 'COMPLETED'
            scan.completed_at = datetime.utcnow()
    
    elif status == 'failed':
        scan.status = 'FAILED'
        # Log the error
        error_log = Log(
            service=f'{scan_type}_scanner',
            level='ERROR',
            message=f"Scan failed: {data.get('error', 'Unknown error')}"
        )
        db.session.add(error_log)
    
    db.session.commit()
    return jsonify({"message": "Results received successfully"})

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
    medium_vulnerabilities = Vulnerability.query.filter_by(severity='MEDIUM').count()
    
    # Calculate some derived metrics
    warnings = high_vulnerabilities + medium_vulnerabilities
    passed_tests = max(0, total_scans * 10 - total_vulnerabilities)  # Example calculation
    
    recent_scans = Scan.query.order_by(Scan.created_at.desc()).limit(5).all()
    
    return jsonify({
        "totalScans": total_scans,
        "totalVulnerabilities": total_vulnerabilities,
        "criticalVulns": critical_vulnerabilities,
        "warnings": warnings,
        "passedTests": passed_tests,
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

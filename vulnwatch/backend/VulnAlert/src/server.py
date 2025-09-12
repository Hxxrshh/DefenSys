import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

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

# Define models
class Threat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    package = db.Column(db.String(128), nullable=False)
    cve_id = db.Column(db.String(64), unique=True, nullable=False)
    severity = db.Column(db.String(32), nullable=False)
    status = db.Column(db.String(32), default='OPEN')
    description = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        return {
            'id': self.id,
            'package': self.package,
            'cveId': self.cve_id,
            'severity': self.severity,
            'status': self.status,
            'description': self.description,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service = db.Column(db.String(128))
    level = db.Column(db.String(32))
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        return {
            'id': self.id,
            'service': self.service,
            'level': self.level,
            'message': self.message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

@app.route("/api/threats", methods=["GET"])
def get_threats():
    threats = Threat.query.all()
    return jsonify([threat.to_dict() for threat in threats])

@app.route("/api/scan", methods=["POST"])
def api_scan():
    data = request.get_json()
    target = data.get("target")
    if not target:
        return jsonify({"error": "No target provided"}), 400

    # Example: Create a new threat and add it to the DB
    new_threat = Threat(
        package="example-package",
        cve_id=f"CVE-2025-{Threat.query.count() + 1}",
        severity="CRITICAL",
        description=f"Vulnerability found in {target}"
    )
    db.session.add(new_threat)
    db.session.commit()

    return jsonify(new_threat.to_dict()), 201

@app.route("/api/overview", methods=["GET"])
def get_overview():
    total_threats = Threat.query.count()
    critical_threats = Threat.query.filter_by(severity='CRITICAL').count()
    return jsonify({
        "totalScans": total_threats,
        "criticalVulns": critical_threats,
        "warnings": 156,
        "passedTests": 2891,
    })

@app.route("/api/logs", methods=["GET"])
def get_logs():
    logs = Log.query.all()
    return jsonify({
        "logs": [log.to_dict() for log in logs],
        "total": len(logs)
    })

@app.route("/api/threats/<int:threat_id>/acknowledge", methods=["POST"])
def acknowledge_threat(threat_id):
    threat = Threat.query.get_or_404(threat_id)
    threat.status = 'ACKNOWLEDGED'
    db.session.commit()
    return jsonify({"success": True, "message": f"Threat {threat_id} acknowledged."})

@app.route("/api/charts", methods=["GET"])
def get_charts():
    # Get actual data from database
    critical_count = Threat.query.filter_by(severity='CRITICAL').count()
    high_count = Threat.query.filter_by(severity='HIGH').count()
    medium_count = Threat.query.filter_by(severity='MEDIUM').count()
    low_count = Threat.query.filter_by(severity='LOW').count()
    
    return jsonify({
        "severityDistribution": [
            {"name": "Critical", "value": critical_count, "color": "hsl(0, 84%, 60%)"},
            {"name": "High", "value": high_count, "color": "hsl(25, 95%, 53%)"},
            {"name": "Medium", "value": medium_count, "color": "hsl(45, 93%, 47%)"},
            {"name": "Low", "value": low_count, "color": "hsl(142, 71%, 45%)"},
        ],
        "vulnerabilitiesTrend": [
            {"date": "2024-01-01", "critical": 15, "high": 45},
            {"date": "2024-01-02", "critical": 18, "high": 52},
        ],
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

from .app import db
from datetime import datetime

class Threat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    package = db.Column(db.String(128), nullable=False)
    cve_id = db.Column(db.String(64), unique=True, nullable=False)
    severity = db.Column(db.String(32), nullable=False)
    status = db.Column(db.String(32), default='OPEN')
    description = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'package': self.package,
            'cveId': self.cve_id,
            'severity': self.severity,
            'status': self.status,
            'description': self.description,
            'timestamp': self.timestamp.isoformat()
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
            'timestamp': self.timestamp.isoformat()
        }

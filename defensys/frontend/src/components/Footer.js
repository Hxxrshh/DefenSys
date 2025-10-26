import React from 'react';
import './Footer.css';

function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="app-footer">
      <div className="footer-content">
        <div className="footer-section">
          <div className="footer-brand">
            <h3 className="footer-logo">
              <i className="bi bi-shield-lock-fill"></i> DefenSys
            </h3>
            <p className="footer-tagline">
              Intelligent Security Vulnerability Scanner
            </p>
            <p className="footer-description">
              Enterprise-grade automated security scanning platform for DevSecOps teams
            </p>
          </div>
        </div>

        <div className="footer-section">
          <h4 className="footer-heading">Platform</h4>
          <ul className="footer-links">
            <li><a href="#dashboard">Dashboard</a></li>
            <li><a href="#scans">Scans</a></li>
            <li><a href="#targets">Targets</a></li>
            <li><a href="#vulnerabilities">Vulnerabilities</a></li>
          </ul>
        </div>

        <div className="footer-section">
          <h4 className="footer-heading">Security Tools</h4>
          <ul className="footer-links">
            <li><span className="tool-badge">Nmap</span></li>
            <li><span className="tool-badge">Nuclei</span></li>
            <li><span className="tool-badge">ZAP</span></li>
            <li><span className="tool-badge">Trivy</span></li>
            <li><span className="tool-badge">Snyk</span></li>
            <li><span className="tool-badge">Semgrep</span></li>
          </ul>
        </div>

        <div className="footer-section">
          <h4 className="footer-heading">System Info</h4>
          <div className="system-info">
            <div className="info-item">
              <span className="info-label">Version:</span>
              <span className="info-value">v1.0.0</span>
            </div>
            <div className="info-item">
              <span className="info-label">Status:</span>
              <span className="status-indicator">
                <span className="status-dot"></span> Operational
              </span>
            </div>
            <div className="info-item">
              <span className="info-label">Build:</span>
              <span className="info-value">2025.10.26</span>
            </div>
          </div>
        </div>
      </div>

      <div className="footer-bottom">
        <div className="footer-bottom-content">
          <div className="copyright">
            <p>© {currentYear} DefenSys. All rights reserved.</p>
            <p className="security-notice">
              <i className="bi bi-shield-check"></i> Secure by Design | DevSecOps Ready
            </p>
          </div>
          <div className="footer-badges">
            <span className="tech-badge">FastAPI</span>
            <span className="tech-badge">React</span>
            <span className="tech-badge">SQLite</span>
            <span className="tech-badge">Docker</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;

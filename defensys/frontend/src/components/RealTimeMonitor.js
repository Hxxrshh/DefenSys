import React, { useState, useEffect } from 'react';
import './RealTimeMonitor.css';

function RealTimeMonitor({ activeScans = [] }) {
  const [scanProgress, setScanProgress] = useState({});

  useEffect(() => {
    // Simulate progress updates for active scans
    const interval = setInterval(() => {
      setScanProgress(prev => {
        const updated = { ...prev };
        activeScans.forEach(scan => {
          if (scan.status === 'running') {
            updated[scan.id] = Math.min((updated[scan.id] || scan.progress || 0) + 2, 100);
          }
        });
        return updated;
      });
    }, 2000);

    return () => clearInterval(interval);
  }, [activeScans]);

  const getToolDescription = (tool) => {
    const descriptions = {
      'Nmap': 'Scanning network for open ports that hackers might exploit',
      'Nuclei': 'Checking for known vulnerabilities using security templates',
      'Nikto': 'Analyzing web server for common security issues',
      'ZAP': 'Testing web application for security weaknesses',
      'Trivy': 'Scanning containers for outdated and vulnerable packages',
      'Snyk': 'Checking code dependencies for security risks',
      'Semgrep': 'Analyzing source code for security patterns',
      'Bandit': 'Reviewing Python code for security vulnerabilities'
    };
    return descriptions[tool] || 'Running security analysis...';
  };

  const getToolIcon = (tool) => {
    const icons = {
      'Nmap': 'bi-hdd-network',
      'Nuclei': 'bi-radioactive',
      'Nikto': 'bi-globe',
      'ZAP': 'bi-shield-lock',
      'Trivy': 'bi-box-seam',
      'Snyk': 'bi-code-slash',
      'Semgrep': 'bi-file-code',
      'Bandit': 'bi-bug'
    };
    return icons[tool] || 'bi-cpu';
  };

  if (activeScans.length === 0) {
    return (
      <div className="real-time-monitor-empty">
        <div className="pulse-icon">
          <i className="bi bi-hourglass-split"></i>
        </div>
        <p className="empty-text">No active scans running</p>
        <p className="empty-subtext">Start a new scan to see real-time progress here</p>
      </div>
    );
  }

  return (
    <div className="real-time-monitor">
      <div className="monitor-header">
        <div className="live-indicator">
          <span className="pulse-dot"></span>
          <span className="live-text">LIVE</span>
        </div>
        <h5 className="monitor-title">Active Scans</h5>
      </div>

      <div className="active-scans-list">
        {activeScans.map((scan) => (
          <div key={scan.id} className="scan-item">
            <div className="scan-header">
              <div className="scan-info">
                <i className={`bi ${getToolIcon(scan.current_tool || 'Nmap')} tool-icon`}></i>
                <div className="scan-details">
                  <span className="scan-name">Scan #{scan.id}</span>
                  <span className="scan-type">{scan.scan_type} scan</span>
                </div>
              </div>
              <span className="scan-percentage">{scanProgress[scan.id] || scan.progress || 0}%</span>
            </div>

            <div className="scan-progress-bar">
              <div 
                className="scan-progress-fill"
                style={{ width: `${scanProgress[scan.id] || scan.progress || 0}%` }}
              >
                <div className="progress-shimmer"></div>
              </div>
            </div>

            <div className="scan-description">
              <i className="bi bi-info-circle me-2"></i>
              {scan.current_stage || getToolDescription(scan.current_tool || 'Nmap')}
            </div>

            {scan.scan_tools && (
              <div className="scan-tools">
                <span className="tools-label">Tools:</span>
                {scan.scan_tools.map((tool, idx) => (
                  <span key={idx} className="tool-badge">
                    <i className={`bi ${getToolIcon(tool)}`}></i> {tool}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="monitor-footer">
        <div className="system-health">
          <i className="bi bi-heart-pulse text-success"></i>
          <span>System Health: Optimal</span>
        </div>
        <div className="scan-rate">
          <i className="bi bi-speedometer2 text-info"></i>
          <span>Scan Rate: {activeScans.length} active</span>
        </div>
      </div>
    </div>
  );
}

export default RealTimeMonitor;

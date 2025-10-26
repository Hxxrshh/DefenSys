import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { targetAPI, scanAPI, vulnerabilityAPI, scannerAPI } from '../services/api';
import ScanForm from '../components/ScanForm';
import RealTimeMonitor from '../components/RealTimeMonitor';
import StatisticalInsights from '../components/StatisticalInsights';
import VulnerabilityExplainer from '../components/VulnerabilityExplainer';
import './Dashboard.css';

function Dashboard() {
  const [stats, setStats] = useState({
    totalTargets: 0,
    totalScans: 0,
    activeScans: 0,
    totalVulnerabilities: 0,
    criticalVulns: 0,
    highVulns: 0,
  });
  const [recentScans, setRecentScans] = useState([]);
  const [vulnerabilities, setVulnerabilities] = useState([]);
  const [scanners, setScanners] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showScanForm, setShowScanForm] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      // Load targets
      const targets = await targetAPI.getAll(0, 1000);
      
      // Load scans
      const scans = await scanAPI.getAll(0, 1000);
      
      // Load vulnerabilities
      const vulnerabilities = await vulnerabilityAPI.getAll();
      
      // Load scanners
      const scannersData = await scannerAPI.getAvailable();

      // Calculate stats
      const activeScans = scans.filter(s => s.status === 'running').length;
      const criticalVulns = vulnerabilities.filter(v => v.severity === 'Critical').length;
      const highVulns = vulnerabilities.filter(v => v.severity === 'High').length;

      setStats({
        totalTargets: targets.length,
        totalScans: scans.length,
        activeScans,
        totalVulnerabilities: vulnerabilities.length,
        criticalVulns,
        highVulns,
      });

      // Get 5 most recent scans
      const sortedScans = scans.sort((a, b) => 
        new Date(b.started_at) - new Date(a.started_at)
      ).slice(0, 5);
      setRecentScans(sortedScans);

      // Store vulnerabilities for the explainer component
      setVulnerabilities(vulnerabilities);

      setScanners(scannersData.scanners || []);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const getStatusBadgeClass = (status) => {
    const statusMap = {
      pending: 'bg-secondary',
      running: 'bg-primary',
      completed: 'bg-success',
      failed: 'bg-danger',
    };
    return statusMap[status] || 'bg-secondary';
  };

  const getSeverityBadgeClass = (severity) => {
    const severityMap = {
      critical: 'bg-danger',
      high: 'bg-warning text-dark',
      medium: 'bg-info text-dark',
      low: 'bg-success',
      info: 'bg-secondary',
    };
    return severityMap[severity] || 'bg-secondary';
  };

  if (loading) {
    return (
      <div className="container mt-4">
        <div className="spinner-container">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container-fluid mt-4">
      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="dashboard-title">Security Operations Center</h1>
          <p className="dashboard-subtitle">Real-time monitoring and threat detection dashboard</p>
        </div>
        <button 
          className="btn btn-primary"
          onClick={() => setShowScanForm(true)}
        >
          <i className="bi bi-lightning-charge me-2"></i>
          Start Quick Scan
        </button>
      </div>

      {/* Statistics Cards */}
      <div className="row mb-4">
        <div className="col-md-3 mb-3">
          <div className="card stat-card stat-cyan">
            <div className="card-body">
              <div className="stat-icon icon-cyan">
                <i className="bi bi-activity"></i>
              </div>
              <h3 className="stat-number">{stats.totalScans.toLocaleString()}</h3>
              <p className="stat-label">Total Scans</p>
              <p className="stat-change">+12% from last week</p>
            </div>
          </div>
        </div>

        <div className="col-md-3 mb-3">
          <div className="card stat-card stat-red">
            <div className="card-body">
              <div className="stat-icon icon-red">
                <i className="bi bi-exclamation-triangle"></i>
              </div>
              <h3 className="stat-number">{stats.criticalVulns + stats.highVulns}</h3>
              <p className="stat-label">Active Threats</p>
              <div className="stat-detail">
                <span className="badge bg-danger me-1">{stats.criticalVulns} critical</span>
                <span className="badge bg-warning">{stats.highVulns} high</span>
              </div>
            </div>
          </div>
        </div>

        <div className="col-md-3 mb-3">
          <div className="card stat-card stat-green">
            <div className="card-body">
              <div className="stat-icon icon-green">
                <i className="bi bi-arrow-up-circle"></i>
              </div>
              <h3 className="stat-number">99.8%</h3>
              <p className="stat-label">System Uptime</p>
              <p className="stat-change">28 days continuous</p>
            </div>
          </div>
        </div>

        <div className="col-md-3 mb-3">
          <div className="card stat-card stat-blue">
            <div className="card-body">
              <div className="stat-icon icon-blue">
                <i className="bi bi-clock"></i>
              </div>
              <h3 className="stat-number">{stats.activeScans > 0 ? 'Running' : '2m ago'}</h3>
              <p className="stat-label">Last Scan</p>
              <p className="stat-change">{stats.activeScans > 0 ? `${stats.activeScans} active` : 'API Endpoint Check'}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Real-Time Monitoring Panel */}
      <div className="row mb-4">
        <div className="col-12">
          <RealTimeMonitor activeScans={recentScans.filter(s => s.status === 'running')} />
        </div>
      </div>

      {/* Statistical Insights */}
      <div className="row mb-4">
        <div className="col-12">
          <StatisticalInsights scans={recentScans} vulnerabilities={vulnerabilities} />
        </div>
      </div>

      {/* Vulnerability Explainer */}
      <div className="row mb-4">
        <div className="col-12">
          <VulnerabilityExplainer vulnerabilities={vulnerabilities.slice(0, 10)} />
        </div>
      </div>

      <div className="row">
        {/* Recent Scans */}
        <div className="col-md-8 mb-4">
          <div className="card">
            <div className="card-header">
              <i className="bi bi-shield-check section-icon"></i>
              <span className="section-title">Recent Security Scans</span>
              <p className="text-muted mb-0 mt-1" style={{fontSize: '0.85rem'}}>Latest vulnerability assessments and security checks</p>
            </div>
            <div className="card-body p-0">
              {recentScans.length === 0 ? (
                <div className="empty-state">
                  <i className="bi bi-shield-x"></i>
                  <p>No scans yet. Start your first scan!</p>
                </div>
              ) : (
                <div className="table-responsive">
                  <table className="table table-hover mb-0">
                    <thead>
                      <tr>
                        <th>Scan Name</th>
                        <th>Timestamp</th>
                        <th>Severity</th>
                        <th>Status</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recentScans.map((scan) => (
                        <tr key={scan.id}>
                          <td>
                            <i className="bi bi-shield-check text-success me-2"></i>
                            <strong>Scan #{scan.id}</strong>
                          </td>
                          <td className="text-muted">
                            {new Date(scan.started_at).toLocaleString('en-US', { 
                              month: 'short', 
                              day: 'numeric', 
                              hour: '2-digit', 
                              minute: '2-digit' 
                            })}
                          </td>
                          <td>
                            <span className="badge bg-secondary">{scan.scan_type}</span>
                          </td>
                          <td>
                            <span className={`badge scan-status-badge status-${scan.status}`}>
                              {scan.status}
                            </span>
                          </td>
                          <td>
                            <Link 
                              to={`/scans/${scan.id}`}
                              className="btn btn-sm btn-outline-primary"
                            >
                              View
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Scanner Status */}
        <div className="col-md-4 mb-4">
          <div className="card">
            <div className="card-header">
              <i className="bi bi-hdd-network section-icon"></i>
              <span className="section-title">Security Alerts</span>
              <p className="text-muted mb-0 mt-1" style={{fontSize: '0.85rem'}}>Recent security notifications</p>
            </div>
            <div className="card-body">
              {scanners.length === 0 ? (
                <p className="text-muted text-center py-3">Loading scanners...</p>
              ) : (
                <div>
                  {scanners.slice(0, 5).map((scanner) => (
                    <div key={scanner.name} className="scanner-status-item">
                      <div className="d-flex justify-content-between align-items-center">
                        <div>
                          <div className="scanner-name">{scanner.name}</div>
                          <div className="scanner-description">{scanner.description}</div>
                        </div>
                        <span className={`badge scanner-badge ${scanner.available ? 'bg-success' : 'bg-danger'}`}>
                          {scanner.available ? 'Online' : 'Offline'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Scan Form Modal */}
      {showScanForm && (
        <div className="modal show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.7)', overflow: 'auto' }}>
          <div className="modal-dialog modal-lg modal-dialog-scrollable">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Start New Scan</h5>
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => setShowScanForm(false)}
                ></button>
              </div>
              <div className="modal-body" style={{ maxHeight: '70vh', overflowY: 'auto' }}>
                <ScanForm 
                  onSuccess={() => {
                    setShowScanForm(false);
                    loadDashboardData();
                  }}
                  onCancel={() => setShowScanForm(false)}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;

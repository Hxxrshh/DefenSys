import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { scanAPI, vulnerabilityAPI, findingAPI, createWebSocket } from '../services/api';
import ScanProgress from '../components/ScanProgress';
import './ScanResults.css';
 
function ScanResults() {
  const { scanId } = useParams();
  const [scan, setScan] = useState(null);
  const [vulnerabilities, setVulnerabilities] = useState([]);
  const [findings, setFindings] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState({
    severity: 'all',
    scanner: 'all',
  });
  const [ws, setWs] = useState(null);

  useEffect(() => {
    if (scanId) {
      loadScanData(parseInt(scanId));
      
      // Setup WebSocket for real-time updates
      const websocket = createWebSocket(
        (data) => {
          if (data.scan_id === parseInt(scanId)) {
            handleWebSocketUpdate(data);
          }
        },
        (error) => {
          console.error('WebSocket error:', error);
        }
      );
      
      setWs(websocket);

      return () => {
        if (websocket) {
          websocket.close();
        }
      };
    }
  }, [scanId]);

  const loadScanData = async (id) => {
    try {
      setLoading(true);
      const results = await scanAPI.getResults(id);
      
      setScan(results.scan);
      setVulnerabilities(results.vulnerabilities || []);
      setFindings(results.findings || []);
      setSummary(results.summary);
    } catch (err) {
      console.error('Failed to load scan data:', err);
      setError('Failed to load scan results');
    } finally {
      setLoading(false);
    }
  };

  const handleWebSocketUpdate = (data) => {
    if (data.type === 'progress') {
      setScan(prev => ({
        ...prev,
        progress: data.progress,
        current_stage: data.current_stage,
        status: data.status,
      }));
    } else if (data.type === 'complete') {
      // Reload full scan data when complete
      loadScanData(parseInt(scanId));
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const getSeverityBadgeClass = (severity) => {
    const severityMap = {
      critical: 'bg-danger',
      high: 'bg-warning text-dark',
      medium: 'bg-info text-dark',
      low: 'bg-success',
      info: 'bg-secondary',
    };
    return severityMap[severity?.toLowerCase()] || 'bg-secondary';
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

  const filteredVulnerabilities = vulnerabilities.filter((vuln) => {
    if (filter.severity !== 'all' && vuln.severity?.toLowerCase() !== filter.severity) {
      return false;
    }
    if (filter.scanner !== 'all' && vuln.scanner_name !== filter.scanner) {
      return false;
    }
    return true;
  });

  const uniqueScanners = [...new Set(vulnerabilities.map(v => v.scanner_name))];

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

  if (error || !scan) {
    return (
      <div className="container mt-4">
        <div className="alert alert-danger" role="alert">
          {error || 'Scan not found'}
        </div>
      </div>
    );
  }

  return (
    <div className="container mt-4">
      {/* Scan Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Scan Results #{scan.id}</h1>
        <span className={`badge ${getStatusBadgeClass(scan.status)} fs-6`}>
          {scan.status.toUpperCase()}
        </span>
      </div>

      {/* Scan Progress (if running) */}
      {scan.status === 'running' && (
        <ScanProgress scan={scan} />
      )}

      {/* Scan Info Card */}
      <div className="card mb-4">
        <div className="card-header">
          <h5 className="mb-0">Scan Information</h5>
        </div>
        <div className="card-body">
          <div className="row">
            <div className="col-md-3">
              <strong>Scan Type:</strong>
              <br />
              <span className="badge bg-secondary mt-1">{scan.scan_type}</span>
            </div>
            <div className="col-md-3">
              <strong>Tools Used:</strong>
              <br />
              <div className="mt-1">
                {scan.scan_tools && scan.scan_tools.map((tool, idx) => (
                  <span key={idx} className="badge bg-info text-dark me-1">{tool}</span>
                ))}
              </div>
            </div>
            <div className="col-md-3">
              <strong>Started:</strong>
              <br />
              {formatDate(scan.started_at)}
            </div>
            <div className="col-md-3">
              <strong>Completed:</strong>
              <br />
              {formatDate(scan.completed_at)}
            </div>
          </div>
        </div>
      </div>

      {/* Summary Statistics */}
      {summary && scan.status === 'completed' && (
        <div className="row mb-4">
          <div className="col-md-3 mb-3">
            <div className="card stat-card">
              <div className="card-body text-center">
                <h3 className="text-danger">{summary.total_vulnerabilities}</h3>
                <p className="text-muted mb-0">Total Vulnerabilities</p>
              </div>
            </div>
          </div>
          <div className="col-md-3 mb-3">
            <div className="card stat-card">
              <div className="card-body text-center">
                <h3 className="text-danger">{summary.critical_count}</h3>
                <p className="text-muted mb-0">Critical</p>
              </div>
            </div>
          </div>
          <div className="col-md-3 mb-3">
            <div className="card stat-card">
              <div className="card-body text-center">
                <h3 className="text-warning">{summary.high_count}</h3>
                <p className="text-muted mb-0">High</p>
              </div>
            </div>
          </div>
          <div className="col-md-3 mb-3">
            <div className="card stat-card">
              <div className="card-body text-center">
                <h3 className="text-primary">{summary.total_findings}</h3>
                <p className="text-muted mb-0">Findings</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Vulnerabilities Section */}
      {scan.status === 'completed' && (
        <>
          <div className="card mb-4">
            <div className="card-header d-flex justify-content-between align-items-center">
              <h5 className="mb-0">Vulnerabilities ({filteredVulnerabilities.length})</h5>
              <div className="d-flex gap-2">
                <select
                  className="form-select form-select-sm"
                  value={filter.severity}
                  onChange={(e) => setFilter({ ...filter, severity: e.target.value })}
                  style={{ width: 'auto' }}
                >
                  <option value="all">All Severities</option>
                  <option value="critical">Critical</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                  <option value="info">Info</option>
                </select>
                <select
                  className="form-select form-select-sm"
                  value={filter.scanner}
                  onChange={(e) => setFilter({ ...filter, scanner: e.target.value })}
                  style={{ width: 'auto' }}
                >
                  <option value="all">All Scanners</option>
                  {uniqueScanners.map((scanner) => (
                    <option key={scanner} value={scanner}>{scanner}</option>
                  ))}
                </select>
              </div>
            </div>
            <div className="card-body">
              {filteredVulnerabilities.length === 0 ? (
                <div className="text-center py-4">
                  <i className="bi bi-shield-check" style={{ fontSize: '3rem', color: '#28a745' }}></i>
                  <p className="text-muted mt-3">No vulnerabilities found!</p>
                </div>
              ) : (
                <div className="vulnerability-list">
                  {filteredVulnerabilities.map((vuln) => (
                    <div key={vuln.id} className="vulnerability-item card mb-3">
                      <div className="card-body">
                        <div className="d-flex justify-content-between align-items-start mb-2">
                          <h6 className="mb-0">{vuln.title}</h6>
                          <span className={`badge ${getSeverityBadgeClass(vuln.severity)}`}>
                            {vuln.severity}
                          </span>
                        </div>
                        <p className="text-muted mb-2">{vuln.description}</p>
                        <div className="row">
                          <div className="col-md-6">
                            <small>
                              <strong>Scanner:</strong> {vuln.scanner_name}
                              {vuln.target_host && (
                                <>
                                  <br />
                                  <strong>Host:</strong> {vuln.target_host}
                                  {vuln.target_port && `:${vuln.target_port}`}
                                </>
                              )}
                            </small>
                          </div>
                          <div className="col-md-6">
                            {vuln.cve_ids && vuln.cve_ids.length > 0 && (
                              <small>
                                <strong>CVEs:</strong>
                                {vuln.cve_ids.map((cve, idx) => (
                                  <span key={idx} className="badge bg-dark ms-1">{cve}</span>
                                ))}
                              </small>
                            )}
                            {vuln.cvss_score && (
                              <small className="ms-2">
                                <strong>CVSS:</strong> {vuln.cvss_score}
                              </small>
                            )}
                          </div>
                        </div>
                        {vuln.remediation && (
                          <div className="mt-2 p-2 bg-light rounded">
                            <small>
                              <strong>Remediation:</strong> {vuln.remediation}
                            </small>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Findings Section */}
          {findings.length > 0 && (
            <div className="card">
              <div className="card-header">
                <h5 className="mb-0">Findings ({findings.length})</h5>
              </div>
              <div className="card-body">
                <div className="table-responsive">
                  <table className="table table-sm">
                    <thead>
                      <tr>
                        <th>Type</th>
                        <th>Scanner</th>
                        <th>Host</th>
                        <th>Port</th>
                        <th>Service</th>
                        <th>Details</th>
                      </tr>
                    </thead>
                    <tbody>
                      {findings.map((finding) => (
                        <tr key={finding.id}>
                          <td>
                            <span className="badge bg-info text-dark">{finding.finding_type}</span>
                          </td>
                          <td>{finding.scanner_name}</td>
                          <td><code>{finding.host}</code></td>
                          <td>{finding.port || 'N/A'}</td>
                          <td>{finding.service || 'N/A'}</td>
                          <td>
                            {finding.data && (
                              <small className="text-muted">
                                {JSON.stringify(finding.data).substring(0, 100)}...
                              </small>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default ScanResults;
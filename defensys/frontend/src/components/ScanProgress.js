import React from 'react';
import './ScanProgress.css';

function ScanProgress({ scan }) {
  const progress = scan.progress || 0;
  const currentStage = scan.current_stage || 'Initializing...';

  const getProgressVariant = () => {
    if (progress < 25) return 'info';
    if (progress < 50) return 'primary';
    if (progress < 75) return 'warning';
    return 'success';
  };

  return (
    <div className="card scan-progress-card mb-4">
      <div className="card-body">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <h5 className="mb-0">
            <i className="bi bi-activity me-2 text-primary"></i>
            Scan in Progress
          </h5>
          <span className="badge bg-primary">
            <i className="bi bi-clock me-1"></i>
            Running
          </span>
        </div>

        <div className="current-stage mb-3">
          <div className="stage-icon">
            <div className="spinner-border spinner-border-sm text-primary" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
          </div>
          <div className="stage-text">
            <strong>Current Stage:</strong>
            <p className="mb-0">{currentStage}</p>
          </div>
        </div>

        <div className="progress" style={{ height: '30px' }}>
          <div
            className={`progress-bar progress-bar-striped progress-bar-animated bg-${getProgressVariant()}`}
            role="progressbar"
            style={{ width: `${progress}%` }}
            aria-valuenow={progress}
            aria-valuemin="0"
            aria-valuemax="100"
          >
            <strong>{progress.toFixed(1)}%</strong>
          </div>
        </div>

        <div className="progress-info mt-3">
          <small className="text-muted">
            <i className="bi bi-info-circle me-1"></i>
            This page will automatically update as the scan progresses. 
            Results will appear when the scan completes.
          </small>
        </div>

        {scan.scan_tools && scan.scan_tools.length > 0 && (
          <div className="mt-3">
            <small>
              <strong>Tools:</strong>
              {scan.scan_tools.map((tool, idx) => (
                <span key={idx} className="badge bg-secondary ms-1">{tool}</span>
              ))}
            </small>
          </div>
        )}
      </div>
    </div>
  );
}

export default ScanProgress;

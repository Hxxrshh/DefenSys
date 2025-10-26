import React, { useState, useEffect } from 'react';
import { targetAPI, scanAPI, scannerAPI } from '../services/api';
import './ScanForm.css';

function ScanForm({ onSuccess, onCancel, preselectedTarget = null }) {
  const [formData, setFormData] = useState({
    targetValue: '',
    targetType: 'ip',
    scanType: 'default',
    scanTools: [],
  });
  const [targets, setTargets] = useState([]);
  const [availableScanners, setAvailableScanners] = useState([]);
  const [useExistingTarget, setUseExistingTarget] = useState(false);
  const [selectedTargetId, setSelectedTargetId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (preselectedTarget) {
      setUseExistingTarget(true);
      setSelectedTargetId(preselectedTarget.id);
      setFormData({
        ...formData,
        targetValue: preselectedTarget.value,
        targetType: preselectedTarget.target_type,
      });
    }
  }, [preselectedTarget]);

  const loadData = async () => {
    try {
      const [targetsData, scannersData] = await Promise.all([
        targetAPI.getAll(),
        scannerAPI.getAvailable(),
      ]);
      setTargets(targetsData);
      setAvailableScanners(scannersData.scanners || []);
    } catch (err) {
      console.error('Failed to load data:', err);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleScannerToggle = (scannerName) => {
    const updatedTools = formData.scanTools.includes(scannerName)
      ? formData.scanTools.filter(t => t !== scannerName)
      : [...formData.scanTools, scannerName];
    
    setFormData({
      ...formData,
      scanTools: updatedTools,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Prepare scan configuration
      const scanConfig = {
        target_value: formData.targetValue,
        target_type: formData.targetType,
        scan_type: formData.scanType,
      };

      // Add scan tools if selected
      if (formData.scanTools.length > 0) {
        scanConfig.scan_tools = formData.scanTools;
      }

      // Start the scan
      const result = await scanAPI.start(scanConfig);
      
      if (onSuccess) {
        onSuccess(result);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start scan. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getRecommendedScanners = () => {
    const { targetType, scanType } = formData;
    
    // Recommend scanners based on target type and scan type
    const recommendations = {
      ip: ['nmap', 'nuclei'],
      domain: ['nmap', 'nuclei', 'nikto'],
      url: ['zap', 'nuclei', 'nikto'],
      cidr: ['nmap'],
    };

    return recommendations[targetType] || [];
  };

  return (
    <form onSubmit={handleSubmit} className="scan-form">
      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}

      {/* Target Selection */}
      <div className="mb-3">
        <label className="form-label">Target Source</label>
        <div className="btn-group w-100" role="group">
          <input
            type="radio"
            className="btn-check"
            name="targetSource"
            id="newTarget"
            checked={!useExistingTarget}
            onChange={() => setUseExistingTarget(false)}
          />
          <label className="btn btn-outline-primary" htmlFor="newTarget">
            New Target
          </label>

          <input
            type="radio"
            className="btn-check"
            name="targetSource"
            id="existingTarget"
            checked={useExistingTarget}
            onChange={() => setUseExistingTarget(true)}
          />
          <label className="btn btn-outline-primary" htmlFor="existingTarget">
            Existing Target
          </label>
        </div>
      </div>

      {useExistingTarget ? (
        <div className="mb-3">
          <label htmlFor="targetSelect" className="form-label">Select Target</label>
          <select
            id="targetSelect"
            className="form-select"
            value={selectedTargetId || ''}
            onChange={(e) => {
              const targetId = parseInt(e.target.value);
              setSelectedTargetId(targetId);
              const target = targets.find(t => t.id === targetId);
              if (target) {
                setFormData({
                  ...formData,
                  targetValue: target.value,
                  targetType: target.target_type,
                });
              }
            }}
            required
          >
            <option value="">Choose a target...</option>
            {targets.map((target) => (
              <option key={target.id} value={target.id}>
                {target.name} - {target.value} ({target.target_type})
              </option>
            ))}
          </select>
        </div>
      ) : (
        <>
          <div className="mb-3">
            <label htmlFor="targetValue" className="form-label">Target Value *</label>
            <input
              type="text"
              className="form-control"
              id="targetValue"
              name="targetValue"
              value={formData.targetValue}
              onChange={handleInputChange}
              placeholder="e.g., 192.168.1.1, example.com, https://example.com"
              required
            />
            <div className="form-text">
              Enter IP address, domain name, URL, or CIDR notation
            </div>
          </div>

          <div className="mb-3">
            <label htmlFor="targetType" className="form-label">Target Type *</label>
            <select
              id="targetType"
              className="form-select"
              name="targetType"
              value={formData.targetType}
              onChange={handleInputChange}
              required
            >
              <option value="ip">IP Address</option>
              <option value="domain">Domain</option>
              <option value="url">URL</option>
              <option value="cidr">CIDR Network</option>
            </select>
          </div>
        </>
      )}

      {/* Scan Type */}
      <div className="mb-3">
        <label htmlFor="scanType" className="form-label">Scan Type *</label>
        <select
          id="scanType"
          className="form-select"
          name="scanType"
          value={formData.scanType}
          onChange={handleInputChange}
          required
        >
          <option value="quick">Quick Scan (Fast, common ports)</option>
          <option value="default">Default Scan (Balanced)</option>
          <option value="full">Full Scan (Comprehensive, slow)</option>
          <option value="network">Network Scan (Infrastructure focus)</option>
          <option value="web">Web Scan (Application focus)</option>
        </select>
        <div className="form-text">
          {formData.scanType === 'quick' && 'Scans top 100 ports, quick vulnerability checks'}
          {formData.scanType === 'default' && 'Scans top 1000 ports, standard security checks'}
          {formData.scanType === 'full' && 'Scans all 65535 ports, deep vulnerability analysis'}
          {formData.scanType === 'network' && 'Focus on network enumeration and infrastructure'}
          {formData.scanType === 'web' && 'Focus on web application vulnerabilities'}
        </div>
      </div>

      {/* Scanner Selection */}
      <div className="mb-3">
        <label className="form-label">
          Select Scanners 
          <span className="text-muted ms-2">(Optional - auto-selected if none chosen)</span>
        </label>
        <div className="scanner-grid">
          {availableScanners.map((scanner) => {
            const isRecommended = getRecommendedScanners().includes(scanner.name.toLowerCase());
            const isSelected = formData.scanTools.includes(scanner.name);
            
            return (
              <div key={scanner.name} className="scanner-card">
                <input
                  type="checkbox"
                  className="btn-check"
                  id={`scanner-${scanner.name}`}
                  checked={isSelected}
                  onChange={() => handleScannerToggle(scanner.name)}
                  disabled={!scanner.available}
                />
                <label
                  className={`btn btn-outline-secondary w-100 ${isRecommended ? 'recommended' : ''}`}
                  htmlFor={`scanner-${scanner.name}`}
                >
                  <div className="d-flex align-items-center justify-content-between">
                    <div>
                      <strong>{scanner.name}</strong>
                      {isRecommended && (
                        <span className="badge bg-primary ms-2">Recommended</span>
                      )}
                    </div>
                    {!scanner.available && (
                      <span className="badge bg-danger">Unavailable</span>
                    )}
                  </div>
                  <small className="text-muted d-block mt-1">{scanner.description}</small>
                </label>
              </div>
            );
          })}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="d-flex justify-content-end gap-2">
        {onCancel && (
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onCancel}
            disabled={loading}
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          className="btn btn-primary"
          disabled={loading}
        >
          {loading ? (
            <>
              <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              Starting Scan...
            </>
          ) : (
            <>
              <i className="bi bi-play-circle me-2"></i>
              Start Scan
            </>
          )}
        </button>
      </div>
    </form>
  );
}

export default ScanForm;

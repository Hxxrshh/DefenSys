import React, { useState, useEffect } from 'react';
import { targetAPI } from '../services/api';
import ScanForm from '../components/ScanForm';
import './TargetManager.css';

function TargetManager() {
  const [targets, setTargets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [showScanForm, setShowScanForm] = useState(false);
  const [selectedTarget, setSelectedTarget] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    targetType: 'ip',
    value: '',
  });
  const [error, setError] = useState('');

  useEffect(() => {
    loadTargets();
  }, []);

  const loadTargets = async () => {
    try {
      setLoading(true);
      const data = await targetAPI.getAll();
      setTargets(data);
    } catch (err) {
      console.error('Failed to load targets:', err);
      setError('Failed to load targets');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleAddTarget = async (e) => {
    e.preventDefault();
    setError('');

    try {
      await targetAPI.create({
        name: formData.name,
        target_type: formData.targetType,
        value: formData.value,
      });

      // Reset form and reload
      setFormData({ name: '', targetType: 'ip', value: '' });
      setShowAddForm(false);
      loadTargets();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create target');
    }
  };

  const handleDeleteTarget = async (targetId) => {
    if (!window.confirm('Are you sure you want to delete this target?')) {
      return;
    }

    try {
      await targetAPI.delete(targetId);
      loadTargets();
    } catch (err) {
      console.error('Failed to delete target:', err);
      alert('Failed to delete target');
    }
  };

  const handleScanTarget = (target) => {
    setSelectedTarget(target);
    setShowScanForm(true);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const getTargetTypeIcon = (type) => {
    const icons = {
      ip: 'bi-hdd-network',
      domain: 'bi-globe',
      url: 'bi-link-45deg',
      cidr: 'bi-diagram-3',
    };
    return icons[type] || 'bi-bullseye';
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
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Target Management</h1>
        <button
          className="btn btn-primary"
          onClick={() => setShowAddForm(!showAddForm)}
        >
          <i className="bi bi-plus-circle me-2"></i>
          Add Target
        </button>
      </div>

      {error && (
        <div className="alert alert-danger alert-dismissible fade show" role="alert">
          {error}
          <button
            type="button"
            className="btn-close"
            onClick={() => setError('')}
          ></button>
        </div>
      )}

      {/* Add Target Form */}
      {showAddForm && (
        <div className="card mb-4">
          <div className="card-header">
            <h5 className="mb-0">Add New Target</h5>
          </div>
          <div className="card-body">
            <form onSubmit={handleAddTarget}>
              <div className="row">
                <div className="col-md-4 mb-3">
                  <label htmlFor="name" className="form-label">Target Name *</label>
                  <input
                    type="text"
                    className="form-control"
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    placeholder="e.g., Production Server"
                    required
                  />
                </div>
                <div className="col-md-3 mb-3">
                  <label htmlFor="targetType" className="form-label">Type *</label>
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
                <div className="col-md-5 mb-3">
                  <label htmlFor="value" className="form-label">Value *</label>
                  <input
                    type="text"
                    className="form-control"
                    id="value"
                    name="value"
                    value={formData.value}
                    onChange={handleInputChange}
                    placeholder="e.g., 192.168.1.1"
                    required
                  />
                </div>
              </div>
              <div className="d-flex justify-content-end gap-2">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setShowAddForm(false);
                    setFormData({ name: '', targetType: 'ip', value: '' });
                  }}
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  <i className="bi bi-plus-circle me-2"></i>
                  Add Target
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Targets List */}
      <div className="card">
        <div className="card-header">
          <h5 className="mb-0">Targets ({targets.length})</h5>
        </div>
        <div className="card-body">
          {targets.length === 0 ? (
            <div className="text-center py-5">
              <i className="bi bi-bullseye" style={{ fontSize: '3rem', color: '#ccc' }}></i>
              <p className="text-muted mt-3">No targets yet. Add your first target to get started!</p>
            </div>
          ) : (
            <div className="table-responsive">
              <table className="table table-hover">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Type</th>
                    <th>Value</th>
                    <th>Last Scanned</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {targets.map((target) => (
                    <tr key={target.id}>
                      <td>
                        <strong>{target.name}</strong>
                      </td>
                      <td>
                        <span className="target-type">
                          <i className={`bi ${getTargetTypeIcon(target.target_type)} me-2`}></i>
                          {target.target_type.toUpperCase()}
                        </span>
                      </td>
                      <td>
                        <code>{target.value}</code>
                      </td>
                      <td>{formatDate(target.last_scanned)}</td>
                      <td>
                        <div className="btn-group" role="group">
                          <button
                            className="btn btn-sm btn-primary"
                            onClick={() => handleScanTarget(target)}
                            title="Scan this target"
                          >
                            <i className="bi bi-play-circle"></i>
                          </button>
                          <button
                            className="btn btn-sm btn-danger"
                            onClick={() => handleDeleteTarget(target.id)}
                            title="Delete target"
                          >
                            <i className="bi bi-trash"></i>
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Scan Form Modal */}
      {showScanForm && selectedTarget && (
        <div className="modal show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-lg">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  Scan Target: {selectedTarget.name}
                </h5>
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => {
                    setShowScanForm(false);
                    setSelectedTarget(null);
                  }}
                ></button>
              </div>
              <div className="modal-body">
                <ScanForm
                  preselectedTarget={selectedTarget}
                  onSuccess={() => {
                    setShowScanForm(false);
                    setSelectedTarget(null);
                    loadTargets();
                  }}
                  onCancel={() => {
                    setShowScanForm(false);
                    setSelectedTarget(null);
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default TargetManager;

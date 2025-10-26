import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navigation.css';

function Navigation() {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path ? 'active' : '';
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
      <div className="container-fluid">
        <Link className="navbar-brand" to="/">
          <i className="bi bi-shield-check me-2"></i>
          DefenSys
        </Link>
        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
          aria-controls="navbarNav"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav me-auto">
            <li className="nav-item">
              <Link className={`nav-link ${isActive('/')}`} to="/">
                <i className="bi bi-speedometer2 me-1"></i>
                Dashboard
              </Link>
            </li>
            <li className="nav-item">
              <Link className={`nav-link ${isActive('/targets')}`} to="/targets">
                <i className="bi bi-bullseye me-1"></i>
                Targets
              </Link>
            </li>
            <li className="nav-item">
              <Link className={`nav-link ${isActive('/scans')}`} to="/scans">
                <i className="bi bi-search me-1"></i>
                Scans
              </Link>
            </li>
          </ul>
          <div className="navbar-text">
            <span className="badge bg-success">Phase 1</span>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navigation;

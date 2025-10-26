import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import Navigation from './components/Navigation';
import Footer from './components/Footer';
import Dashboard from './pages/Dashboard';
import TargetManager from './pages/TargetManager';
import ScanResults from './pages/ScanResults';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Navigation />
        <div className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/targets" element={<TargetManager />} />
            <Route path="/scans/:scanId" element={<ScanResults />} />
            <Route path="/scans" element={<ScanResults />} />
          </Routes>
        </div>
        <Footer />
      </div>
    </Router>
  );
}

export default App;

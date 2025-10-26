import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, ArcElement, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend } from 'chart.js';
import { Doughnut, Bar, Line } from 'react-chartjs-2';
import './StatisticalInsights.css';

ChartJS.register(
  ArcElement,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend
);

const StatisticalInsights = ({ scans = [], vulnerabilities = [] }) => {
  const [stats, setStats] = useState({
    totalScans: 0,
    avgScanTime: 0,
    toolEfficiency: {},
    vulnerabilityBreakdown: { Critical: 0, High: 0, Medium: 0, Low: 0 },
    scanTrend: [],
  });

  useEffect(() => {
    calculateStats();
  }, [scans, vulnerabilities]);

  const calculateStats = () => {
    const totalScans = scans.length;
    const avgScanTime = scans.reduce((sum, scan) => {
      const duration = scan.duration || 0;
      return sum + duration;
    }, 0) / (totalScans || 1);

    // Tool efficiency (scans by tool type)
    const toolEfficiency = {};
    scans.forEach(scan => {
      const tool = scan.scan_type || 'Unknown';
      toolEfficiency[tool] = (toolEfficiency[tool] || 0) + 1;
    });

    // Vulnerability breakdown by severity
    const vulnerabilityBreakdown = { Critical: 0, High: 0, Medium: 0, Low: 0 };
    vulnerabilities.forEach(vuln => {
      const severity = vuln.severity || 'Low';
      if (vulnerabilityBreakdown[severity] !== undefined) {
        vulnerabilityBreakdown[severity]++;
      }
    });

    // Scan trend (last 7 days)
    const scanTrend = Array(7).fill(0);
    const today = new Date();
    scans.forEach(scan => {
      const scanDate = new Date(scan.created_at);
      const diffDays = Math.floor((today - scanDate) / (1000 * 60 * 60 * 24));
      if (diffDays >= 0 && diffDays < 7) {
        scanTrend[6 - diffDays]++;
      }
    });

    setStats({ totalScans, avgScanTime, toolEfficiency, vulnerabilityBreakdown, scanTrend });
  };

  // Vulnerability Severity Donut Chart
  const vulnerabilityChartData = {
    labels: ['Critical', 'High', 'Medium', 'Low'],
    datasets: [{
      data: [
        stats.vulnerabilityBreakdown.Critical,
        stats.vulnerabilityBreakdown.High,
        stats.vulnerabilityBreakdown.Medium,
        stats.vulnerabilityBreakdown.Low
      ],
      backgroundColor: [
        'rgba(255, 8, 68, 0.8)',
        'rgba(255, 120, 0, 0.8)',
        'rgba(255, 193, 7, 0.8)',
        'rgba(6, 255, 165, 0.8)'
      ],
      borderColor: [
        '#ff0844',
        '#ff7800',
        '#ffc107',
        '#06ffa5'
      ],
      borderWidth: 2,
    }]
  };

  const vulnerabilityChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: '#e4e6eb',
          padding: 15,
          font: { size: 12, family: "'Inter', sans-serif" }
        }
      },
      tooltip: {
        backgroundColor: '#1a1f2e',
        titleColor: '#00d9ff',
        bodyColor: '#e4e6eb',
        borderColor: '#00d9ff',
        borderWidth: 1,
        padding: 12,
        displayColors: true,
        callbacks: {
          label: (context) => {
            const label = context.label || '';
            const value = context.parsed || 0;
            const total = context.dataset.data.reduce((a, b) => a + b, 0);
            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
            return `${label}: ${value} (${percentage}%)`;
          }
        }
      }
    }
  };

  // Tool Efficiency Bar Chart
  const toolNames = Object.keys(stats.toolEfficiency);
  const toolCounts = Object.values(stats.toolEfficiency);

  const toolChartData = {
    labels: toolNames,
    datasets: [{
      label: 'Scans Completed',
      data: toolCounts,
      backgroundColor: 'rgba(0, 217, 255, 0.8)',
      borderColor: '#00d9ff',
      borderWidth: 2,
    }]
  };

  const toolChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: 'y',
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#1a1f2e',
        titleColor: '#00d9ff',
        bodyColor: '#e4e6eb',
        borderColor: '#00d9ff',
        borderWidth: 1,
        padding: 12,
      }
    },
    scales: {
      x: {
        grid: { color: '#2a3441', borderColor: '#2a3441' },
        ticks: { color: '#8892a6', font: { size: 11 } }
      },
      y: {
        grid: { display: false },
        ticks: { color: '#e4e6eb', font: { size: 12, weight: '500' } }
      }
    }
  };

  // Scan Trend Line Chart
  const days = ['6 days ago', '5 days ago', '4 days ago', '3 days ago', '2 days ago', 'Yesterday', 'Today'];
  
  const trendChartData = {
    labels: days,
    datasets: [{
      label: 'Scans per Day',
      data: stats.scanTrend,
      borderColor: '#06ffa5',
      backgroundColor: 'rgba(6, 255, 165, 0.2)',
      borderWidth: 3,
      tension: 0.4,
      fill: true,
      pointBackgroundColor: '#06ffa5',
      pointBorderColor: '#0f1419',
      pointBorderWidth: 2,
      pointRadius: 5,
      pointHoverRadius: 7,
    }]
  };

  const trendChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#1a1f2e',
        titleColor: '#00d9ff',
        bodyColor: '#e4e6eb',
        borderColor: '#06ffa5',
        borderWidth: 1,
        padding: 12,
      }
    },
    scales: {
      x: {
        grid: { color: '#2a3441', borderColor: '#2a3441' },
        ticks: { color: '#8892a6', font: { size: 10 } }
      },
      y: {
        grid: { color: '#2a3441', borderColor: '#2a3441' },
        ticks: { 
          color: '#8892a6', 
          font: { size: 11 },
          stepSize: 1 
        }
      }
    }
  };

  return (
    <div className="statistical-insights">
      <div className="insights-header">
        <i className="bi bi-graph-up-arrow"></i>
        <h3>Statistical Insights</h3>
        <span className="insights-badge">Live Data</span>
      </div>

      {/* Quick Stats Summary */}
      <div className="quick-stats">
        <div className="stat-mini">
          <i className="bi bi-bar-chart-fill"></i>
          <div className="stat-mini-info">
            <span className="stat-mini-value">{stats.totalScans}</span>
            <span className="stat-mini-label">Total Scans</span>
          </div>
        </div>
        <div className="stat-mini">
          <i className="bi bi-clock-history"></i>
          <div className="stat-mini-info">
            <span className="stat-mini-value">{stats.avgScanTime.toFixed(1)}s</span>
            <span className="stat-mini-label">Avg Scan Time</span>
          </div>
        </div>
        <div className="stat-mini">
          <i className="bi bi-shield-exclamation"></i>
          <div className="stat-mini-info">
            <span className="stat-mini-value">
              {Object.values(stats.vulnerabilityBreakdown).reduce((a, b) => a + b, 0)}
            </span>
            <span className="stat-mini-label">Vulnerabilities</span>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="charts-grid">
        {/* Vulnerability Breakdown */}
        <div className="chart-card">
          <div className="chart-card-header">
            <h4>Vulnerability Distribution</h4>
            <i className="bi bi-info-circle chart-info" title="Shows how vulnerabilities are categorized by risk level"></i>
          </div>
          <div className="chart-explanation">
            <p>🔍 <strong>What this means:</strong> This shows how many security issues were found at each danger level.</p>
          </div>
          <div className="chart-container">
            <Doughnut data={vulnerabilityChartData} options={vulnerabilityChartOptions} />
          </div>
        </div>

        {/* Tool Efficiency */}
        <div className="chart-card">
          <div className="chart-card-header">
            <h4>Tool Usage Comparison</h4>
            <i className="bi bi-info-circle chart-info" title="Compares how many scans each tool has performed"></i>
          </div>
          <div className="chart-explanation">
            <p>🛠️ <strong>What this means:</strong> Which security tools have been used most often to check your systems.</p>
          </div>
          <div className="chart-container">
            {toolNames.length > 0 ? (
              <Bar data={toolChartData} options={toolChartOptions} />
            ) : (
              <div className="no-data">No tool data available yet</div>
            )}
          </div>
        </div>

        {/* Scan Trend */}
        <div className="chart-card chart-card-wide">
          <div className="chart-card-header">
            <h4>Scan Activity Trend</h4>
            <i className="bi bi-info-circle chart-info" title="Shows scanning activity over the past week"></i>
          </div>
          <div className="chart-explanation">
            <p>📈 <strong>What this means:</strong> How often security scans have been running over the last 7 days.</p>
          </div>
          <div className="chart-container">
            <Line data={trendChartData} options={trendChartOptions} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatisticalInsights;

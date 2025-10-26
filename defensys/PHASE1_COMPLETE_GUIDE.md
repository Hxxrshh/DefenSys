# DefenSys Phase 1 - Complete Setup and Testing Guide

## Overview
DefenSys Phase 1 is now complete with comprehensive backend infrastructure and React frontend. This guide covers installation, setup, testing, and usage.

## Architecture

### Backend Stack
- **Framework**: FastAPI 0.104.0+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Real-time**: WebSocket, RabbitMQ, Redis
- **Scanners**: Nmap, Nuclei, Nikto, OWASP ZAP, Snyk, Trivy, Semgrep, Bandit

### Frontend Stack
- **Framework**: React 18.2.0
- **UI**: Bootstrap 5.3
- **Routing**: React Router 6.14
- **Charts**: Chart.js 4.3
- **HTTP Client**: Axios

## Prerequisites

### System Requirements
- Python 3.9+
- Node.js 16+
- PostgreSQL 12+
- Redis 6+
- RabbitMQ 3.9+

### Security Scanners (Install as needed)
```bash
# Nmap (required for Phase 1)
# Windows: Download from https://nmap.org/download.html
# Linux: sudo apt install nmap

# Nuclei (optional)
go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest

# Nikto (optional)
# Windows: Download from https://github.com/sullo/nikto
# Linux: sudo apt install nikto

# OWASP ZAP (optional)
# Download from https://www.zaproxy.org/download/
```

## Installation

### 1. Database Setup

```bash
# Create PostgreSQL database
psql -U postgres
CREATE DATABASE defensys;
CREATE USER defensys_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE defensys TO defensys_user;
\q
```

### 2. Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
# Create .env file
DATABASE_URL=postgresql://defensys_user:your_password@localhost/defensys
REDIS_URL=redis://localhost:6379
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# Run database migration
python migrate_database.py

# Start backend server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install Node.js dependencies
npm install

# Start development server
npm start
```

The frontend will open at http://localhost:3000 and proxy API requests to http://localhost:8000.

## Testing Phase 1 Features

### Step 1: Verify Scanner Availability

**API Test:**
```bash
curl http://localhost:8000/api/v1/scanners/available
```

**Expected Response:**
```json
{
  "scanners": [
    {
      "name": "Nmap",
      "available": true,
      "description": "Network mapper and port scanner"
    },
    {
      "name": "Nuclei",
      "available": true,
      "description": "Vulnerability scanner using templates"
    }
    // ... more scanners
  ]
}
```

### Step 2: Create a Target

**Via API:**
```bash
curl -X POST http://localhost:8000/api/v1/targets \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Server",
    "target_type": "ip",
    "value": "192.168.1.1"
  }'
```

**Via UI:**
1. Navigate to http://localhost:3000/targets
2. Click "Add Target"
3. Enter target details
4. Click "Add Target"

### Step 3: Start a Scan

**Via API:**
```bash
curl -X POST http://localhost:8000/api/v1/scans/start \
  -H "Content-Type: application/json" \
  -d '{
    "target_value": "192.168.1.1",
    "target_type": "ip",
    "scan_type": "quick",
    "scan_tools": ["Nmap"]
  }'
```

**Expected Response:**
```json
{
  "scan_id": 1,
  "status": "pending",
  "message": "Scan started successfully"
}
```

**Via UI:**
1. Navigate to Dashboard or Targets page
2. Click "New Scan" or scan icon on target
3. Configure scan options
4. Click "Start Scan"

### Step 4: Monitor Progress

**Via API:**
```bash
curl http://localhost:8000/api/v1/scans/1/progress
```

**Expected Response:**
```json
{
  "scan_id": 1,
  "status": "running",
  "progress": 45.5,
  "current_stage": "Running Nmap scan...",
  "started_at": "2024-01-15T10:30:00"
}
```

**Via UI:**
1. Navigate to scan results page
2. Watch real-time progress bar update
3. WebSocket updates progress automatically

### Step 5: View Results

**Via API:**
```bash
curl http://localhost:8000/api/v1/scans/1/results
```

**Expected Response:**
```json
{
  "scan": {
    "id": 1,
    "status": "completed",
    "scan_type": "quick",
    "progress": 100
  },
  "vulnerabilities": [
    {
      "id": 1,
      "severity": "high",
      "title": "Open SSH Port",
      "description": "SSH service exposed on port 22",
      "target_host": "192.168.1.1",
      "target_port": 22
    }
  ],
  "findings": [
    {
      "id": 1,
      "finding_type": "open_port",
      "host": "192.168.1.1",
      "port": 22,
      "service": "ssh"
    }
  ],
  "summary": {
    "total_vulnerabilities": 5,
    "critical_count": 0,
    "high_count": 2,
    "medium_count": 2,
    "low_count": 1,
    "total_findings": 10
  }
}
```

**Via UI:**
1. Results appear automatically when scan completes
2. View vulnerabilities with severity badges
3. Filter by severity or scanner
4. View findings in table format

## API Documentation

### Target Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/targets` | POST | Create new target |
| `/api/v1/targets` | GET | List all targets |
| `/api/v1/targets/{id}` | GET | Get target details |
| `/api/v1/targets/{id}` | PUT | Update target |
| `/api/v1/targets/{id}` | DELETE | Delete target |

### Scan Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/scans/start` | POST | Start new scan |
| `/api/v1/scans/{id}/progress` | GET | Get scan progress |
| `/api/v1/scans/{id}/results` | GET | Get complete results |
| `/api/v1/scans` | GET | List all scans |

### Vulnerability Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/vulnerabilities` | GET | List vulnerabilities |
| `/api/v1/vulnerabilities/{id}` | GET | Get vulnerability details |

Query parameters: `scan_id`, `severity`, `scanner_name`

### Enumeration

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/enumerate/discover` | POST | Discover hosts on network |
| `/api/v1/enumerate/ports` | POST | Enumerate ports on target |

### WebSocket

| Endpoint | Protocol | Description |
|----------|----------|-------------|
| `/ws` | WebSocket | Real-time scan progress updates |

## Scan Types

### Quick Scan
- **Duration**: 2-5 minutes
- **Ports**: Top 100 ports
- **Tools**: Nmap (quick scan)
- **Use Case**: Fast reconnaissance

### Default Scan
- **Duration**: 5-15 minutes
- **Ports**: Top 1000 ports
- **Tools**: Nmap + Nuclei
- **Use Case**: Standard security assessment

### Full Scan
- **Duration**: 30-60+ minutes
- **Ports**: All 65535 ports
- **Tools**: All available scanners
- **Use Case**: Comprehensive security audit

### Network Scan
- **Duration**: 10-20 minutes
- **Focus**: Network infrastructure
- **Tools**: Nmap (intensive), network enumeration
- **Use Case**: Infrastructure discovery

### Web Scan
- **Duration**: 15-30 minutes
- **Focus**: Web applications
- **Tools**: ZAP, Nuclei, Nikto
- **Use Case**: Web vulnerability assessment

## Troubleshooting

### Scanner Not Available

**Issue**: Scanner shows as unavailable in API response

**Solution**:
1. Verify scanner is installed: `nmap --version`, `nuclei -version`, etc.
2. Ensure scanner is in system PATH
3. Check scanner permissions (Linux: `chmod +x /path/to/scanner`)

### Database Connection Error

**Issue**: Cannot connect to PostgreSQL

**Solution**:
1. Verify PostgreSQL is running: `pg_isready`
2. Check credentials in .env file
3. Ensure database exists: `psql -U postgres -l`

### Frontend API Connection Error

**Issue**: Frontend cannot reach backend API

**Solution**:
1. Verify backend is running on port 8000
2. Check proxy setting in `frontend/package.json`
3. Ensure CORS is enabled in `backend/api/main.py`

### WebSocket Connection Failed

**Issue**: Real-time updates not working

**Solution**:
1. Check WebSocket endpoint: `ws://localhost:8000/ws`
2. Verify no firewall blocking WebSocket connections
3. Check browser console for WebSocket errors

### Scan Stuck at 0%

**Issue**: Scan starts but progress never updates

**Solution**:
1. Check scanner is actually installed and working
2. Verify target is reachable: `ping <target>`
3. Check backend logs for errors
4. Ensure async task execution is working

## Performance Optimization

### Database Indexing
```sql
-- Add indexes for faster queries
CREATE INDEX idx_vulnerabilities_scan_id ON vulnerabilities(scan_id);
CREATE INDEX idx_vulnerabilities_severity ON vulnerabilities(severity);
CREATE INDEX idx_findings_scan_id ON findings(scan_id);
CREATE INDEX idx_scans_status ON scans(status);
```

### Concurrent Scans
- By default, orchestrator runs scanners sequentially
- For parallel execution, modify `ScanOrchestrator._execute_scan()` to use `asyncio.gather()`

### Result Caching
- Consider caching scan results in Redis for faster retrieval
- Implement in `crud.py` for `get_scan_results()`

## Next Steps - Phase 2 & 3

### Phase 2: Report Aggregation & Intelligence
- [ ] Report generation (PDF, HTML, JSON)
- [ ] Historical trend analysis
- [ ] Risk scoring and prioritization
- [ ] Compliance mapping (OWASP, CWE, etc.)
- [ ] Scheduled scanning

### Phase 3: RAG Chatbot
- [ ] LLM integration (OpenAI, LLaMA, etc.)
- [ ] Vector database for embeddings
- [ ] Natural language query interface
- [ ] Vulnerability explanation and remediation suggestions
- [ ] Interactive threat analysis

## Support

For issues or questions:
1. Check this guide first
2. Review API documentation: http://localhost:8000/docs
3. Check application logs for errors
4. Verify all prerequisites are installed

## Security Notes

⚠️ **Important Security Considerations:**
1. Never scan targets without permission
2. Use strong database passwords in production
3. Enable authentication for API endpoints
4. Use HTTPS in production
5. Limit scanner execution permissions
6. Implement rate limiting for API endpoints
7. Sanitize all user inputs

## License

DefenSys Phase 1 - Internal Use Only

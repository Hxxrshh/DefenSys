# 🚀 DefenSys Complete Deployment Guide

## 📋 Overview

DefenSys is now a **fully containerized, enterprise-grade security platform** with comprehensive SAST, DAST, and dependency scanning capabilities.

### 🛠️ Architecture Components

```
│                   DefenSys Platform             │
├─────────────────────────────────────────────────┤
│  Frontend (React + Nginx)     :3000             │
│  ├── User-friendly Interface                    │
│  ├── Scan Results Dashboard                     │
│  └── Real-time Progress Tracking               │
├─────────────────────────────────────────────────┤
### Expected Result
When services are running locally (or reachable via configured hosts), you should be able to:

- Reach the frontend at http://localhost:3000 (if running the frontend dev server)
- Reach the API at http://localhost:8000 and open the OpenAPI docs at /docs
- Connect to your database on the host/port configured in `DATABASE_URL`

For service-specific status and logs, consult the local service manager you used to start them (systemd, Docker, or the process running the service).
│  API Backend (FastAPI)        :8000             │
│  ├── 13 Security Scanners                      │
│  ├── User-friendly Abstraction                 │
│  └── RESTful API Endpoints                     │
├─────────────────────────────────────────────────┤
│  Database (PostgreSQL)        :5432             │
│  ├── Scan Results Storage                      │
│  ├── Project Management                        │
│  └── User Preferences                          │
├─────────────────────────────────────────────────┤
│  Cache (Redis)                :6379             │
#### 1. Port Already in Use
```bash
# Check what's using the port (Windows PowerShell example)
Get-NetTCPConnection -LocalPort 8000 | Format-Table -AutoSize

# Kill the process by PID (PowerShell)
Stop-Process -Id <PID> -Force

# Or change the port when starting the service (for uvicorn use --port)
uvicorn api.main:app --host 0.0.0.0 --port 8001
```
│  ├── Session Management                        │
│  ├── Scan Queue                                │
│  └── Real-time Updates                         │
├─────────────────────────────────────────────────┤
│  SonarQube (Code Quality)     :9000             │
│  ├── Enterprise Analytics                      │
│  ├── Technical Debt Tracking                   │
│  └── Quality Gates                             │
└─────────────────────────────────────────────────┘
```

#### 2. Local build / tool install issues
```bash
# If dependency installs fail while building or installing locally, try cleaning pip cache and reinstalling
python -m pip cache purge
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt --no-cache-dir

# Check disk space (Windows PowerShell)
Get-PSDrive -PSProvider FileSystem | Select-Object Name, @{n='Free(GB)';e={[math]::Round($_.Free/1GB,2)}}, @{n='Used(GB)';e={[math]::Round(($_.Used)/1GB,2)}}
```
---

## 🔧 Installed Security Tools (13 Total)

### 📊 Static Analysis (SAST) - 9 Tools
| Tool | Language | Purpose | Enterprise |
|------|----------|---------|------------|
| **Bandit** | Python | Security linting | ✅ |
| **Semgrep** | Multi-lang | Advanced SAST | ✅ |
#### 3. Database Connection Issues
```bash
# Restart your local Postgres service (platform dependent)
# Example (systemctl on Linux):
sudo systemctl restart postgresql

# Check DB readiness using psql
psql "$DATABASE_URL" -c "SELECT version();"
```
| **Snyk** | Multi-lang | Vulnerability detection | ✅ |
| **Trivy** | Containers | Container/filesystem scanning | ✅ |
| **pip-audit** | Python | Dependency vulnerabilities | ✅ |
| **Safety** | Python | Dependency security | ✅ |
| **GitLeaks** | Git | Secret detection | ✅ |
| **npm audit** | Node.js | NPM vulnerabilities | ✅ |
| **yarn audit** | Node.js | Yarn vulnerabilities | ✅ |

### 🌐 Dynamic Analysis (DAST) - 4 Tools
| Tool | Purpose | Target | Complexity |
#### 4. Scanner Tools Not Found
```bash
# Install scanner CLIs locally or ensure they are available on PATH
# Example checks (Windows PowerShell)
Get-Command snyk -ErrorAction SilentlyContinue
Get-Command trivy -ErrorAction SilentlyContinue
Get-Command semgrep -ErrorAction SilentlyContinue

# Install if missing:
# npm install -g snyk
# curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
# pip install semgrep
```
|------|---------|--------|------------|
| **OWASP ZAP** | Web app testing | Running apps | High |
| **Nuclei** | Template-based scanning | Web services | Medium |
| **Nikto** | Web server scanning | Web servers | Medium |
| **SQLMap** | SQL injection testing | Database endpoints | High |

---

## 🚀 Quick Start (5 Minutes)

### 1. Prerequisites
### Resource Monitoring
Use your OS tools to monitor resource usage, for example:

- Windows: Task Manager or Resource Monitor
- Linux: top, htop, vmstat, iotop
- Disk usage: df -h (Linux/macOS) or Get-PSDrive (PowerShell)

Clean up temporary files and caches according to your OS tooling.
```bash
# Required software for local development
- Python 3.9+ (recommended)
- PostgreSQL (or use a local SQLite for quickly testing)
- Redis (optional for caching/queues)
- RabbitMQ (optional for real-time monitoring)
- Git
- Node.js & npm (for frontend development)
- 8GB+ RAM recommended
- 10GB+ disk space
### Scaling
To scale the API, run multiple instances behind a load balancer or use your platform's auto-scaling features. Example approaches:

- Run multiple uvicorn/gunicorn workers and put an NGINX or other reverse proxy in front
- Deploy behind a cloud load balancer and use a process manager or container orchestrator

Ensure session/state is stored in Redis or another shared store when scaling horizontally.
```

### 2. Clone & Run Locally
```bash
# Clone the repository
git clone https://github.com/Hxxrshh/Devsyns.git
cd Devsyns/defensys

# Run backend locally (ensure DATABASE_URL points to a running Postgres instance or use SQLite in tests)
cd backend
python -m pip install -r requirements.txt
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Run frontend locally (development mode)
cd ../frontend
npm install
npm start
```

### 3. Access the Platform
```bash
# Frontend Dashboard
open http://localhost:3000

# API Documentation  
open http://localhost:8000/docs

# SonarQube Dashboard
open http://localhost:9000
```

---

## 📊 Service Health Check

### Verify Services (local)
```bash
# Check API health
curl http://localhost:8000/health

# Check database connection (example using psql against a running Postgres)
psql "$DATABASE_URL" -c "SELECT version();"

# Check Redis (if running locally)
redis-cli ping
```

### Expected Output
```
     Name                   Command                  State           Ports
--------------------------------------------------------------------------------
defensys_api        uvicorn api.main:app ...         Up      0.0.0.0:8000->8000/tcp
defensys_db         docker-entrypoint.sh postgres    Up      0.0.0.0:5432->5432/tcp
defensys_frontend   nginx -g daemon off;             Up      0.0.0.0:3000->3000/tcp
defensys_redis      docker-entrypoint.sh redis ...   Up      0.0.0.0:6379->6379/tcp
defensys_sonarqube  bin/run.sh                       Up      0.0.0.0:9000->9000/tcp
defensys_trivy      trivy server --listen ...        Up      0.0.0.0:4954->4954/tcp
```

---

## 🎯 Usage Examples

### 1. Simple Web Security Scan
```bash
curl -X POST "http://localhost:8000/api/simple-scan" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-website.com",
    "category": "web_application_testing"
  }'
```

### 2. Complete Security Audit
```bash
curl -X POST "http://localhost:8000/api/simple-scan" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "/path/to/your/code",
    "category": "full_security_audit"
  }'
```

### 3. Container Security Scan
```bash
curl -X POST "http://localhost:8000/api/simple-scan" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "/path/to/dockerfile",
    "category": "container_security"
  }'
```

---

## 📈 Monitoring & Maintenance

### Application Logs
```bash
# Backend logs are printed to stdout when running uvicorn locally
# For production deployments, run with a process manager and capture logs (systemd, supervisord, etc.)

# Postgres logs depend on your DB installation and location
# Redis logs depend on your Redis installation
```

### Database Backup
```bash
# Create backup using local psql
pg_dump -U defensys_user -h localhost -d defensys_db > backup_$(date +%Y%m%d).sql

# Restore backup
psql -U defensys_user -h localhost -d defensys_db < backup_20240920.sql
```

### Resource Monitoring
```bash
# Container resource usage
docker stats

# Disk usage
docker system df

# Clean up old images/containers
docker system prune -a
```

---

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Database
DATABASE_URL=postgresql://defensys_user:defensys_password@db:5432/defensys_db

# Redis
REDIS_URL=redis://redis:6379

# API Settings
SECRET_KEY=your-secret-key-here
DEBUG=False

# Scanner Settings
SNYK_TOKEN=your-snyk-token
NUCLEI_TEMPLATES_PATH=/opt/nuclei-templates
```

### Custom Scanner Configuration
```python
# Add custom scanner rules
# File: backend/scanners/custom_rules.py

class CustomSecurityScanner(Scanner):
    def scan(self, path: str) -> List[dict]:
        # Your custom security logic here
        return vulnerabilities
```

---

## 🛠️ Development Setup

### Local Development
```bash
# Run database and Redis using your local installations or managed services

# Run API locally for development
cd backend
pip install -r requirements.txt
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Run frontend locally
cd ../frontend
npm install
npm start
```

### Testing
```bash
# Run all tests
cd backend
python -m pytest tests/ -v

# Run specific test files
python -m pytest tests/test_user_friendly.py -v
python -m pytest tests/test_api.py -v
```

---

## 🚨 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
netstat -tulpn | grep :8000

# Kill the process
sudo kill -9 <PID>

# Or use different ports
docker-compose up --scale api=1 -d
```

#### 2. Docker Build Fails
```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache

# Check disk space
df -h
```

#### 3. Database Connection Issues
```bash
# Reset database
docker-compose down -v
docker-compose up db -d

# Wait for DB to be ready
docker-compose exec db pg_isready -U defensys_user
```

#### 4. Scanner Tools Not Found
```bash
# Rebuild container with tools
docker-compose build --no-cache api

# Check tool installation
docker-compose exec api which snyk
docker-compose exec api which trivy
docker-compose exec api which semgrep
```

---

## 🔒 Security Considerations

### Production Deployment
1. **Change default passwords** in docker-compose.yml
2. **Use environment variables** for sensitive data
3. **Enable TLS/SSL** for external access
4. **Set up firewall rules** to restrict access
5. **Regular security updates** for base images

### Network Security
```yaml
# Production docker-compose.yml additions
services:
  api:
    networks:
      - internal
  frontend:
    networks:
      - internal
      - external
    
networks:
  internal:
    internal: true
  external:
```

---

## 📊 Performance Optimization

### Resource Allocation
```yaml
# Optimized service resources
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### Scaling
```bash
# Scale API service
docker-compose up --scale api=3 -d

# Load balancer configuration needed for multiple API instances
```

---

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Source Code**: https://github.com/Hxxrshh/Devsyns
- **Issue Tracking**: https://github.com/Hxxrshh/Devsyns/issues
- **Security Guidelines**: See ENHANCED_SECURITY_TOOLS_GUIDE.md

---

## 🏆 Success Metrics

Your DefenSys platform is successfully deployed when:

✅ All 6 containers are running  
✅ Frontend accessible at :3000  
✅ API responding at :8000  
✅ All 13 security scanners available  
✅ Database connectivity confirmed  
✅ Sample scans completing successfully  

**Congratulations! You now have an enterprise-grade security scanning platform! 🚀**
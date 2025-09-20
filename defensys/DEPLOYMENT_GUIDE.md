# 🚀 DefenSys Complete Deployment Guide

## 📋 Overview

DefenSys is now a **fully containerized, enterprise-grade security platform** with comprehensive SAST, DAST, and dependency scanning capabilities.

### 🛠️ Architecture Components

```
┌─────────────────────────────────────────────────┐
│                   DefenSys Platform             │
├─────────────────────────────────────────────────┤
│  Frontend (React + Nginx)     :3000             │
│  ├── User-friendly Interface                    │
│  ├── Scan Results Dashboard                     │
│  └── Real-time Progress Tracking               │
├─────────────────────────────────────────────────┤
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

---

## 🔧 Installed Security Tools (13 Total)

### 📊 Static Analysis (SAST) - 9 Tools
| Tool | Language | Purpose | Enterprise |
|------|----------|---------|------------|
| **Bandit** | Python | Security linting | ✅ |
| **Semgrep** | Multi-lang | Advanced SAST | ✅ |
| **Snyk** | Multi-lang | Vulnerability detection | ✅ |
| **Trivy** | Containers | Container/filesystem scanning | ✅ |
| **pip-audit** | Python | Dependency vulnerabilities | ✅ |
| **Safety** | Python | Dependency security | ✅ |
| **GitLeaks** | Git | Secret detection | ✅ |
| **npm audit** | Node.js | NPM vulnerabilities | ✅ |
| **yarn audit** | Node.js | Yarn vulnerabilities | ✅ |

### 🌐 Dynamic Analysis (DAST) - 4 Tools
| Tool | Purpose | Target | Complexity |
|------|---------|--------|------------|
| **OWASP ZAP** | Web app testing | Running apps | High |
| **Nuclei** | Template-based scanning | Web services | Medium |
| **Nikto** | Web server scanning | Web servers | Medium |
| **SQLMap** | SQL injection testing | Database endpoints | High |

---

## 🚀 Quick Start (5 Minutes)

### 1. Prerequisites
```bash
# Required software
- Docker & Docker Compose
- Git
- 8GB+ RAM recommended
- 10GB+ disk space
```

### 2. Clone & Deploy
```bash
# Clone the repository
git clone https://github.com/Hxxrshh/Devsyns.git
cd Devsyns/defensys

# Start all services (this will take 5-10 minutes on first run)
docker-compose up --build -d

# Check service status
docker-compose ps
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

### Verify All Services
```bash
# Check all containers are running
docker-compose ps

# Check API health
curl http://localhost:8000/health

# Check database connection
docker-compose exec db psql -U defensys_user -d defensys_db -c "SELECT version();"

# Check Redis
docker-compose exec redis redis-cli ping
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

### Container Logs
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f api
docker-compose logs -f db
docker-compose logs -f frontend
```

### Database Backup
```bash
# Create backup
docker-compose exec db pg_dump -U defensys_user defensys_db > backup_$(date +%Y%m%d).sql

# Restore backup
docker-compose exec -T db psql -U defensys_user defensys_db < backup_20240920.sql
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
# Start only database and Redis
docker-compose up db redis -d

# Run API locally for development
cd backend
pip install -r requirements.txt
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Run frontend locally
cd frontend
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
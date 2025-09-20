# DefenSys Advanced Security Scanners Setup Guide

DefenSys now includes powerful industry-standard security scanning tools! This guide will help you install and configure the advanced scanners for maximum security coverage.

## 🛡️ Available Scanners

### Basic Scanners (Always Available)
- **Bandit** - Python SAST scanner
- **pip-audit** - Python dependency vulnerability scanner  
- **Secret Scanner** - Custom secret detection

### Advanced Scanners (Require Installation)
- **Snyk** - Multi-purpose security platform
- **Trivy** - Container and filesystem vulnerability scanner
- **Semgrep** - Advanced SAST with custom rules

## 📦 Installation Instructions

### 1. Snyk Installation

**Method 1: npm (Recommended)**
```bash
npm install -g snyk
snyk --version
```

**Method 2: Binary Download**
```bash
# Linux/macOS
curl -Lo snyk https://github.com/snyk/snyk/releases/latest/download/snyk-linux
chmod +x snyk
sudo mv snyk /usr/local/bin/

# Windows
# Download from: https://github.com/snyk/snyk/releases/latest
```

**Authentication:**
```bash
snyk auth
# Or set token directly:
export SNYK_TOKEN=your-token-here
```

### 2. Trivy Installation

**Method 1: Installation Script (Linux/macOS)**
```bash
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
trivy --version
```

**Method 2: Package Managers**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install wget apt-transport-https gnupg lsb-release
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt-get update
sudo apt-get install trivy

# macOS (Homebrew)
brew install trivy

# Windows (Chocolatey)
choco install trivy
```

**Method 3: Docker**
```bash
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v $PWD:/tmp/.cache/ aquasec/trivy:latest
```

### 3. Semgrep Installation

**Method 1: pip (Recommended)**
```bash
pip install semgrep
semgrep --version
```

**Method 2: pipx**
```bash
pipx install semgrep
```

**Method 3: Docker**
```bash
docker run --rm -v $(pwd):/src returntocorp/semgrep:latest
```

## 🚀 Quick Start

### Running Basic Scans
```bash
# API endpoint
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{
    "repository_url": "https://github.com/user/repo",
    "scan_types": ["basic"]
  }'
```

### Running Advanced Scans
```bash
# Full scan with all tools
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{
    "repository_url": "https://github.com/user/repo", 
    "scan_types": ["full"]
  }'

# Advanced scanners only
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{
    "repository_url": "https://github.com/user/repo",
    "scan_types": ["advanced"]
  }'

# Specific scanner
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{
    "repository_url": "https://github.com/user/repo",
    "scan_types": ["snyk"]
  }'
```

### Check Scanner Availability
```bash
curl http://localhost:8000/api/scanners
```

### Get Scan Recommendations
```bash
curl -X POST http://localhost:8000/api/scan/recommendations \
  -H "Content-Type: application/json" \
  -d '{"path": "/path/to/project"}'
```

## ⚙️ Scanner Configuration

### Snyk Configuration
Create `~/.snyk` file:
```yaml
version: v1.0.0
ignore:
  SNYK-JS-LODASH-567746:
    - '*':
        reason: False positive
        expires: 2024-12-31T23:59:59.999Z
```

### Trivy Configuration
Create `trivy.yaml`:
```yaml
timeout: 10m
security-checks:
  - vuln
  - secret
  - config
severity:
  - CRITICAL
  - HIGH
  - MEDIUM
```

### Semgrep Configuration
Create `.semgrepignore`:
```
node_modules/
*.min.js
*.min.css
.git/
__pycache__/
```

## 🔧 Advanced Usage

### Custom Semgrep Rules
```python
# In your scan request
{
  "repository_url": "https://github.com/user/repo",
  "scan_types": ["semgrep"],
  "semgrep_config": "/path/to/custom/rules.yml",
  "language": "python"
}
```

### Trivy Container Scanning
```python
{
  "repository_url": "https://github.com/user/repo",
  "scan_types": ["trivy"],
  "trivy_target_type": "image",
  "image_name": "my-app:latest"
}
```

### Snyk Specific Scans
```python
{
  "repository_url": "https://github.com/user/repo", 
  "scan_types": ["snyk"],
  "snyk_scan_type": "code"  # or "oss", "container", "iac"
}
```

## 🐛 Troubleshooting

### Common Issues

**Snyk Authentication Error**
```bash
# Re-authenticate
snyk auth
# Or check token
echo $SNYK_TOKEN
```

**Trivy Database Update Error**
```bash
# Clear cache and update
trivy clean --all
trivy image --download-db-only
```

**Semgrep Rate Limiting**
```bash
# Use local rules instead of registry
semgrep --config=auto --exclude=node_modules .
```

**Scanner Not Found**
```bash
# Check if scanner is in PATH
which snyk
which trivy  
which semgrep

# Install missing scanners
npm install -g snyk
pip install semgrep
```

### Performance Optimization

**Parallel Scanning**
```python
{
  "scan_types": ["full"],
  "parallel": true,
  "max_workers": 3,
  "scanner_timeout": 600
}
```

**Scanner-Specific Timeouts**
- Snyk: 5 minutes per scan type
- Trivy: 10 minutes for filesystem, 15 minutes for images
- Semgrep: 5 minutes per config

## 📊 Scanner Comparison

| Scanner | Languages | Strength | Use Case |
|---------|-----------|----------|----------|
| Bandit | Python | Python security | Python projects |
| pip-audit | Python | Dependencies | Python dependencies |
| Snyk | Multi | Commercial accuracy | Enterprise security |
| Trivy | Multi | Container focus | DevOps/containers |
| Semgrep | Multi | Custom rules | Advanced SAST |
| Secret Scanner | All | Secrets | Credential scanning |

## 🎯 Best Practices

1. **Start with basic scans** for new projects
2. **Use full scans** for production deployments
3. **Configure exclusions** to reduce false positives
4. **Set up authentication** for Snyk premium features
5. **Regular updates** of scanner databases
6. **Custom rules** for organization-specific requirements

## 🔗 Additional Resources

- [Snyk Documentation](https://docs.snyk.io/)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [Semgrep Documentation](https://semgrep.dev/docs/)
- [DefenSys API Documentation](http://localhost:8000/docs)

---

**Pro Tip:** Run `curl http://localhost:8000/api/scanners` to check which scanners are currently available in your environment!
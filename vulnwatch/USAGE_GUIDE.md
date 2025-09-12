# 🛡️ DefenSys - Complete Usage Guide

## 🎯 **How to Scan Websites/Repositories for Vulnerabilities**

### **Step 1: Access the DefenSys Dashboard**
Open your browser and go to: **http://localhost:8081**

### **Step 2: Start a New Scan**

#### **Method A: Web Interface (Easiest)**
1. Click the **"Start New Scan"** button on the dashboard
2. Enter the repository URL (e.g., `https://github.com/username/repository`)
3. Select scan types:
   - ✅ **SAST** - Static code analysis
   - ✅ **SECRET** - Credential detection  
   - ✅ **DEPENDENCY** - Package vulnerabilities
4. Click **"Start Scan"**
5. Monitor progress in real-time

#### **Method B: API Call**
```bash
# Windows PowerShell
Invoke-WebRequest -Uri "http://localhost:5000/api/scans" -Method POST -ContentType "application/json" -Body '{"repo_url": "https://github.com/WebGoat/WebGoat", "scan_types": ["SAST", "SECRET", "DEPENDENCY"]}'

# Linux/Mac curl
curl -X POST http://localhost:5000/api/scans \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/WebGoat/WebGoat", "scan_types": ["SAST", "SECRET", "DEPENDENCY"]}'
```

#### **Method C: Python Script**
```python
import requests

response = requests.post('http://localhost:5000/api/scans', 
    json={
        'repo_url': 'https://github.com/WebGoat/WebGoat',
        'scan_types': ['SAST', 'SECRET', 'DEPENDENCY']
    }
)
print(response.json())
```

### **Step 3: View Results**

#### **Dashboard View:**
- Navigate to **http://localhost:8081**
- See vulnerability counts by severity
- Browse detailed findings
- Acknowledge or track vulnerabilities

#### **API Access:**
```bash
# Get all vulnerabilities
curl http://localhost:5000/api/vulnerabilities

# Filter by severity
curl http://localhost:5000/api/vulnerabilities?severity=CRITICAL

# Get scan details
curl http://localhost:5000/api/scans
```

## 🔍 **What DefenSys Detects**

### **🐛 SAST (Static Application Security Testing)**
- **SQL Injection** vulnerabilities
- **Cross-Site Scripting (XSS)** flaws
- **Hardcoded passwords/secrets** in code
- **Command injection** vulnerabilities
- **Weak cryptographic** implementations
- **Insecure file operations**
- **Authentication bypass** issues

### **🔐 Secret Detection**
- **AWS Access Keys** (`AKIA...`)
- **GitHub Personal Access Tokens** (`ghp_...`)
- **API Keys** (Stripe, SendGrid, etc.)
- **Database connection strings**
- **Private SSH/SSL keys**
- **JWT tokens** 
- **Slack webhooks**
- **Password patterns** in configuration

### **📦 Dependency Vulnerabilities**
- **Known CVEs** in packages
- **Outdated libraries** with security fixes
- **Vulnerable versions** of dependencies
- **Transitive dependency** issues
- **License compliance** problems
- **Package integrity** verification

## 🎯 **Example Vulnerable Repositories to Test**

1. **WebGoat**: `https://github.com/WebGoat/WebGoat`
   - OWASP's deliberately vulnerable Java application
   - Contains SQL injection, XSS, authentication flaws

2. **NodeGoat**: `https://github.com/OWASP/NodeGoat`
   - Vulnerable Node.js application  
   - NoSQL injection, session management issues

3. **Juice Shop**: `https://github.com/juice-shop/juice-shop`
   - Modern vulnerable web application
   - 100+ security challenges

4. **DVWA**: `https://github.com/digininja/DVWA`
   - Damn Vulnerable Web Application
   - Classic web vulnerabilities

## 📊 **Understanding Vulnerability Severities**

### 🔴 **CRITICAL**
- **Immediate action required**
- Remote code execution possible
- Data breach potential
- Examples: SQL injection, exposed AWS keys

### 🟠 **HIGH** 
- **Fix within days**
- Significant security impact
- Privilege escalation possible
- Examples: XSS, hardcoded passwords

### 🟡 **MEDIUM**
- **Fix within weeks**
- Moderate security risk
- Limited impact
- Examples: weak encryption, outdated packages

### 🟢 **LOW**
- **Fix when convenient**
- Minor security concern
- Minimal impact
- Examples: information disclosure

## 🚀 **Advanced Usage**

### **Filtering Results**
```bash
# Only critical vulnerabilities
curl "http://localhost:5000/api/vulnerabilities?severity=CRITICAL"

# Specific scanner results
curl "http://localhost:5000/api/vulnerabilities?scanner=bandit"

# Combined filters
curl "http://localhost:5000/api/vulnerabilities?severity=HIGH&scanner=semgrep"
```

### **Monitoring Scans**
```bash
# List all scans
curl http://localhost:5000/api/scans

# Get specific scan details
curl http://localhost:5000/api/scans/{scan_id}

# Dashboard overview
curl http://localhost:5000/api/overview
```

### **Bulk Operations**
```python
import requests

# Scan multiple repositories
repos = [
    "https://github.com/WebGoat/WebGoat",
    "https://github.com/OWASP/NodeGoat", 
    "https://github.com/juice-shop/juice-shop"
]

for repo in repos:
    response = requests.post('http://localhost:5000/api/scans', 
        json={'repo_url': repo, 'scan_types': ['SAST', 'SECRET', 'DEPENDENCY']}
    )
    print(f"Scanning {repo}: {response.status_code}")
```

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **API Not Responding**
   ```bash
   # Check if services are running
   curl http://localhost:5000/api/overview
   
   # Restart API server
   cd backend/VulnAlert
   python src/simple_server.py
   ```

2. **Frontend Not Loading**
   ```bash
   # Check frontend service
   curl http://localhost:8081
   
   # Restart frontend
   cd frontend/vulnwatch-dash
   npm run dev
   ```

3. **Scanner Issues**
   ```bash
   # Check scanner dependencies
   pip install bandit safety requests
   
   # Test manual scan
   python demo_scanner.py
   ```

## 📈 **Next Steps**

1. **Integrate with CI/CD**: Add webhook endpoints for automated scanning
2. **Set up Alerts**: Configure Slack/email notifications for critical findings
3. **Create Policies**: Define security policies and compliance rules
4. **Scale Up**: Deploy with Docker Compose for production use
5. **Custom Scanners**: Add domain-specific security checks

## 🎓 **Learning Resources**

- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **CWE Database**: https://cwe.mitre.org/
- **CVE Details**: https://cvedetails.com/
- **Security Testing Guide**: https://owasp.org/www-project-web-security-testing-guide/

---

🛡️ **DefenSys is now ready to help secure your applications!**

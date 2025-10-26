# Demo Vulnerable Website for DefenSys Testing

⚠️ **WARNING: This application contains intentional security vulnerabilities for testing purposes only. DO NOT deploy to production or expose to the internet!**

## Overview

This is a deliberately vulnerable web application designed to test DefenSys security scanning capabilities. It includes multiple common web vulnerabilities that can be detected by various security scanners.

## Vulnerabilities Included

### 1. **SQL Injection** (`/login`)
- **Description**: Login form vulnerable to SQL injection
- **Test**: Use `' OR '1'='1' --` as username
- **Impact**: Bypass authentication, access any user account

### 2. **Cross-Site Scripting (XSS)** (`/search`)
- **Description**: Search functionality doesn't sanitize output
- **Test**: Enter `<script>alert('XSS')</script>` in search
- **Impact**: Execute arbitrary JavaScript in victim's browser

### 3. **Insecure Direct Object Reference (IDOR)** (`/dashboard`)
- **Description**: No authorization check on user_id parameter
- **Test**: Change `?user_id=1` to `?user_id=2` in URL
- **Impact**: Access other users' private data

### 4. **Arbitrary File Upload** (`/upload`)
- **Description**: No file type validation or restrictions
- **Test**: Upload any file type including executables
- **Impact**: Upload malicious files, potential RCE

### 5. **Broken Access Control** (`/admin`)
- **Description**: Admin panel accessible without authentication
- **Test**: Navigate directly to `/admin`
- **Impact**: Unauthorized access to administrative functions

### 6. **Command Injection** (`/ping`)
- **Description**: Executes system commands without sanitization
- **Test**: Enter `127.0.0.1 && dir` (Windows) or `127.0.0.1; ls` (Linux)
- **Impact**: Remote code execution

### 7. **No Rate Limiting** (`/api/products`)
- **Description**: API endpoints have no rate limiting
- **Test**: Send rapid requests to API
- **Impact**: API abuse, DDoS vulnerability

### 8. **Information Disclosure** (`/config`, `/api/products`)
- **Description**: Exposes sensitive configuration data
- **Test**: Visit `/config` endpoint
- **Impact**: Leaks secrets, database paths, API keys

### 9. **Insecure Deserialization** (`/deserialize`)
- **Description**: Uses unsafe pickle deserialization
- **Test**: Send malicious serialized object
- **Impact**: Remote code execution

### 10. **Hardcoded Secrets**
- **Description**: Secret keys hardcoded in source code
- **Location**: Line 12 - `app.secret_key = 'hardcoded-secret-key-12345'`
- **Impact**: Secrets exposed in version control

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the application:**
```bash
python app.py
```

3. **Access the application:**
- Open browser to `http://localhost:5000`
- The database will be automatically created with sample data

## Testing with DefenSys

### Step 1: Start the Demo Website
```bash
cd demo-website
python app.py
```

### Step 2: Add Target in DefenSys
1. Go to DefenSys dashboard (`http://localhost:3000`)
2. Click "Targets" in navigation
3. Click "Add Target"
4. Enter:
   - **Name**: Demo Vulnerable Website
   - **URL**: `http://localhost:5000`
   - **Description**: Intentionally vulnerable test application

### Step 3: Run Scans
Choose from these scan types:

#### **Quick Port Scan**
- Detects open port 5000
- Identifies HTTP service

#### **Web Application Scan**
- Detects XSS vulnerabilities
- Finds SQL injection points
- Identifies broken access control
- Discovers sensitive endpoints

#### **Full Security Audit**
- Comprehensive scan using all tools
- Detects all vulnerabilities
- Provides detailed remediation guidance

### Step 4: Review Results
- Check the dashboard for vulnerability counts
- Click on individual scans to see detailed findings
- Review plain-language explanations of each issue

## Sample Test Cases

### SQL Injection Test
```bash
# Login form
Username: ' OR '1'='1' --
Password: anything

# Expected: Successful login bypass
```

### XSS Test
```bash
# Search form
Search: <script>alert('XSS')</script>

# Expected: JavaScript executes in browser
```

### IDOR Test
```bash
# URL manipulation
http://localhost:5000/dashboard?user_id=1  # Your account
http://localhost:5000/dashboard?user_id=2  # Other user's account

# Expected: Access other user's data without authorization
```

### Command Injection Test
```bash
# Ping form
Host: 127.0.0.1 && dir  (Windows)
Host: 127.0.0.1; ls     (Linux)

# Expected: Directory listing shown in output
```

## Expected DefenSys Findings

When you scan this application with DefenSys, you should see findings similar to:

### Critical Severity (3-5 findings)
- SQL Injection in login form
- Command Injection in ping utility
- Insecure deserialization endpoint
- Remote Code Execution via file upload

### High Severity (3-4 findings)
- Cross-Site Scripting in search
- Broken Access Control in admin panel
- Hardcoded secret keys
- Information disclosure endpoints

### Medium Severity (2-3 findings)
- Insecure Direct Object Reference
- Missing rate limiting
- Debug mode enabled in production

### Low Severity (1-2 findings)
- Missing security headers
- Verbose error messages

## Security Scanners That Will Detect Issues

- **Nmap**: Detects open port 5000, identifies HTTP service
- **Nuclei**: Finds XSS, SQL injection, exposed config files
- **Nikto**: Discovers admin panel, identifies web server info
- **OWASP ZAP**: Comprehensive web vulnerability scan
- **Bandit**: Detects hardcoded secrets, insecure functions
- **Semgrep**: Identifies code-level security issues
- **Trivy**: Checks for vulnerable dependencies

## Cleanup

To stop the application:
- Press `Ctrl+C` in the terminal running the Flask app

To remove database and uploads:
```bash
rm demo.db
rm -rf uploads/
```

## Educational Purpose

This application is designed for:
- ✅ Learning about web vulnerabilities
- ✅ Testing security scanning tools
- ✅ Understanding vulnerability remediation
- ✅ Training security professionals

**NOT for:**
- ❌ Production deployment
- ❌ Public internet exposure
- ❌ Storing real user data
- ❌ Any malicious purposes

## Vulnerability Remediation Examples

### Fix SQL Injection:
```python
# Bad (current code)
query = f"SELECT * FROM users WHERE username='{username}'"

# Good (use parameterized queries)
cursor.execute("SELECT * FROM users WHERE username=? AND password=?", 
               (username, password))
```

### Fix XSS:
```python
# Bad (current code)
return f"<h3>Results for: {query}</h3>"

# Good (escape output)
from markupsafe import escape
return f"<h3>Results for: {escape(query)}</h3>"
```

### Fix Command Injection:
```python
# Bad (current code)
subprocess.check_output(f'ping -n 1 {host}', shell=True)

# Good (use argument list)
subprocess.check_output(['ping', '-n', '1', host])
```

## Support

If you encounter issues:
1. Ensure Flask is installed: `pip install Flask`
2. Check port 5000 is not in use
3. Verify you're running from the demo-website directory
4. Check terminal for error messages

## License

This educational tool is provided as-is for security testing and training purposes only.

---

**Remember: Never deploy vulnerable applications to production environments!** 🔒

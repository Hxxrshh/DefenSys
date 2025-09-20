"""
DefenSys User Testing Guide
===========================

🎯 How Users Can Test for Security Problems Using DefenSys

Your DefenSys application provides multiple ways for users to test their code 
for security issues. Here's a comprehensive guide showing all available methods:

═══════════════════════════════════════════════════════════════════════════════

METHOD 1: 🌐 GIT REPOSITORY TESTING (PRIMARY METHOD)
═══════════════════════════════════════════════════════════════════════════════

Users can add Git repository links to scan for security problems:

📋 SUPPORTED REPOSITORY FORMATS:
• GitHub: https://github.com/username/repository-name
• GitLab: https://gitlab.com/username/repository-name  
• Bitbucket: https://bitbucket.org/username/repository-name
• Any Git URL: https://your-git-server.com/repo.git

🔧 HOW TO USE:

1️⃣ Via Web Interface (User-Friendly):
   • Open: http://localhost:8002/user_friendly_scanner.html
   • Enter repository URL in the "Repository URL" field
   • Choose scan type from dropdown (e.g., "Code Security Check")
   • Click "Start Security Scan"
   • Wait for results to appear

2️⃣ Via API Call:
   POST http://localhost:8002/api/scan/simple
   {
     "repository_url": "https://github.com/username/repo",
     "scan_category": "code_security",
     "project_name": "My Project"
   }

3️⃣ Via Advanced API:
   POST http://localhost:8002/api/scan
   {
     "repository_url": "https://github.com/username/repo",
     "scan_types": ["secrets", "sast", "dependencies"]
   }

🎨 AVAILABLE SCAN CATEGORIES:
• code_security - Find vulnerabilities in source code
• secrets_check - Detect API keys, passwords, tokens
• dependency_audit - Check for vulnerable dependencies  
• container_security - Scan Docker/container configurations
• infrastructure_check - Analyze infrastructure as code
• compliance_check - Verify security compliance standards
• quick_overview - Fast general security overview
• comprehensive_audit - Deep security analysis

═══════════════════════════════════════════════════════════════════════════════

METHOD 2: 📁 LOCAL FILE/FOLDER TESTING  
═══════════════════════════════════════════════════════════════════════════════

Users can test local files and folders:

🔧 HOW TO USE:

1️⃣ Direct Path Scanning:
   POST http://localhost:8002/api/scan/recommendations
   {
     "path": "/path/to/local/project"
   }

2️⃣ File Upload (Future Enhancement):
   • Drag & drop files/folders
   • Zip file upload
   • Direct folder selection

📋 SUPPORTED LOCAL FORMATS:
• Individual files (.py, .js, .java, .php, etc.)
• Project folders (with multiple files)
• Configuration files (Dockerfile, docker-compose.yml)
• Infrastructure files (.tf, .yml, .json)

═══════════════════════════════════════════════════════════════════════════════

METHOD 3: 🔌 API INTEGRATION TESTING
═══════════════════════════════════════════════════════════════════════════════

Developers can integrate DefenSys into their workflows:

🔧 PROGRAMMATIC ACCESS:

1️⃣ Get Scan Options:
   GET http://localhost:8002/api/scan/options
   Response: Available scan categories and descriptions

2️⃣ Get Project Recommendations:
   POST http://localhost:8002/api/scan/recommendations
   {
     "repository_url": "https://github.com/user/repo"
   }
   Response: Personalized scan recommendations

3️⃣ Check Scanner Status:
   GET http://localhost:8002/api/scanners
   Response: Available scanners and their status

4️⃣ View Scan Results:
   GET http://localhost:8002/api/scans/
   Response: List of all scans and their results

═══════════════════════════════════════════════════════════════════════════════

METHOD 4: 🚀 CI/CD PIPELINE INTEGRATION
═══════════════════════════════════════════════════════════════════════════════

Users can integrate DefenSys into their development workflows:

🔧 GITHUB ACTIONS EXAMPLE:
```yaml
name: Security Scan
on: [push, pull_request]
jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: DefenSys Security Scan
        run: |
          curl -X POST "http://defensys-server:8002/api/scan/simple" \
               -H "Content-Type: application/json" \
               -d '{
                 "repository_url": "${{ github.server_url }}/${{ github.repository }}",
                 "scan_category": "comprehensive_audit"
               }'
```

🔧 JENKINS PIPELINE:
```groovy
pipeline {
    agent any
    stages {
        stage('Security Scan') {
            steps {
                script {
                    def response = sh(
                        script: """
                            curl -X POST "http://defensys:8002/api/scan/simple" \
                                 -H "Content-Type: application/json" \
                                 -d '{"repository_url": "${env.GIT_URL}", "scan_category": "code_security"}'
                        """,
                        returnStdout: true
                    )
                    echo "Scan initiated: ${response}"
                }
            }
        }
    }
}
```

═══════════════════════════════════════════════════════════════════════════════

METHOD 5: 🎯 SPECIFIC TESTING SCENARIOS
═══════════════════════════════════════════════════════════════════════════════

Examples of what users can test:

🔒 SECURITY VULNERABILITIES:
• SQL Injection vulnerabilities
• Cross-Site Scripting (XSS)
• Command Injection
• Path Traversal
• Authentication bypasses

🔑 SECRETS & CREDENTIALS:
• Hardcoded API keys
• Database passwords
• AWS/Cloud credentials
• SSL certificates and keys
• JWT tokens

📦 DEPENDENCY ISSUES:
• Outdated packages with known CVEs
• Vulnerable third-party libraries
• License compliance issues
• Dependency confusion attacks

🐳 CONTAINER SECURITY:
• Dockerfile misconfigurations
• Insecure base images
• Exposed ports and services
• Privilege escalation risks

🏗️ INFRASTRUCTURE PROBLEMS:
• Terraform misconfigurations
• Kubernetes security issues
• Cloud resource exposures
• Network security gaps

═══════════════════════════════════════════════════════════════════════════════

PRACTICAL TESTING EXAMPLES:
═══════════════════════════════════════════════════════════════════════════════

🧪 Example 1: Test a Python Web App
Repository: https://github.com/user/flask-app
Scan Type: "Code Security Check"
Expected Findings: SQL injection, XSS, insecure configs

🧪 Example 2: Test a React Frontend  
Repository: https://github.com/user/react-dashboard
Scan Type: "Secrets Check"
Expected Findings: API keys, hardcoded tokens

🧪 Example 3: Test Infrastructure Code
Repository: https://github.com/user/terraform-aws
Scan Type: "Infrastructure Check"  
Expected Findings: Open security groups, unencrypted storage

🧪 Example 4: Test Docker Application
Repository: https://github.com/user/docker-app
Scan Type: "Container Security"
Expected Findings: Vulnerable base images, exposed ports

═══════════════════════════════════════════════════════════════════════════════

TESTING WORKFLOW RECOMMENDATIONS:
═══════════════════════════════════════════════════════════════════════════════

🎯 FOR DEVELOPERS:
1. Start with "Quick Overview" for new projects
2. Use "Code Security Check" during development
3. Run "Comprehensive Audit" before releases
4. Integrate into CI/CD for continuous monitoring

🎯 FOR SECURITY TEAMS:
1. Use "Comprehensive Audit" for thorough analysis
2. Focus on "Secrets Check" for credential hygiene
3. Regular "Dependency Audit" for supply chain security
4. "Compliance Check" for regulatory requirements

🎯 FOR DEVOPS TEAMS:
1. "Container Security" for containerized apps
2. "Infrastructure Check" for IaC deployments  
3. Automated scans in deployment pipelines
4. Regular monitoring of production codebases

═══════════════════════════════════════════════════════════════════════════════

SUMMARY: HOW USERS TEST WITH DEFENSYS
═══════════════════════════════════════════════════════════════════════════════

✅ Primary Method: Add Git repository URL for automated scanning
✅ Secondary: Upload local files/folders for analysis
✅ API Integration: Programmatic access for custom workflows
✅ CI/CD Integration: Automated security in development pipelines
✅ Web Interface: User-friendly scanning with dropdown selections
✅ Multiple Scan Types: From quick overviews to comprehensive audits
✅ Real-time Results: Progressive scanning with live updates
✅ Enterprise Ready: Handles large codebases efficiently

Your DefenSys platform provides comprehensive security testing capabilities
that scale from individual developers to enterprise development teams!
"""

print(__doc__)
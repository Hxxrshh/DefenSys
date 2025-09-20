"""
DefenSys Practical Demo Scenarios & Use Cases
==============================================

Real-world examples showing how different types of users can test
their code for security problems using DefenSys.
"""

# =============================================================================
# DEMO SCENARIO 1: WEB DEVELOPER - Testing a Flask Application
# =============================================================================

def demo_scenario_1_web_developer():
    """
    Scenario: Sarah is developing a Flask web application and wants to check
    for security vulnerabilities before deploying to production.
    """
    print("🎭 DEMO SCENARIO 1: Web Developer Testing Flask App")
    print("=" * 60)
    print("👩‍💻 User: Sarah (Full-stack Developer)")
    print("🎯 Goal: Security check before production deployment")
    print("📦 Project: Flask e-commerce application")
    print("")
    
    # Step-by-step testing approach
    steps = [
        {
            "step": "1️⃣ Quick Overview Scan",
            "method": "Git Repository",
            "url": "https://github.com/sarah/flask-ecommerce",
            "scan_type": "quick_overview",
            "reasoning": "Get a general sense of security posture",
            "expected_time": "2-3 minutes"
        },
        {
            "step": "2️⃣ Code Security Deep Dive",
            "method": "Same Repository",
            "url": "https://github.com/sarah/flask-ecommerce", 
            "scan_type": "code_security",
            "reasoning": "Find SQL injection, XSS, and other code vulnerabilities",
            "expected_time": "8-12 minutes"
        },
        {
            "step": "3️⃣ Secrets and Credentials Check",
            "method": "Same Repository",
            "url": "https://github.com/sarah/flask-ecommerce",
            "scan_type": "secrets_check", 
            "reasoning": "Ensure no API keys or passwords are hardcoded",
            "expected_time": "3-5 minutes"
        },
        {
            "step": "4️⃣ Dependency Audit",
            "method": "Same Repository",
            "url": "https://github.com/sarah/flask-ecommerce",
            "scan_type": "dependency_audit",
            "reasoning": "Check for vulnerable Flask/Python packages",
            "expected_time": "5-7 minutes"
        }
    ]
    
    for step_info in steps:
        print(f"{step_info['step']} {step_info['scan_type'].replace('_', ' ').title()}")
        print(f"   🔗 Method: {step_info['method']}")
        print(f"   🎯 Purpose: {step_info['reasoning']}")
        print(f"   ⏱️ Time: {step_info['expected_time']}")
        print(f"   📋 API Call:")
        print(f"      POST /api/scan/simple")
        print(f"      {{")
        print(f"        \"repository_url\": \"{step_info['url']}\",")
        print(f"        \"scan_category\": \"{step_info['scan_type']}\",")
        print(f"        \"project_name\": \"Flask E-commerce\"")
        print(f"      }}")
        print("")
    
    print("📊 Expected Results for Flask App:")
    print("   🔍 Code Security: SQL injection in login.py, XSS in search.py")
    print("   🔑 Secrets: Database password in config.py")
    print("   📦 Dependencies: Outdated Flask version with known CVE")
    print("   🎯 Total Issues: 15-25 security findings")
    print("")

# =============================================================================
# DEMO SCENARIO 2: DEVOPS ENGINEER - Container Security Testing
# =============================================================================

def demo_scenario_2_devops_engineer():
    """
    Scenario: Mike is a DevOps engineer preparing a containerized microservices
    application for Kubernetes deployment.
    """
    print("🎭 DEMO SCENARIO 2: DevOps Engineer Testing Containers")
    print("=" * 60)
    print("👨‍💻 User: Mike (DevOps Engineer)")
    print("🎯 Goal: Secure container deployment to Kubernetes")
    print("📦 Project: Microservices with Docker containers")
    print("")
    
    # Multiple repositories/components to test
    components = [
        {
            "name": "Frontend Service",
            "repo": "https://github.com/company/frontend-service",
            "scan_type": "container_security",
            "focus": "Dockerfile security, exposed ports"
        },
        {
            "name": "API Gateway", 
            "repo": "https://github.com/company/api-gateway",
            "scan_type": "comprehensive_audit",
            "focus": "Full security audit including code and containers"
        },
        {
            "name": "Database Service",
            "repo": "https://github.com/company/db-service", 
            "scan_type": "secrets_check",
            "focus": "Database credentials and connection strings"
        },
        {
            "name": "Infrastructure Code",
            "repo": "https://github.com/company/k8s-manifests",
            "scan_type": "infrastructure_check", 
            "focus": "Kubernetes YAML security configurations"
        }
    ]
    
    print("🏗️ Multi-Component Security Testing:")
    for i, component in enumerate(components, 1):
        print(f"{i}️⃣ {component['name']}")
        print(f"   📁 Repository: {component['repo']}")
        print(f"   🔍 Scan Type: {component['scan_type']}")
        print(f"   🎯 Focus: {component['focus']}")
        print("")
    
    print("🚀 Batch Testing Script:")
    print("```python")
    print("client = DefenSysAPIClient()")
    print("scan_ids = []")
    print("")
    for component in components:
        print(f"# {component['name']}")
        print(f"result = client.scan_repository(")
        print(f"    '{component['repo']}',") 
        print(f"    '{component['scan_type']}'")
        print(f")")
        print(f"scan_ids.append(result['scan_id'])")
        print("")
    print("# Monitor all scans")
    print("for scan_id in scan_ids:")
    print("    results = client.get_scan_results(scan_id)")
    print("    print(f'Scan {scan_id}: {results}')")
    print("```")
    print("")

# =============================================================================
# DEMO SCENARIO 3: SECURITY TEAM - Compliance Audit
# =============================================================================

def demo_scenario_3_security_team():
    """
    Scenario: Jessica is a security analyst conducting a quarterly compliance
    audit of all company applications.
    """
    print("🎭 DEMO SCENARIO 3: Security Team Compliance Audit")
    print("=" * 60)
    print("👩‍🔒 User: Jessica (Security Analyst)")
    print("🎯 Goal: Quarterly compliance audit for SOC2/ISO27001")
    print("📦 Scope: All company applications and infrastructure")
    print("")
    
    # Comprehensive audit approach
    audit_phases = [
        {
            "phase": "Phase 1: Discovery",
            "description": "Identify all repositories and applications",
            "method": "Bulk repository scanning",
            "scan_type": "quick_overview",
            "timeline": "Week 1"
        },
        {
            "phase": "Phase 2: Deep Analysis", 
            "description": "Comprehensive security analysis",
            "method": "Comprehensive audit scans",
            "scan_type": "comprehensive_audit",
            "timeline": "Week 2-3"
        },
        {
            "phase": "Phase 3: Compliance Check",
            "description": "Verify compliance requirements",
            "method": "Compliance-focused scanning", 
            "scan_type": "compliance_check",
            "timeline": "Week 4"
        },
        {
            "phase": "Phase 4: Reporting",
            "description": "Generate compliance reports",
            "method": "Results aggregation and reporting",
            "scan_type": "N/A",
            "timeline": "Week 5"
        }
    ]
    
    for phase in audit_phases:
        print(f"📋 {phase['phase']}")
        print(f"   📝 Description: {phase['description']}")
        print(f"   🔧 Method: {phase['method']}")
        if phase['scan_type'] != 'N/A':
            print(f"   🔍 Scan Type: {phase['scan_type']}")
        print(f"   📅 Timeline: {phase['timeline']}")
        print("")
    
    print("📊 Compliance Metrics Tracked:")
    print("   • Code vulnerabilities per application")
    print("   • Hardcoded secrets and credentials") 
    print("   • Dependency security posture")
    print("   • Container/infrastructure security")
    print("   • Security policy compliance")
    print("   • Remediation timeline tracking")
    print("")

# =============================================================================
# DEMO SCENARIO 4: STARTUP TEAM - Pre-Investment Security Check
# =============================================================================

def demo_scenario_4_startup_team():
    """
    Scenario: Alex's startup is preparing for Series A funding and investors
    want to see their security posture and code quality.
    """
    print("🎭 DEMO SCENARIO 4: Startup Pre-Investment Security")
    print("=" * 60)
    print("👨‍💼 User: Alex (Startup CTO)")
    print("🎯 Goal: Demonstrate security readiness for investors")
    print("📦 Project: SaaS platform with mobile app")
    print("")
    
    # Investment-focused security demonstration
    security_checklist = [
        {
            "area": "Application Security",
            "repositories": [
                "https://github.com/startup/web-app",
                "https://github.com/startup/mobile-backend",
                "https://github.com/startup/admin-dashboard"
            ],
            "scan_type": "comprehensive_audit",
            "investor_concern": "Code vulnerabilities that could lead to data breaches"
        },
        {
            "area": "Data Protection",
            "repositories": [
                "https://github.com/startup/web-app",
                "https://github.com/startup/mobile-backend"
            ],
            "scan_type": "secrets_check", 
            "investor_concern": "Hardcoded credentials and API keys"
        },
        {
            "area": "Supply Chain Security",
            "repositories": [
                "https://github.com/startup/web-app",
                "https://github.com/startup/mobile-backend"
            ],
            "scan_type": "dependency_audit",
            "investor_concern": "Vulnerable third-party dependencies"
        },
        {
            "area": "Infrastructure Security",
            "repositories": [
                "https://github.com/startup/infrastructure",
                "https://github.com/startup/docker-configs"
            ],
            "scan_type": "infrastructure_check",
            "investor_concern": "Cloud security and deployment practices"
        }
    ]
    
    print("💼 Investor Security Checklist:")
    for i, item in enumerate(security_checklist, 1):
        print(f"{i}️⃣ {item['area']}")
        print(f"   🎯 Investor Concern: {item['investor_concern']}")
        print(f"   📁 Repositories to scan: {len(item['repositories'])}")
        print(f"   🔍 Scan Type: {item['scan_type']}")
        print(f"   📋 Repositories:")
        for repo in item['repositories']:
            print(f"      • {repo}")
        print("")
    
    print("📈 Security Scorecard for Investors:")
    print("   🛡️ Security Score: 85/100 (Good)")
    print("   🔍 Critical Issues: 2 (Fixed within 48h)")
    print("   ⚠️ Medium Issues: 8 (Remediation plan provided)")
    print("   ℹ️ Low Issues: 15 (Non-blocking for funding)")
    print("   📊 Security Trend: Improving (monthly scans)")
    print("")

# =============================================================================
# DEMO SCENARIO 5: OPEN SOURCE MAINTAINER - Community Project Security
# =============================================================================

def demo_scenario_5_open_source_maintainer():
    """
    Scenario: Emma maintains a popular open source library and wants to ensure
    it's secure for the thousands of developers who depend on it.
    """
    print("🎭 DEMO SCENARIO 5: Open Source Project Security")
    print("=" * 60)
    print("👩‍💻 User: Emma (Open Source Maintainer)")
    print("🎯 Goal: Secure popular library used by thousands")
    print("📦 Project: JavaScript utility library with 50K+ downloads")
    print("")
    
    # Open source security workflow
    workflow_steps = [
        {
            "trigger": "Pull Request",
            "action": "Automated security scan on PR",
            "scan_type": "code_security",
            "description": "Scan new code before merging"
        },
        {
            "trigger": "Weekly Schedule",
            "action": "Dependency audit",
            "scan_type": "dependency_audit", 
            "description": "Check for new CVEs in dependencies"
        },
        {
            "trigger": "Release Preparation",
            "action": "Comprehensive security audit",
            "scan_type": "comprehensive_audit",
            "description": "Full security check before release"
        },
        {
            "trigger": "Security Report",
            "action": "Targeted vulnerability scan",
            "scan_type": "code_security",
            "description": "Investigate reported security issues"
        }
    ]
    
    print("🔄 Automated Security Workflow:")
    for step in workflow_steps:
        print(f"🔔 Trigger: {step['trigger']}")
        print(f"   ⚡ Action: {step['action']}")
        print(f"   🔍 Scan: {step['scan_type']}")
        print(f"   📝 Description: {step['description']}")
        print("")
    
    print("🤖 GitHub Actions Integration:")
    print("```yaml")
    print("name: Security Scan")
    print("on:")
    print("  pull_request:")
    print("  schedule:")
    print("    - cron: '0 2 * * 1'  # Weekly Monday 2 AM")
    print("")
    print("jobs:")
    print("  security-scan:")
    print("    runs-on: ubuntu-latest")
    print("    steps:")
    print("      - uses: actions/checkout@v2")
    print("      - name: DefenSys Security Scan")
    print("        run: |")
    print("          curl -X POST \"${{ secrets.DEFENSYS_URL }}/api/scan/simple\" \\")
    print("               -H \"Content-Type: application/json\" \\")
    print("               -d '{")
    print("                 \"repository_url\": \"${{ github.server_url }}/${{ github.repository }}\",")
    print("                 \"scan_category\": \"comprehensive_audit\"")
    print("               }'")
    print("```")
    print("")

# =============================================================================
# CI/CD INTEGRATION EXAMPLES
# =============================================================================

def cicd_integration_examples():
    """
    Comprehensive CI/CD integration examples for different platforms
    """
    print("🚀 CI/CD INTEGRATION EXAMPLES")
    print("=" * 60)
    print("How to integrate DefenSys into various CI/CD platforms")
    print("")
    
    # GitHub Actions
    print("🐙 GITHUB ACTIONS")
    print("File: .github/workflows/security.yml")
    print("```yaml")
    github_actions = """
name: DefenSys Security Scan
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        
      - name: DefenSys Quick Scan
        if: github.event_name == 'pull_request'
        run: |
          response=$(curl -s -X POST "${{ secrets.DEFENSYS_URL }}/api/scan/simple" \\
                          -H "Content-Type: application/json" \\
                          -d '{
                            "repository_url": "${{ github.server_url }}/${{ github.repository }}",
                            "scan_category": "quick_overview",
                            "project_name": "${{ github.repository }}"
                          }')
          echo "Scan result: $response"
          
      - name: DefenSys Comprehensive Scan
        if: github.ref == 'refs/heads/main'
        run: |
          curl -X POST "${{ secrets.DEFENSYS_URL }}/api/scan/simple" \\
               -H "Content-Type: application/json" \\
               -d '{
                 "repository_url": "${{ github.server_url }}/${{ github.repository }}",
                 "scan_category": "comprehensive_audit"
               }'
"""
    print(github_actions)
    print("```")
    print("")
    
    # Jenkins Pipeline
    print("🏗️ JENKINS PIPELINE")
    print("File: Jenkinsfile")
    print("```groovy")
    jenkins_pipeline = """
pipeline {
    agent any
    
    environment {
        DEFENSYS_URL = credentials('defensys-url')
        REPO_URL = "${env.GIT_URL}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Security Scan') {
            parallel {
                stage('Code Security') {
                    steps {
                        script {
                            def response = sh(
                                script: '''
                                    curl -X POST "${DEFENSYS_URL}/api/scan/simple" \\
                                         -H "Content-Type: application/json" \\
                                         -d "{
                                           \\"repository_url\\": \\"${REPO_URL}\\",
                                           \\"scan_category\\": \\"code_security\\",
                                           \\"project_name\\": \\"${JOB_NAME}\\"
                                         }"
                                ''',
                                returnStdout: true
                            )
                            echo "Code security scan: ${response}"
                        }
                    }
                }
                
                stage('Dependency Audit') {
                    steps {
                        script {
                            sh '''
                                curl -X POST "${DEFENSYS_URL}/api/scan/simple" \\
                                     -H "Content-Type: application/json" \\
                                     -d "{
                                       \\"repository_url\\": \\"${REPO_URL}\\",
                                       \\"scan_category\\": \\"dependency_audit\\"
                                     }"
                            '''
                        }
                    }
                }
            }
        }
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                echo 'Deploying after security checks passed...'
            }
        }
    }
    
    post {
        always {
            echo 'Security scanning completed'
        }
        failure {
            echo 'Security scan failed - blocking deployment'
        }
    }
}
"""
    print(jenkins_pipeline)
    print("```")
    print("")
    
    # GitLab CI
    print("🦊 GITLAB CI")
    print("File: .gitlab-ci.yml")
    print("```yaml")
    gitlab_ci = """
stages:
  - security
  - deploy

variables:
  DEFENSYS_URL: $DEFENSYS_URL

security-scan:
  stage: security
  image: curlimages/curl:latest
  script:
    - |
      echo "Starting DefenSys security scan..."
      
      # Quick scan for merge requests
      if [ "$CI_PIPELINE_SOURCE" = "merge_request_event" ]; then
        SCAN_TYPE="quick_overview"
      else
        SCAN_TYPE="comprehensive_audit"
      fi
      
      response=$(curl -s -X POST "$DEFENSYS_URL/api/scan/simple" \\
                      -H "Content-Type: application/json" \\
                      -d "{
                        \\"repository_url\\": \\"$CI_REPOSITORY_URL\\",
                        \\"scan_category\\": \\"$SCAN_TYPE\\",
                        \\"project_name\\": \\"$CI_PROJECT_NAME\\"
                      }")
      
      echo "Scan response: $response"
      
      # Extract scan ID for monitoring
      scan_id=$(echo $response | grep -o '"scan_id":[0-9]*' | cut -d':' -f2)
      echo "Scan ID: $scan_id"
  
  artifacts:
    reports:
      junit: security-report.xml
  
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

deploy:
  stage: deploy
  script:
    - echo "Deploying application..."
  dependencies:
    - security-scan
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
"""
    print(gitlab_ci)
    print("```")
    print("")
    
    # Azure DevOps
    print("🔷 AZURE DEVOPS")
    print("File: azure-pipelines.yml")
    print("```yaml")
    azure_pipeline = """
trigger:
  branches:
    include:
      - main
      - develop

pool:
  vmImage: 'ubuntu-latest'

variables:
  defensysUrl: $(DEFENSYS_URL)

stages:
- stage: SecurityScan
  displayName: 'Security Scanning'
  jobs:
  - job: DefenSysScan
    displayName: 'DefenSys Security Scan'
    steps:
    - checkout: self
    
    - task: Bash@3
      displayName: 'Run DefenSys Scan'
      inputs:
        targetType: 'inline'
        script: |
          echo "Starting DefenSys security scan..."
          
          # Determine scan type based on branch
          if [ "$(Build.SourceBranch)" = "refs/heads/main" ]; then
            SCAN_TYPE="comprehensive_audit"
          else
            SCAN_TYPE="code_security"
          fi
          
          # Run security scan
          response=$(curl -s -X POST "$(defensysUrl)/api/scan/simple" \\
                          -H "Content-Type: application/json" \\
                          -d "{
                            \\"repository_url\\": \\"$(Build.Repository.Uri)\\",
                            \\"scan_category\\": \\"$SCAN_TYPE\\",
                            \\"project_name\\": \\"$(Build.Repository.Name)\\"
                          }")
          
          echo "Response: $response"
          
          # Check for errors
          if echo "$response" | grep -q "error"; then
            echo "##vso[task.logissue type=error]Security scan failed"
            exit 1
          fi

- stage: Deploy
  displayName: 'Deploy Application'
  dependsOn: SecurityScan
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  jobs:
  - deployment: DeployToProduction
    displayName: 'Deploy to Production'
    environment: 'production'
    strategy:
      runOnce:
        deploy:
          steps:
          - script: echo "Deploying after security validation..."
"""
    print(azure_pipeline)
    print("```")
    print("")

# =============================================================================
# MAIN DEMO RUNNER
# =============================================================================

def run_all_demo_scenarios():
    """Run all demo scenarios and examples"""
    print("🎬 DEFENSYS PRACTICAL DEMO SCENARIOS")
    print("=" * 80)
    print("Real-world examples of how users test for security problems")
    print("")
    
    scenarios = [
        demo_scenario_1_web_developer,
        demo_scenario_2_devops_engineer, 
        demo_scenario_3_security_team,
        demo_scenario_4_startup_team,
        demo_scenario_5_open_source_maintainer,
        cicd_integration_examples
    ]
    
    for scenario in scenarios:
        scenario()
        print("─" * 80)
        print("")
    
    print("🎯 SUMMARY: USER TESTING SCENARIOS")
    print("=" * 80)
    print("✅ Web Developers: Code security before deployment")
    print("✅ DevOps Engineers: Container and infrastructure security")
    print("✅ Security Teams: Compliance auditing and reporting")
    print("✅ Startup Teams: Investment-ready security posture") 
    print("✅ Open Source Maintainers: Community project security")
    print("✅ CI/CD Integration: Automated security in pipelines")
    print("")
    print("🔧 Integration Options:")
    print("✅ GitHub Actions")
    print("✅ Jenkins Pipeline")
    print("✅ GitLab CI/CD")
    print("✅ Azure DevOps")
    print("✅ Custom REST API integration")

if __name__ == "__main__":
    run_all_demo_scenarios()
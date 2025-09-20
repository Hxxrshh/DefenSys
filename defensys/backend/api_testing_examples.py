"""
DefenSys API Testing Examples
=============================

Complete collection of API calls and examples showing how users can
programmatically test their code for security problems using DefenSys.
"""

import requests
import json
import time
from pathlib import Path

class DefenSysAPIClient:
    """
    Python client for DefenSys API - makes testing easy for developers
    """
    
    def __init__(self, base_url="http://localhost:8002"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_scan_options(self):
        """Get available scan categories and options"""
        response = self.session.get(f"{self.base_url}/api/scan/options")
        return response.json()
    
    def scan_repository(self, repository_url, scan_category="code_security", project_name=None):
        """
        Scan a Git repository for security issues
        
        Args:
            repository_url: Git repository URL
            scan_category: Type of scan to perform
            project_name: Optional project name
        """
        payload = {
            "repository_url": repository_url,
            "scan_category": scan_category
        }
        if project_name:
            payload["project_name"] = project_name
            
        response = self.session.post(f"{self.base_url}/api/scan/simple", json=payload)
        return response.json()
    
    def upload_file_scan(self, file_path, scan_category="code_security", project_name=None):
        """Upload and scan a single file"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'scan_category': scan_category}
            if project_name:
                data['project_name'] = project_name
                
            response = self.session.post(f"{self.base_url}/api/upload/file", files=files, data=data)
            return response.json()
    
    def upload_folder_scan(self, zip_path, scan_category="comprehensive_audit", project_name=None):
        """Upload and scan a ZIP folder"""
        with open(zip_path, 'rb') as f:
            files = {'zip_file': f}
            data = {'scan_category': scan_category}
            if project_name:
                data['project_name'] = project_name
                
            response = self.session.post(f"{self.base_url}/api/upload/folder", files=files, data=data)
            return response.json()
    
    def scan_local_path(self, local_path, scan_category="code_security", project_name=None):
        """Scan a local file system path"""
        payload = {
            "path": local_path,
            "scan_category": scan_category
        }
        if project_name:
            payload["project_name"] = project_name
            
        response = self.session.post(f"{self.base_url}/api/scan/local-path", json=payload)
        return response.json()
    
    def get_scan_results(self, scan_id):
        """Get results of a specific scan"""
        response = self.session.get(f"{self.base_url}/api/scans/{scan_id}")
        return response.json()
    
    def get_all_scans(self):
        """Get list of all scans"""
        response = self.session.get(f"{self.base_url}/api/scans/")
        return response.json()
    
    def get_project_recommendations(self, repository_url=None, local_path=None):
        """Get scan recommendations for a project"""
        payload = {}
        if repository_url:
            payload["repository_url"] = repository_url
        if local_path:
            payload["path"] = local_path
            
        response = self.session.post(f"{self.base_url}/api/scan/recommendations", json=payload)
        return response.json()

# =============================================================================
# EXAMPLE 1: Basic Repository Scanning
# =============================================================================

def example_1_basic_repo_scan():
    """Example: Scan a GitHub repository for code security issues"""
    print("🧪 Example 1: Basic Repository Scanning")
    print("=" * 50)
    
    client = DefenSysAPIClient()
    
    # Scan a popular vulnerable app for demonstration
    result = client.scan_repository(
        repository_url="https://github.com/OWASP/WebGoat",
        scan_category="code_security",
        project_name="WebGoat Security Test"
    )
    
    print(f"✅ Scan initiated: {result['message']}")
    print(f"📊 Scan ID: {result['scan_id']}")
    print(f"🔍 Scan Type: {result['scan_details']['chosen_scan']}")
    print(f"⏱️ Estimated Time: {result['scan_details']['estimated_time']}")
    print("")

# =============================================================================
# EXAMPLE 2: Multiple Scan Types
# =============================================================================

def example_2_multiple_scan_types():
    """Example: Run different types of scans on the same repository"""
    print("🧪 Example 2: Multiple Scan Types")
    print("=" * 50)
    
    client = DefenSysAPIClient()
    repo_url = "https://github.com/username/my-app"
    
    scan_types = [
        ("secrets_check", "Look for API keys and passwords"),
        ("dependency_audit", "Check for vulnerable dependencies"),
        ("code_security", "Find code vulnerabilities"),
        ("container_security", "Scan Docker configurations")
    ]
    
    for scan_type, description in scan_types:
        print(f"🔍 Running {scan_type}: {description}")
        result = client.scan_repository(repo_url, scan_type)
        print(f"   ✅ Scan ID: {result['scan_id']}")
    print("")

# =============================================================================
# EXAMPLE 3: File Upload Testing
# =============================================================================

def example_3_file_upload_testing():
    """Example: Upload and scan individual files"""
    print("🧪 Example 3: File Upload Testing")
    print("=" * 50)
    
    client = DefenSysAPIClient()
    
    # Example files to test (create these for testing)
    test_files = [
        ("vulnerable_app.py", "secrets_check"),
        ("config.js", "code_security"),
        ("Dockerfile", "container_security")
    ]
    
    for filename, scan_type in test_files:
        if Path(filename).exists():
            print(f"📁 Uploading {filename} for {scan_type} scan")
            result = client.upload_file_scan(filename, scan_type)
            print(f"   ✅ Found {result['vulnerabilities_found']} issues")
        else:
            print(f"   ⚠️ File {filename} not found, skipping")
    print("")

# =============================================================================
# EXAMPLE 4: Local Path Scanning
# =============================================================================

def example_4_local_path_scanning():
    """Example: Scan local directories and files"""
    print("🧪 Example 4: Local Path Scanning")
    print("=" * 50)
    
    client = DefenSysAPIClient()
    
    # Scan current directory
    current_dir = str(Path.cwd())
    print(f"📁 Scanning current directory: {current_dir}")
    
    result = client.scan_local_path(
        local_path=current_dir,
        scan_category="quick_overview",
        project_name="Current Directory Scan"
    )
    
    print(f"✅ {result['message']}")
    print(f"🐛 Vulnerabilities found: {result['vulnerabilities_found']}")
    print("")

# =============================================================================
# EXAMPLE 5: CI/CD Integration Pattern
# =============================================================================

def example_5_cicd_integration():
    """Example: How to integrate DefenSys into CI/CD pipelines"""
    print("🧪 Example 5: CI/CD Integration Pattern")
    print("=" * 50)
    
    client = DefenSysAPIClient()
    
    # Simulate CI/CD workflow
    repository_url = "https://github.com/username/production-app"
    
    # Step 1: Get recommendations
    print("1️⃣ Getting scan recommendations...")
    recommendations = client.get_project_recommendations(repository_url)
    print(f"   📊 Detected project type: {recommendations['detected_project_type']}")
    
    # Step 2: Run comprehensive scan
    print("2️⃣ Running comprehensive security audit...")
    scan_result = client.scan_repository(repository_url, "comprehensive_audit")
    scan_id = scan_result['scan_id']
    print(f"   🔍 Scan ID: {scan_id}")
    
    # Step 3: Wait for completion (in real CI/CD, you'd poll or use webhooks)
    print("3️⃣ Waiting for scan completion...")
    time.sleep(2)  # Simulate wait
    
    # Step 4: Check results
    print("4️⃣ Checking scan results...")
    all_scans = client.get_all_scans()
    print(f"   📈 Total scans in system: {len(all_scans)}")
    print("")

# =============================================================================
# EXAMPLE 6: Batch Testing Multiple Repositories
# =============================================================================

def example_6_batch_testing():
    """Example: Scan multiple repositories in batch"""
    print("🧪 Example 6: Batch Testing Multiple Repositories")
    print("=" * 50)
    
    client = DefenSysAPIClient()
    
    # List of repositories to scan
    repositories = [
        ("https://github.com/org/frontend-app", "code_security"),
        ("https://github.com/org/backend-api", "comprehensive_audit"),
        ("https://github.com/org/infrastructure", "infrastructure_check"),
        ("https://github.com/org/mobile-app", "dependency_audit")
    ]
    
    scan_ids = []
    for repo_url, scan_type in repositories:
        print(f"🔍 Scanning {repo_url.split('/')[-1]} with {scan_type}")
        result = client.scan_repository(repo_url, scan_type)
        scan_ids.append(result['scan_id'])
        print(f"   ✅ Scan ID: {result['scan_id']}")
    
    print(f"📊 Initiated {len(scan_ids)} scans: {scan_ids}")
    print("")

# =============================================================================
# EXAMPLE 7: API Error Handling
# =============================================================================

def example_7_error_handling():
    """Example: Proper error handling when using the API"""
    print("🧪 Example 7: API Error Handling")
    print("=" * 50)
    
    client = DefenSysAPIClient()
    
    try:
        # Test invalid scan category
        result = client.scan_repository(
            "https://github.com/test/repo",
            "invalid_scan_type"
        )
    except requests.exceptions.RequestException as e:
        print(f"❌ API Error handled: {e}")
    
    try:
        # Test missing repository URL
        result = client.scan_repository("", "code_security")
    except requests.exceptions.RequestException as e:
        print(f"❌ Validation Error handled: {e}")
    
    print("✅ Error handling examples completed")
    print("")

# =============================================================================
# EXAMPLE 8: Custom API Calls with Requests
# =============================================================================

def example_8_raw_api_calls():
    """Example: Direct API calls using requests library"""
    print("🧪 Example 8: Raw API Calls")
    print("=" * 50)
    
    base_url = "http://localhost:8002"
    
    # 1. Get available scan options
    print("1️⃣ Getting scan options...")
    response = requests.get(f"{base_url}/api/scan/options")
    if response.status_code == 200:
        options = response.json()
        print(f"   📋 Available scans: {len(options['scan_options'])}")
    
    # 2. Start a scan
    print("2️⃣ Starting scan...")
    scan_payload = {
        "repository_url": "https://github.com/example/test-repo",
        "scan_category": "secrets_check",
        "project_name": "API Test Project"
    }
    
    response = requests.post(f"{base_url}/api/scan/simple", json=scan_payload)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ {result['message']}")
        print(f"   🆔 Scan ID: {result['scan_id']}")
    
    # 3. Check scanner status
    print("3️⃣ Checking scanner status...")
    response = requests.get(f"{base_url}/api/scanners")
    if response.status_code == 200:
        scanners = response.json()
        print(f"   🔧 Available scanners: {len(scanners['available_scanners'])}")
    
    print("")

# =============================================================================
# MAIN DEMO RUNNER
# =============================================================================

def run_all_examples():
    """Run all API testing examples"""
    print("🚀 DefenSys API Testing Examples")
    print("=" * 60)
    print("This demonstrates all the ways users can test with DefenSys")
    print("")
    
    examples = [
        example_1_basic_repo_scan,
        example_2_multiple_scan_types,
        example_3_file_upload_testing,
        example_4_local_path_scanning,
        example_5_cicd_integration,
        example_6_batch_testing,
        example_7_error_handling,
        example_8_raw_api_calls
    ]
    
    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"❌ Example failed: {e}")
            print("")
    
    print("🎉 All API testing examples completed!")
    print("")
    print("📚 Summary of Testing Methods:")
    print("✅ Git repository scanning")
    print("✅ Single file upload scanning")
    print("✅ ZIP folder upload scanning") 
    print("✅ Local path scanning")
    print("✅ Batch repository scanning")
    print("✅ CI/CD pipeline integration")
    print("✅ Error handling patterns")
    print("✅ Raw API call examples")

if __name__ == "__main__":
    run_all_examples()

# =============================================================================
# CURL COMMAND EXAMPLES (for non-Python users)
# =============================================================================

curl_examples = """
# Basic repository scan
curl -X POST "http://localhost:8002/api/scan/simple" \
     -H "Content-Type: application/json" \
     -d '{
       "repository_url": "https://github.com/user/repo",
       "scan_category": "code_security",
       "project_name": "My Project"
     }'

# Get scan options
curl -X GET "http://localhost:8002/api/scan/options"

# Upload file for scanning
curl -X POST "http://localhost:8002/api/upload/file" \
     -F "file=@vulnerable_app.py" \
     -F "scan_category=secrets_check" \
     -F "project_name=File Test"

# Scan local path
curl -X POST "http://localhost:8002/api/scan/local-path" \
     -H "Content-Type: application/json" \
     -d '{
       "path": "/path/to/project",
       "scan_category": "comprehensive_audit"
     }'

# Get all scans
curl -X GET "http://localhost:8002/api/scans/"

# Get scan recommendations
curl -X POST "http://localhost:8002/api/scan/recommendations" \
     -H "Content-Type: application/json" \
     -d '{
       "repository_url": "https://github.com/user/repo"
     }'
"""

print("💻 CURL Command Examples saved in curl_examples variable")
print("Use these for testing from command line or other tools!")
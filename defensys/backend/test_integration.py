#!/usr/bin/env python3
"""Integration test to verify DefenSys works end-to-end"""

import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {response.status_code} - {response.json()}")
    return response.status_code == 200

def test_create_project():
    """Test creating a new project"""
    project_data = {
        "name": "Test Project",
        "description": "A test project for integration testing",
        "repository_url": "https://github.com/example/test-project"
    }
    
    response = requests.post(f"{BASE_URL}/projects/", json=project_data)
    print(f"Create project: {response.status_code} - {response.json()}")
    
    if response.status_code == 200:
        return response.json()["id"]
    return None

def test_start_scan(project_id):
    """Test starting a scan for a project"""
    scan_data = {
        "project_id": project_id,
        "scan_type": "full",
        "path": "/tmp/test"  # Dummy path for testing
    }
    
    response = requests.post(f"{BASE_URL}/scans/", json=scan_data)
    print(f"Start scan: {response.status_code} - {response.json()}")
    
    if response.status_code == 200:
        return response.json()["id"]
    return None

def test_get_projects():
    """Test listing all projects"""
    response = requests.get(f"{BASE_URL}/projects/")
    print(f"Get projects: {response.status_code} - Found {len(response.json())} projects")
    return response.status_code == 200

def test_get_scans():
    """Test listing all scans"""
    response = requests.get(f"{BASE_URL}/scans/")
    print(f"Get scans: {response.status_code} - Found {len(response.json())} scans")
    return response.status_code == 200

def run_integration_test():
    """Run the complete integration test"""
    print("=" * 50)
    print("DefenSys Integration Test")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    if not test_health():
        print("❌ Health check failed!")
        return False
    
    # Test 2: Create project
    print("\n2. Testing project creation...")
    project_id = test_create_project()
    if not project_id:
        print("❌ Project creation failed!")
        return False
    
    # Test 3: Start scan
    print("\n3. Testing scan creation...")
    scan_id = test_start_scan(project_id)
    if not scan_id:
        print("❌ Scan creation failed!")
        return False
    
    # Test 4: List projects
    print("\n4. Testing project listing...")
    if not test_get_projects():
        print("❌ Project listing failed!")
        return False
    
    # Test 5: List scans
    print("\n5. Testing scan listing...")
    if not test_get_scans():
        print("❌ Scan listing failed!")
        return False
    
    print("\n" + "=" * 50)
    print("✅ All integration tests passed!")
    print("DefenSys is working correctly!")
    print("=" * 50)
    return True

if __name__ == "__main__":
    try:
        success = run_integration_test()
        exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to DefenSys API at http://localhost:8000")
        print("Please make sure the server is running with: uvicorn api.main:app --reload")
        exit(1)
    except Exception as e:
        print(f"❌ Integration test failed with error: {e}")
        exit(1)
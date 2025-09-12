#!/usr/bin/env python3
"""
DefenSys Platform Management Script
Manages the DefenSys DevSecOps vulnerability scanning platform
"""

import subprocess
import sys
import os
import time
import requests

def start_services():
    """Start DefenSys services"""
    print("🚀 Starting DefenSys Platform...")
    
    # Start API server (using actual path)
    print("📡 Starting DefenSys API...")
    api_process = subprocess.Popen([
        sys.executable, "backend/VulnAlert/src/simple_server.py"
    ], cwd=os.getcwd())
    
    # Wait a moment for API to start
    time.sleep(3)
    
    # Start frontend (using actual path)
    print("🎨 Starting DefenSys Dashboard...")
    frontend_process = subprocess.Popen([
        "npm", "run", "dev"
    ], cwd="frontend/vulnwatch-dash")
    
    print("✅ DefenSys is starting up...")
    print("📊 Dashboard: http://localhost:8080")
    print("🔌 API: http://localhost:5000")
    
    return api_process, frontend_process

def scan_repository(repo_url):
    """Scan a repository for vulnerabilities"""
    print(f"🔍 Scanning repository: {repo_url}")
    
    try:
        response = requests.post("http://localhost:5000/api/scan", 
                               json={"target": repo_url})
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Scan completed: {results}")
        else:
            print(f"❌ Scan failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error scanning: {e}")

def check_status():
    """Check DefenSys service status"""
    print("📊 Checking DefenSys Status...")
    
    try:
        api_response = requests.get("http://localhost:5000/api/overview")
        print(f"✅ API Status: {api_response.status_code}")
    except:
        print("❌ API: Not running")
    
    try:
        frontend_response = requests.get("http://localhost:8080")
        print(f"✅ Frontend Status: {frontend_response.status_code}")
    except:
        print("❌ Frontend: Not running")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python defensys.py [start|scan|status]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "start":
        start_services()
    elif command == "scan":
        if len(sys.argv) < 3:
            print("Usage: python defensys.py scan <repository_url>")
            sys.exit(1)
        scan_repository(sys.argv[2])
    elif command == "status":
        check_status()
    else:
        print("Unknown command. Use: start, scan, or status")

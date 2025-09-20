#!/usr/bin/env python3
"""
Test the API endpoints directly without running a web server
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from api.main import app

def test_api_endpoints():
    """Test the user-friendly API endpoints"""
    
    print("🌐 TESTING API ENDPOINTS")
    print("=" * 50)
    
    client = TestClient(app)
    
    # Test 1: Get scan options
    print("\n1. 📋 Testing /api/scan/options")
    response = client.get("/api/scan/options")
    if response.status_code == 200:
        options = response.json()
        print(f"   ✅ Success! Response: {type(options)}")
        print(f"   📝 Content preview: {str(options)[:100]}...")
    else:
        print(f"   ❌ Failed: {response.status_code}")
    
    # Test 2: Get scan recommendations  
    print("\n2. 💡 Testing /api/scan/recommendations")
    response = client.post("/api/scan/recommendations", json={
        "repository_url": "https://github.com/test/python-app"
    })
    if response.status_code == 200:
        recommendations = response.json()
        print(f"   ✅ Success! Got {len(recommendations['recommendations'])} recommendations")
        print(f"   🎯 Top recommendation: {recommendations['recommendations'][0]['display_name']}")
    else:
        print(f"   ❌ Failed: {response.status_code}")
    
    # Test 3: Root endpoint
    print("\n3. 🏠 Testing root endpoint")
    response = client.get("/")
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Success! Message: {result['message']}")
    else:
        print(f"   ❌ Failed: {response.status_code}")
    
    print("\n🎉 API testing complete!")

if __name__ == "__main__":
    test_api_endpoints()
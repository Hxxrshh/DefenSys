#!/usr/bin/env python3
"""
DefenSys DAST Integration Demo
Shows the new Dynamic Application Security Testing capabilities
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scanners.user_friendly import UserFriendlyScanManager

def demo_dast_options():
    """Demo the new DAST scanning options"""
    
    print("🎯 DEFENSYS - NOW WITH DYNAMIC SECURITY TESTING!")
    print("=" * 60)
    print("✨ New DAST (Dynamic Application Security Testing) Options")
    print("🌐 Test your RUNNING applications for real-world vulnerabilities")
    print("=" * 60)
    
    manager = UserFriendlyScanManager()
    options = manager.get_scan_options_for_frontend()
    
    # Filter and display DAST options
    dast_options = [opt for opt in options if 'test' in opt['value'].lower() or 'penetration' in opt['value'].lower()]
    
    print(f"\n🆕 NEW DAST SCAN OPTIONS ({len(dast_options)} available):")
    print("-" * 50)
    
    for i, option in enumerate(dast_options, 1):
        print(f"\n{i}. {option['label']}")
        print(f"   {option['description']}")
        print(f"   💡 {option['use_case']}")
        print(f"   ⏱️  {option['estimated_time']} | 📊 {option['complexity']}")
        print(f"   🔧 {option['tools_used']}")
    
    print(f"\n📋 COMPLETE SCAN PORTFOLIO ({len(options)} total options):")
    print("-" * 50)
    
    # Categorize all options
    static_options = [opt for opt in options if 'test' not in opt['value'].lower() and 'penetration' not in opt['value'].lower()]
    
    print(f"\n📊 STATIC ANALYSIS (SAST): {len(static_options)} options")
    for opt in static_options:
        print(f"   • {opt['label']}")
    
    print(f"\n🎯 DYNAMIC ANALYSIS (DAST): {len(dast_options)} options")
    for opt in dast_options:
        print(f"   • {opt['label']}")
    
    print("\n" + "=" * 60)
    print("🚀 DAST TOOLS AVAILABLE FOR INTEGRATION:")
    print("=" * 60)
    
    tools_info = {
        "OWASP ZAP": {
            "type": "Free/Open Source",
            "strength": "Comprehensive web app testing",
            "command": "zap.sh -cmd -quickurl http://target.com"
        },
        "Nuclei": {
            "type": "Free/Open Source", 
            "strength": "Fast template-based scanning",
            "command": "nuclei -u http://target.com -json-export results.json"
        },
        "Nikto": {
            "type": "Free/Open Source",
            "strength": "Web server configuration testing",
            "command": "nikto -h http://target.com -Format json"
        },
        "SQLMap": {
            "type": "Free/Open Source",
            "strength": "SQL injection detection & exploitation",
            "command": "sqlmap -u 'http://target.com/page?id=1' --batch"
        }
    }
    
    for tool, info in tools_info.items():
        print(f"\n🔧 {tool}")
        print(f"   Type: {info['type']}")
        print(f"   Strength: {info['strength']}")
        print(f"   Command: {info['command']}")
    
    print("\n" + "=" * 60)
    print("💡 HOW DAST COMPLEMENTS EXISTING SAST TOOLS:")
    print("=" * 60)
    
    comparison = [
        {
            "aspect": "Testing Method",
            "SAST": "Analyzes source code (static)",
            "DAST": "Tests running application (dynamic)"
        },
        {
            "aspect": "Vulnerabilities Found",
            "SAST": "Code-level issues, logic flaws",
            "DAST": "Runtime issues, configuration problems"
        },
        {
            "aspect": "Requirements",
            "SAST": "Source code access needed",
            "DAST": "Running application URL needed"
        },
        {
            "aspect": "Best Used For",
            "SAST": "Development phase testing",
            "DAST": "Pre-production & production testing"
        }
    ]
    
    for comp in comparison:
        print(f"\n{comp['aspect']}:")
        print(f"   SAST: {comp['SAST']}")
        print(f"   DAST: {comp['DAST']}")
    
    print("\n" + "=" * 60)
    print("✅ IMPLEMENTATION STATUS:")
    print("=" * 60)
    print("✅ DAST scanner framework created (`scanners/dast.py`)")
    print("✅ OWASP ZAP integration implemented")
    print("✅ Nuclei template scanner implemented") 
    print("✅ Nikto web server scanner implemented")
    print("✅ User-friendly interface updated with DAST options")
    print("✅ Ready for deployment!")
    
    print("\n🎯 NEXT STEPS TO USE DAST:")
    print("1. Install DAST tools (zap, nuclei, nikto)")
    print("2. Deploy your application to a test environment")
    print("3. Select 'Live Web Application Security Test' from dropdown")
    print("4. Enter your application URL")
    print("5. Get comprehensive dynamic security analysis!")

if __name__ == "__main__":
    demo_dast_options()
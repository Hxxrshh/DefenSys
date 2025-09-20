#!/usr/bin/env python3
"""
DefenSys Enhanced DAST Tools Demo
Shows all 5 DAST (Dynamic Application Security Testing) capabilities
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scanners.user_friendly import UserFriendlyScanManager
from scanners.dast import DastScannerManager

def demo_enhanced_dast_tools():
    """Demo the enhanced DAST scanning capabilities"""
    
    print("🚀 DEFENSYS - ENHANCED DAST SECURITY TESTING!")
    print("=" * 70)
    print("✨ Now featuring 5 powerful DAST tools for dynamic security testing")
    print("🎯 Test your RUNNING applications for real-world vulnerabilities")
    print("=" * 70)
    
    # Initialize managers
    user_manager = UserFriendlyScanManager()
    dast_manager = DastScannerManager()
    
    # Show available DAST scanners
    print("\n🛡️ AVAILABLE DAST SCANNERS:")
    print("-" * 50)
    
    available_scanners = dast_manager.get_available_scanners()
    
    scanner_info = {
        "zap": {
            "name": "OWASP ZAP", 
            "purpose": "Comprehensive web application security scanner",
            "strength": "Industry standard for web app testing",
            "targets": "Web applications, APIs, AJAX applications"
        },
        "nuclei": {
            "name": "Nuclei",
            "purpose": "Template-based vulnerability scanner", 
            "strength": "Fast scanning with community templates",
            "targets": "Web services, APIs, network services"
        },
        "nikto": {
            "name": "Nikto",
            "purpose": "Web server scanner and security auditor",
            "strength": "Comprehensive web server testing",
            "targets": "Web servers, CGI scripts, server configurations"
        },
        "sqlmap": {
            "name": "SQLMap",
            "purpose": "SQL injection detection and exploitation",
            "strength": "Most advanced SQL injection testing tool",
            "targets": "Database-driven web applications"
        },
        "nmap": {
            "name": "Nmap",
            "purpose": "Network discovery and security auditing",
            "strength": "Network reconnaissance and port scanning",
            "targets": "Network hosts, open ports, services"
        }
    }
    
    for scanner_id, info in scanner_info.items():
        status = "✅ Available" if available_scanners.get(scanner_id, False) else "❌ Not installed"
        print(f"\n{info['name']} ({scanner_id.upper()})")
        print(f"   Status: {status}")
        print(f"   Purpose: {info['purpose']}")
        print(f"   Strength: {info['strength']}")
        print(f"   Targets: {info['targets']}")
    
    # Show user-friendly DAST options
    print("\n" + "=" * 70)
    print("🎨 USER-FRIENDLY DAST SCAN OPTIONS:")
    print("=" * 70)
    
    options = user_manager.get_scan_options_for_frontend()
    dast_options = [opt for opt in options if any(keyword in opt['value'].lower() 
                   for keyword in ['testing', 'penetration'])]
    
    for i, option in enumerate(dast_options, 1):
        print(f"\n{i}. {option['label']}")
        print(f"   📋 {option['description']}")
        print(f"   💡 Use Case: {option['use_case']}")
        print(f"   ⏱️  {option['estimated_time']} | 📊 {option['complexity']}")
        print(f"   🔧 Tools: {option['tools_used']}")
    
    # Security testing comparison
    print("\n" + "=" * 70)
    print("🆚 DAST vs SAST COMPARISON:")
    print("=" * 70)
    
    comparison = [
        {
            "aspect": "Testing Approach",
            "DAST": "Tests running application (black-box)",
            "SAST": "Analyzes source code (white-box)"
        },
        {
            "aspect": "Vulnerabilities Found",
            "DAST": "Runtime issues, config problems, injection flaws",
            "SAST": "Code-level issues, logic flaws, coding errors"
        },
        {
            "aspect": "Requirements",
            "DAST": "Running application URL required",
            "SAST": "Source code access required"
        },
        {
            "aspect": "False Positives",
            "DAST": "Lower false positives (real vulnerabilities)",
            "SAST": "Higher false positives (potential issues)"
        },
        {
            "aspect": "Testing Phase",
            "DAST": "Integration, staging, production testing",
            "SAST": "Development, code review, CI/CD"
        }
    ]
    
    for comp in comparison:
        print(f"\n{comp['aspect']}:")
        print(f"   DAST: {comp['DAST']}")
        print(f"   SAST: {comp['SAST']}")
    
    # Advanced DAST techniques
    print("\n" + "=" * 70)
    print("🔬 ADVANCED DAST TECHNIQUES:")
    print("=" * 70)
    
    techniques = {
        "Automated Crawling": {
            "tools": "ZAP, Nuclei",
            "description": "Automatically discover web pages and endpoints",
            "benefit": "Comprehensive application mapping"
        },
        "SQL Injection Testing": {
            "tools": "SQLMap, ZAP",
            "description": "Test for database injection vulnerabilities",
            "benefit": "Critical data security validation"
        },
        "Template-based Scanning": {
            "tools": "Nuclei",
            "description": "Use community-contributed vulnerability templates",
            "benefit": "Latest vulnerability detection"
        },
        "Network Reconnaissance": {
            "tools": "Nmap",
            "description": "Discover services and potential attack vectors",
            "benefit": "Infrastructure security assessment"
        },
        "Web Server Analysis": {
            "tools": "Nikto",
            "description": "Analyze web server configuration and security",
            "benefit": "Server hardening recommendations"
        }
    }
    
    for technique, details in techniques.items():
        print(f"\n🔧 {technique}")
        print(f"   Tools: {details['tools']}")
        print(f"   Description: {details['description']}")
        print(f"   Benefit: {details['benefit']}")
    
    # Usage examples
    print("\n" + "=" * 70)
    print("📚 USAGE EXAMPLES:")
    print("=" * 70)
    
    examples = [
        {
            "scenario": "E-commerce Website Testing",
            "scan_type": "web_application_testing",
            "tools": "ZAP + Nuclei + Nmap",
            "command": 'curl -X POST "http://localhost:8000/api/simple-scan" -d \'{"url": "https://shop.example.com", "category": "web_application_testing"}\''
        },
        {
            "scenario": "REST API Security Audit",
            "scan_type": "api_security_testing", 
            "tools": "ZAP + Nuclei + SQLMap",
            "command": 'curl -X POST "http://localhost:8000/api/simple-scan" -d \'{"url": "https://api.example.com", "category": "api_security_testing"}\''
        },
        {
            "scenario": "Full Penetration Test",
            "scan_type": "penetration_testing",
            "tools": "All DAST tools (ZAP, Nuclei, Nikto, SQLMap, Nmap)",
            "command": 'curl -X POST "http://localhost:8000/api/simple-scan" -d \'{"url": "https://target.example.com", "category": "penetration_testing"}\''
        }
    ]
    
    for example in examples:
        print(f"\n🎯 {example['scenario']}")
        print(f"   Scan Type: {example['scan_type']}")
        print(f"   Tools Used: {example['tools']}")
        print(f"   Command: {example['command']}")
    
    print("\n" + "=" * 70)
    print("✅ DEFENSYS DAST ENHANCEMENT COMPLETE!")
    print("=" * 70)
    print("🎉 You now have 5 powerful DAST tools integrated:")
    print("   • OWASP ZAP - Industry standard web app scanner")
    print("   • Nuclei - Fast template-based vulnerability scanner")
    print("   • Nikto - Comprehensive web server scanner")
    print("   • SQLMap - Advanced SQL injection testing")
    print("   • Nmap - Network discovery and security auditing")
    print("\n🌟 Total Security Arsenal: 13 SAST + 5 DAST = 18 Security Tools!")
    print("🚀 Your DefenSys platform is now enterprise-ready!")

if __name__ == "__main__":
    demo_enhanced_dast_tools()
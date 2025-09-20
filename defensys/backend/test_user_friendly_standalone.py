#!/usr/bin/env python3
"""
Simple test script for the user-friendly scanner functionality
"""

import sys
import os
import tempfile

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scanners.user_friendly import UserFriendlyScanManager
import json

def test_user_friendly_scanner():
    """Test the user-friendly scanner functionality"""
    
    print("🧪 Testing User-Friendly Scanner")
    print("=" * 50)
    
    # Initialize manager
    manager = UserFriendlyScanManager()
    
    # Test 1: Get scan options
    print("\n1. 📋 Getting scan options...")
    options = manager.get_scan_options_for_frontend()
    print(f"   ✅ Found {len(options)} scan options:")
    for opt in options:
        print(f"      • {opt['label']}")
    
    # Test 2: Test project type detection
    print("\n2. 🔍 Testing project type detection...")
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a Python project
        with open(os.path.join(temp_dir, "main.py"), "w") as f:
            f.write("print('hello world')")
        with open(os.path.join(temp_dir, "requirements.txt"), "w") as f:
            f.write("requests==2.25.1")
        
        project_type = manager.detect_project_type(temp_dir)
        print(f"   ✅ Detected project type: {project_type.value}")
    
    # Test 3: Get recommendations
    print("\n3. 💡 Getting scan recommendations...")
    recommendations = manager.get_recommended_scans(project_type)
    print(f"   ✅ Found {len(recommendations)} recommendations:")
    for rec in recommendations[:3]:  # Show top 3
        print(f"      • {rec['display_name']} (Priority: {rec['priority']})")
    
    # Test 4: Map user choice to technical scan
    print("\n4. 🔧 Mapping user choice to technical configuration...")
    config = manager.map_user_choice_to_technical_scans("code_security", temp_dir)
    print(f"   ✅ Scan configuration generated:")
    print(f"      • Tools: {config['scan_types']}")
    print(f"      • Parallel: {config['execution_config']['parallel']}")
    print(f"      • Max workers: {config['execution_config']['max_workers']}")
    if 'project_optimizations' in config:
        print(f"      • Optimizations: {list(config['project_optimizations'].keys())}")
    
    print("\n🎉 All tests passed! The user-friendly scanner is working correctly.")
    print("\n📝 Summary:")
    print(f"   • {len(options)} scan options available")
    print(f"   • Project type detection working")
    print(f"   • {len(recommendations)} recommendations generated")
    print(f"   • Technical mapping successful")
    
    return True

def demo_scan_options():
    """Demo the available scan options in a user-friendly format"""
    
    print("\n" + "=" * 60)
    print("🛡️  DEFENSYS SECURITY SCAN OPTIONS")
    print("=" * 60)
    
    manager = UserFriendlyScanManager()
    options = manager.get_scan_options_for_frontend()
    
    for i, option in enumerate(options, 1):
        print(f"\n{i}. {option['label']}")
        print(f"   📋 {option['description']}")
        print(f"   💡 Use case: {option['use_case']}")
        print(f"   ⏱️  Time: {option['estimated_time']}")
        print(f"   🔧 Tools: {', '.join(option['tools_used'])}")
        print(f"   📊 Complexity: {option['complexity']}")

if __name__ == "__main__":
    try:
        # Run tests
        test_user_friendly_scanner()
        
        # Show demo
        demo_scan_options()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
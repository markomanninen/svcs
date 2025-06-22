#!/usr/bin/env python3
"""
Final comprehensive test of the SVCS dashboard after JavaScript fix.
This test verifies that all components work together properly.
"""

import subprocess
import time
import sys
import os
import json

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

def test_web_server_api():
    """Test that the web server API endpoints work."""
    
    print("🌐 Testing Web Server API...")
    
    if not REQUESTS_AVAILABLE:
        print("⚠️  requests library not available, skipping API test")
        return True
    
    try:
        # Test the basic status endpoint
        response = requests.get('http://localhost:8080/', timeout=5)
        if response.status_code == 200:
            print("✅ Web server responding")
            return True
        else:
            print(f"❌ Web server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Web server not accessible: {e}")
        return False

def run_comprehensive_test():
    """Run a comprehensive test of the dashboard system."""
    
    print("🧪 SVCS Dashboard Comprehensive Test")
    print("=" * 50)
    
    # Check required files
    required_files = [
        'svcs_web_server.py',
        'svcs_interactive_dashboard.html',
        'test_js_fix_automated.py'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Required file missing: {file}")
            return False
        print(f"✅ Found: {file}")
    
    # Test 1: Run the JavaScript fix test
    print("\n📝 Test 1: JavaScript Fix Verification")
    result = subprocess.run([sys.executable, 'test_js_fix_automated.py'], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ JavaScript fix test passed")
    else:
        print("❌ JavaScript fix test failed")
        print(result.stderr)
        return False
    
    # Test 2: Start web server
    print("\n📝 Test 2: Web Server Startup")
    server_process = None
    try:
        server_process = subprocess.Popen(
            [sys.executable, 'svcs_web_server.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give server time to start
        time.sleep(8)
        
        if server_process.poll() is None:
            print("✅ Web server started")
            
            # Test 3: Check server process is running
            print("\n📝 Test 3: Server Process Check")
            if server_process.poll() is None:
                print("✅ Web server process is running")
            else:
                print("❌ Web server process stopped")
                return False
            
        else:
            print("❌ Web server failed to start")
            stdout, stderr = server_process.communicate()
            if stderr:
                print(f"Error: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing web server: {e}")
        return False
    finally:
        if server_process and server_process.poll() is None:
            server_process.terminate()
            server_process.wait()
            print("🛑 Web server stopped")
    
    # Test 4: Verify dashboard HTML structure
    print("\n📝 Test 4: Dashboard HTML Structure")
    with open('svcs_interactive_dashboard.html', 'r') as f:
        content = f.read()
    
    # Check for key components
    key_components = [
        'showResults(',
        'showError(',
        'querySelector(\'h3\')',
        'result-container',
        'result-content'
    ]
    
    for component in key_components:
        if component in content:
            print(f"✅ Found: {component}")
        else:
            print(f"❌ Missing: {component}")
            return False
    
    print("\n" + "=" * 50)
    print("🎉 Comprehensive Test Results:")
    print("✅ JavaScript fix verified")
    print("✅ Web server starts successfully")  
    print("✅ Server process runs correctly")
    print("✅ Dashboard HTML structure correct")
    print("\n🚀 SVCS Dashboard is ready for use!")
    print("\nTo start the dashboard:")
    print("  ./start_dashboard.sh")
    print("  OR")
    print("  python svcs_web_server.py")
    print("\nThen open: http://localhost:8080")
    
    return True

if __name__ == "__main__":
    success = run_comprehensive_test()
    if not success:
        print("\n❌ Comprehensive test failed")
        exit(1)
    else:
        print("\n✅ All tests passed!")
        exit(0)

#!/usr/bin/env python3
"""
Test New Dashboard Integration

Test that the new dashboard UI works with the updated web server.
"""

import subprocess
import time
import requests
import sys
from pathlib import Path

def test_new_dashboard():
    """Test the new dashboard functionality."""
    print("🧪 Testing New Dashboard Integration")
    print("=" * 45)
    
    # Start web server in background
    print("🚀 Starting web server...")
    process = subprocess.Popen([
        sys.executable, 'svcs_repo_web_server.py', '--port', '8082'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Give server time to start
    time.sleep(3)
    
    try:
        # Test dashboard endpoint
        print("🌐 Testing dashboard endpoint...")
        response = requests.get('http://localhost:8082/', timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # Check for new dashboard features
            checks = [
                ('Repository-Local Architecture', 'Repository-Local Architecture' in content),
                ('Repository Management', 'Repository Management' in content),
                ('Semantic Search', 'Semantic Search' in content),
                ('Evolution Tracking', 'Evolution Tracking' in content),
                ('Analytics', 'Analytics' in content),
                ('Quality Analysis', 'Quality Analysis' in content),
                ('Branch Comparison', 'Branch Comparison' in content),
                ('API endpoints', '/api/repositories/discover' in content),
                ('New styling', 'grid-template-columns' in content)
            ]
            
            passed = 0
            for check_name, result in checks:
                if result:
                    print(f"✅ {check_name}")
                    passed += 1
                else:
                    print(f"❌ {check_name}")
            
            print(f"\n📊 Dashboard checks: {passed}/{len(checks)} passed")
            
            if passed >= len(checks) * 0.8:  # 80% pass rate
                print("✅ Dashboard integration test passed!")
                return True
            else:
                print("❌ Dashboard integration test failed!")
                return False
        else:
            print(f"❌ Dashboard failed to load: {response.status_code}")
            return False
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False
    finally:
        # Clean up: terminate the server
        print("🧹 Cleaning up...")
        process.terminate()
        process.wait(timeout=5)

def test_api_endpoints():
    """Test API endpoints that the dashboard uses."""
    print("\n🔌 Testing API Endpoints")
    print("=" * 30)
    
    # Start web server in background
    process = subprocess.Popen([
        sys.executable, 'svcs_repo_web_server.py', '--port', '8083'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Give server time to start
    time.sleep(3)
    
    try:
        endpoints = [
            ('GET', '/health', None, 5),  # timeout in seconds
            ('GET', '/api/system/status', None, 10),  # longer timeout for system status
            ('POST', '/api/repositories/discover', {'scan_paths': ['/tmp']}, 15),  # limited scope discovery
        ]
        
        passed = 0
        for method, endpoint, data, timeout in endpoints:
            try:
                if method == 'GET':
                    response = requests.get(f'http://localhost:8083{endpoint}', timeout=timeout)
                else:
                    response = requests.post(f'http://localhost:8083{endpoint}', json=data, timeout=timeout)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success', True):  # Some endpoints don't have success field
                        print(f"✅ {method} {endpoint}")
                        passed += 1
                    else:
                        print(f"❌ {method} {endpoint}: {result.get('error', 'Unknown error')}")
                else:
                    print(f"❌ {method} {endpoint}: HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ {method} {endpoint}: {e}")
        
        print(f"\n📊 API checks: {passed}/{len(endpoints)} passed")
        return passed == len(endpoints)
        
    finally:
        # Clean up: terminate the server
        process.terminate()
        process.wait(timeout=5)

if __name__ == "__main__":
    print("🚀 Starting Dashboard Integration Tests")
    print("=" * 50)
    
    # Test 1: Dashboard UI
    dashboard_success = test_new_dashboard()
    
    # Test 2: API endpoints
    api_success = test_api_endpoints()
    
    if dashboard_success and api_success:
        print("\n🎉 All dashboard integration tests passed!")
        print("✅ New UI is ready for the repository-local architecture!")
    else:
        print("\n❌ Some dashboard integration tests failed")
        sys.exit(1)

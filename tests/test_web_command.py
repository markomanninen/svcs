#!/usr/bin/env python3
"""
Test Web Command Integration

Test that svcs web start properly launches the new web server.
"""

import subprocess
import time
import requests
import sys
from pathlib import Path

def test_web_command():
    """Test the svcs web command integration."""
    print("🧪 Testing SVCS Web Command Integration")
    print("=" * 45)
    
    # Start web server in background
    print("🚀 Starting web server...")
    process = subprocess.Popen([
        sys.executable, '-m', 'svcs.cli', 'web', 'start', '--port', '8081'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Give server time to start
    time.sleep(3)
    
    try:
        # Test health endpoint
        print("🏥 Testing health endpoint...")
        response = requests.get('http://localhost:8081/health', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['service']}")
            print(f"   Version: {data['version']}")
            print(f"   Architecture: {data['architecture']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
        
        # Test system status
        print("📊 Testing system status...")
        response = requests.get('http://localhost:8081/api/system/status', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ System status OK: {data['data']['architecture']}")
            print(f"   Capabilities: {len(data['data']['capabilities'])} features")
        else:
            print(f"❌ System status failed: {response.status_code}")
            return False
        
        print("\n🎉 Web command integration test passed!")
        return True
        
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

if __name__ == "__main__":
    success = test_web_command()
    if not success:
        print("\n❌ Web command integration test failed")
        sys.exit(1)
    else:
        print("✅ Web command integration is working!")

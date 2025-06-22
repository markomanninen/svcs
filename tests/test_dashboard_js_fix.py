#!/usr/bin/env python3
"""
Test script to verify the JavaScript error fix in the dashboard.
This script starts the web server and provides instructions for testing.
"""

import subprocess
import time
import sys
import os

def test_dashboard_fix():
    """Test the dashboard JavaScript fix."""
    
    print("🔧 Testing Dashboard JavaScript Fix")
    print("=" * 50)
    
    # Check if the web server file exists
    if not os.path.exists('svcs_web_server.py'):
        print("❌ svcs_web_server.py not found in current directory")
        return False
    
    # Check if the dashboard file exists
    if not os.path.exists('svcs_interactive_dashboard.html'):
        print("❌ svcs_interactive_dashboard.html not found in current directory")
        return False
    
    print("✅ Dashboard files found")
    
    # Start the web server in the background
    print("\n🚀 Starting web server...")
    try:
        server_process = subprocess.Popen(
            [sys.executable, 'svcs_web_server.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give the server time to start
        time.sleep(3)
        
        # Check if server is still running
        if server_process.poll() is None:
            print("✅ Web server started successfully")
            print("\n📋 Manual Testing Instructions:")
            print("-" * 40)
            print("1. Open your browser and go to: http://localhost:5000")
            print("2. Try these operations to test the JavaScript fix:")
            print("   a. Perform a semantic search (valid operation)")
            print("   b. Try an invalid operation to trigger an error")
            print("   c. Then perform another valid operation")
            print("   d. Check browser console for JavaScript errors")
            print("\n🔍 What to look for:")
            print("   - No 'container.querySelector('h3') is null' errors in console")
            print("   - Error messages display properly without breaking the UI")
            print("   - Subsequent operations work after an error")
            
            input("\nPress Enter when you've finished testing...")
            
            # Stop the server
            server_process.terminate()
            server_process.wait()
            print("🛑 Web server stopped")
            
            return True
            
        else:
            print("❌ Web server failed to start")
            stdout, stderr = server_process.communicate()
            if stderr:
                print(f"Error: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error starting web server: {e}")
        return False

if __name__ == "__main__":
    success = test_dashboard_fix()
    if success:
        print("\n✅ Dashboard JavaScript fix test completed")
        print("If you saw no JavaScript errors in the browser console,")
        print("the fix was successful!")
    else:
        print("\n❌ Dashboard JavaScript fix test failed")
    
    sys.exit(0 if success else 1)

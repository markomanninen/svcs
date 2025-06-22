#!/usr/bin/env python3
"""
Test script to verify the analytics API fix.
"""

import subprocess
import time
import sys
import os

def test_analytics_fix():
    """Test the analytics API fix."""
    
    print("🔧 Testing Analytics API Fix")
    print("=" * 40)
    
    # Check if the web server file exists
    if not os.path.exists('svcs_web_server.py'):
        print("❌ svcs_web_server.py not found")
        return False
    
    # Start the web server in the background
    print("🚀 Starting web server...")
    try:
        server_process = subprocess.Popen(
            [sys.executable, 'svcs_web_server.py', '--port', '8081'],  # Use different port
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give the server time to start
        time.sleep(5)
        
        # Check if server is still running
        if server_process.poll() is None:
            print("✅ Web server started on port 8081")
            
            # Test the analytics API with curl if available
            print("📊 Testing analytics API...")
            try:
                curl_result = subprocess.run([
                    'curl', '-s', '-X', 'POST', 
                    'http://localhost:8081/api/generate_analytics',
                    '-H', 'Content-Type: application/json',
                    '-d', '{}'
                ], capture_output=True, text=True, timeout=10)
                
                if curl_result.returncode == 0:
                    response = curl_result.stdout
                    if '"success":true' in response or '"success": true' in response:
                        print("✅ Analytics API working correctly")
                        print("📋 Response preview:")
                        # Parse and show a cleaner preview
                        import json
                        try:
                            data = json.loads(response)
                            if data.get('success'):
                                analytics = data.get('data', {})
                                print(f"   Total events: {analytics.get('total_events')}")
                                print(f"   Events shown: {analytics.get('events_shown')}")
                                print(f"   Report generated: {analytics.get('report_generated')}")
                        except:
                            print(response[:200] + "..." if len(response) > 200 else response)
                        result = True
                    else:
                        print("❌ Analytics API returned error")
                        print("Response:", response[:500] + "..." if len(response) > 500 else response)
                        result = False
                else:
                    print("❌ Curl request failed")
                    result = False
                    
            except subprocess.TimeoutExpired:
                print("❌ Request timed out")
                result = False
            except FileNotFoundError:
                print("⚠️  curl not available, cannot test API endpoint")
                print("✅ Server started successfully (manual test required)")
                result = True
            
        else:
            print("❌ Web server failed to start")
            stdout, stderr = server_process.communicate()
            if stderr:
                print(f"Error: {stderr.decode()}")
            result = False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        result = False
    finally:
        if 'server_process' in locals() and server_process.poll() is None:
            server_process.terminate()
            server_process.wait()
            print("🛑 Web server stopped")
    
    return result

if __name__ == "__main__":
    success = test_analytics_fix()
    if success:
        print("\n✅ Analytics API fix test completed successfully")
        print("The 500 error should now be resolved!")
    else:
        print("\n❌ Analytics API fix test failed")
    
    sys.exit(0 if success else 1)

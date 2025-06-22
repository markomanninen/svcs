#!/usr/bin/env python3
"""
SVCS Interactive Dashboard Demo

This script demonstrates the key features of the SVCS interactive web dashboard.
It opens the dashboard in your default browser and provides a guided tour.
"""

import webbrowser
import time
import sys
import subprocess
import os
from pathlib import Path

def print_banner():
    """Print the demo banner."""
    print("""
🧠 SVCS Interactive Dashboard Demo
===================================

This demo will:
1. Start the SVCS web server
2. Open the dashboard in your browser
3. Guide you through the key features

Prerequisites:
- You should be in a git repository with SVCS tracking
- Flask and Flask-CORS should be installed
- Some commits should have been analyzed by SVCS

""")

def check_prerequisites():
    """Check if the prerequisites are met."""
    print("🔍 Checking prerequisites...")
    
    # Check if we're in the right directory
    if not Path('svcs.py').exists():
        print("❌ Error: Not in SVCS root directory")
        print("   Please run this from the directory containing svcs.py")
        return False
    
    # Check if Flask is available
    try:
        import flask
        import flask_cors
        print("✅ Flask dependencies available")
    except ImportError:
        print("❌ Error: Flask dependencies not installed")
        print("   Run: pip install Flask Flask-CORS")
        return False
    
    # Check if we have SVCS data
    if not Path('.svcs').exists():
        print("❌ Error: No .svcs directory found")
        print("   Please initialize SVCS first")
        return False
    
    print("✅ Prerequisites checked")
    return True

def start_server():
    """Start the SVCS web server in the background."""
    print("🚀 Starting SVCS web server...")
    
    try:
        # Start the server in the background
        process = subprocess.Popen([
            sys.executable, 'svcs_web_server.py',
            '--host', '127.0.0.1',
            '--port', '8080'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give the server time to start
        time.sleep(3)
        
        # Check if the server is still running
        if process.poll() is None:
            print("✅ Server started successfully")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Server failed to start:")
            print(f"   stdout: {stdout.decode()}")
            print(f"   stderr: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return None

def open_dashboard():
    """Open the dashboard in the default browser."""
    print("🌐 Opening dashboard in browser...")
    
    url = "http://127.0.0.1:8080"
    try:
        webbrowser.open(url)
        print(f"✅ Dashboard opened: {url}")
        return True
    except Exception as e:
        print(f"❌ Error opening browser: {e}")
        print(f"   Please manually open: {url}")
        return False

def show_tour_guide():
    """Display the interactive tour guide."""
    print("""
🎯 Dashboard Tour Guide
======================

Your SVCS Interactive Dashboard is now open! Here's what to explore:

1. 🔍 SEMANTIC SEARCH (Active by default)
   - Try the quick action buttons: Performance, Error Handling, Architecture
   - Adjust filters: author, days back, confidence level
   - Click "Search Events" to see results

2. 📝 GIT INTEGRATION 
   - Enter a recent commit hash (get one from: git log --oneline -5)
   - Click "Changed Files" to see what was modified
   - Click "Show Diff" to see the actual code changes
   - Try "Full Summary" for semantic events + git info

3. 📈 CODE EVOLUTION
   - Enter a node ID like "func:main" or "class:MyClass"
   - Track how specific code elements evolved over time
   - Use filters to focus on recent or high-confidence changes

4. 🎯 PATTERN ANALYSIS
   - Select different pattern types (Performance, Architecture, etc.)
   - Adjust confidence thresholds to see different quality levels
   - Great for understanding code improvement trends

5. 📋 SYSTEM LOGS
   - View LLM inference logs to see what AI analysis was performed
   - Check error logs if you encounter issues
   - Monitor real-time SVCS activity

6. 🗂️ PROJECT MANAGEMENT
   - List all SVCS-tracked projects
   - View project statistics and health
   - Use debug tools if you encounter issues

7. 📊 ANALYTICS
   - Generate comprehensive reports
   - Run quality analysis to see improvement trends
   - Export data for external analysis

💡 TIPS:
- Start with "Recent Activity" to see what's been happening
- Use semantic search to find specific types of changes
- Combine git integration with semantic search for full context
- Check the browser console (F12) if you encounter issues

Press Ctrl+C in this terminal to stop the server when you're done exploring.
""")

def main():
    """Main demo function."""
    print_banner()
    
    if not check_prerequisites():
        sys.exit(1)
    
    # Start the server
    server_process = start_server()
    if not server_process:
        sys.exit(1)
    
    # Open the dashboard
    if not open_dashboard():
        print("Please manually open http://127.0.0.1:8080")
    
    # Show the tour guide
    show_tour_guide()
    
    try:
        # Keep the script running while the server is active
        print("🖥️  Server running... Press Ctrl+C to stop")
        while server_process.poll() is None:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Stopping server...")
        server_process.terminate()
        server_process.wait()
        print("✅ Server stopped. Thank you for trying the SVCS dashboard!")

if __name__ == '__main__':
    main()

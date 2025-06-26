#!/usr/bin/env python3
"""
Test script to verify LLM logging functionality
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the process_query function
from svcs_repo_discuss import process_query

def test_logging():
    print("🧪 Testing LLM logging functionality...")
    
    # Check if .svcs/logs directory exists
    logs_dir = Path(".svcs/logs")
    if not logs_dir.exists():
        print(f"📁 Creating logs directory: {logs_dir}")
        logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Test query
    test_query = "What is the current status of this repository?"
    
    print(f"🔍 Processing test query: '{test_query}'")
    
    try:
        response = process_query(test_query)
        print(f"✅ Response received: {response[:100]}...")
        
        # Check if log files were created
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = logs_dir / f"svcs_repo_discuss_{today}.jsonl"
        error_file = logs_dir / f"svcs_repo_discuss_errors_{today}.jsonl"
        
        if log_file.exists():
            print(f"✅ Log file created: {log_file}")
            with open(log_file, 'r') as f:
                lines = f.readlines()
                print(f"📊 Log entries: {len(lines)}")
        else:
            print(f"❌ No log file found: {log_file}")
        
        if error_file.exists():
            print(f"⚠️ Error log exists: {error_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        
        # Check if error was logged
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        error_file = logs_dir / f"svcs_repo_discuss_errors_{today}.jsonl"
        
        if error_file.exists():
            print(f"✅ Error logged to: {error_file}")
            with open(error_file, 'r') as f:
                lines = f.readlines()
                print(f"📊 Error entries: {len(lines)}")
        
        return False

if __name__ == "__main__":
    success = test_logging()
    sys.exit(0 if success else 1)

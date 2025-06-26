#!/usr/bin/env python3
"""
Test error logging by temporarily breaking the API key
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_error_logging():
    print("🧪 Testing error logging functionality...")
    
    # Backup the original API key
    original_key = os.environ.get('GOOGLE_API_KEY')
    
    try:
        # Set an invalid API key
        os.environ['GOOGLE_API_KEY'] = 'invalid_key_for_testing'
        
        # Import and test
        from svcs_repo_discuss import process_query
        
        response = process_query("This should fail with invalid API key")
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"Expected error occurred: {e}")
    finally:
        # Restore original API key
        if original_key:
            os.environ['GOOGLE_API_KEY'] = original_key
        elif 'GOOGLE_API_KEY' in os.environ:
            del os.environ['GOOGLE_API_KEY']
    
    # Check error logs
    today = datetime.now().strftime("%Y-%m-%d")
    error_file = Path(f".svcs/logs/svcs_repo_discuss_errors_{today}.jsonl")
    
    if error_file.exists():
        with open(error_file, 'r') as f:
            lines = f.readlines()
            print(f"✅ Error log created with {len(lines)} entries")
            if lines:
                print(f"📄 Latest error entry: {lines[-1][:100]}...")
            return True
    else:
        print("❌ No error log found")
        return False

if __name__ == "__main__":
    success = test_error_logging()
    sys.exit(0 if success else 1)

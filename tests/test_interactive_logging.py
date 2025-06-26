#!/usr/bin/env python3
"""
Test the interactive conversational interface with automatic input
"""

import sys
import os
import time
import subprocess
from pathlib import Path

def test_interactive_logging():
    print("🧪 Testing interactive session logging...")
    
    # Create a simple test input
    test_input = "hello\nexit\n"
    
    try:
        # Run the interactive session with input
        proc = subprocess.run(
            [sys.executable, "svcs_repo_discuss.py"],
            input=test_input,
            text=True,
            capture_output=True,
            timeout=30
        )
        
        print(f"✅ Interactive session completed")
        print(f"📤 Return code: {proc.returncode}")
        
        # Check logs
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = Path(f".svcs/logs/svcs_repo_discuss_{today}.jsonl")
        
        if log_file.exists():
            with open(log_file, 'r') as f:
                lines = f.readlines()
                print(f"📊 Total log entries: {len(lines)}")
                
                # Find interactive session entries
                interactive_entries = [line for line in lines if '"mode": "interactive"' in line]
                print(f"💬 Interactive entries: {len(interactive_entries)}")
                
                if interactive_entries:
                    print("✅ Interactive logging working!")
                    return True
                else:
                    print("⚠️ No interactive entries found")
                    return False
        else:
            print(f"❌ No log file found")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Test timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_interactive_logging()
    sys.exit(0 if success else 1)

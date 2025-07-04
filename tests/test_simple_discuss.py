#!/usr/bin/env python3
"""
Simple test to check if the discuss module shows raw diff output correctly.
"""

import subprocess
import sys
import os

# Check if GOOGLE_API_KEY is set
if not os.getenv("GOOGLE_API_KEY"):
    print("Error: GOOGLE_API_KEY not set. Please run: export GOOGLE_API_KEY='your_key_here'")
    sys.exit(1)

# Simple test queries
test_input = """Show me the raw git diff for commit 6104d18 - I want to see the exact code changes, not a summary
exit
"""

print("Testing raw diff display in discuss module...")
print("=" * 50)

try:
    result = subprocess.run(
        [sys.executable, "svcs_discuss.py"],
        input=test_input,
        text=True,
        capture_output=True,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    
    print("OUTPUT:")
    print(result.stdout)
    
    if result.stderr:
        print("\nERRORS:")
        print(result.stderr)
    
    # Check if the output contains raw diff indicators
    if "diff --git" in result.stdout:
        print("\n✅ SUCCESS: Raw diff output detected!")
    elif "@@" in result.stdout and "+" in result.stdout and "-" in result.stdout:
        print("\n✅ SUCCESS: Diff-like output detected!")
    else:
        print("\n❌ ISSUE: No raw diff output detected - may be interpreted/summarized")
        
except Exception as e:
    print(f"Error: {e}")

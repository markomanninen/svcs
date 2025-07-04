#!/usr/bin/env python3
"""
Test commit summary with a commit that has semantic events.
"""

import subprocess
import sys
import os

# Check if GOOGLE_API_KEY is set
if not os.getenv("GOOGLE_API_KEY"):
    print("Error: GOOGLE_API_KEY not set. Please run: export GOOGLE_API_KEY='your_key_here'")
    sys.exit(1)

# Test with a commit that has semantic events
test_input = """Summarize commit 3f7274c with all details including semantic events
exit
"""

print("Testing commit summary with semantic events...")
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
    
    # Check for semantic events in the output
    if "node_added" in result.stdout or "node_logic_changed" in result.stdout:
        print("\n✅ SUCCESS: Semantic events included in commit summary!")
    else:
        print("\n⚠️  No semantic events detected in summary")
        
except Exception as e:
    print(f"Error: {e}")

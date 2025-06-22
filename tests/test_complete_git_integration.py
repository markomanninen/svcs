#!/usr/bin/env python3
"""
Comprehensive test of all git integration features in the discuss module.
"""

import subprocess
import sys
import os

# Check if GOOGLE_API_KEY is set
if not os.getenv("GOOGLE_API_KEY"):
    print("Error: GOOGLE_API_KEY not set. Please run: export GOOGLE_API_KEY='your_key_here'")
    sys.exit(1)

# Test all the new git integration features
test_input = """What files were changed in commit 6104d18?
Show me the git diff for commit 6104d18 for just the file .svcs/llm_logger.py
Summarize commit 6104d18 with all details including semantic events
exit
"""

print("Testing all git integration features in discuss module...")
print("=" * 60)

try:
    result = subprocess.run(
        [sys.executable, "svcs_discuss.py"],
        input=test_input,
        text=True,
        capture_output=True,
        cwd="/Users/markomanninen/Documents/GitHub/svcs"
    )
    
    print("OUTPUT:")
    print(result.stdout)
    
    if result.stderr:
        print("\nERRORS:")
        print(result.stderr)
    
    # Check for key indicators of successful git integration
    success_indicators = []
    
    if ".svcs/llm_logger.py" in result.stdout:
        success_indicators.append("✅ Changed files detection working")
    
    if "diff --git" in result.stdout or "+import sys" in result.stdout:
        success_indicators.append("✅ File-specific diff working")
    
    if "commit 6104d18" in result.stdout:
        success_indicators.append("✅ Commit summary working")
    
    print("\n" + "="*60)
    print("RESULTS:")
    for indicator in success_indicators:
        print(indicator)
    
    if len(success_indicators) == 3:
        print("\n🎉 ALL GIT INTEGRATION FEATURES WORKING!")
    else:
        print(f"\n⚠️  {len(success_indicators)}/3 features working")
        
except Exception as e:
    print(f"Error: {e}")

#!/usr/bin/env python3
"""
Test script for the discuss module's new git integration features.
This script will automatically test queries about changed files and diffs.
"""

import subprocess
import sys
import os

def test_discuss_git_integration():
    """Test the discuss module with git integration queries."""
    
    # Test queries for the new git integration features
    test_queries = [
        # First, get some commit hashes to work with
        "Get recent activity and show me a commit hash",
        
        # Test the new git integration functions with specific instructions
        "What files were changed in the most recent commit?",
        "Show me the actual raw git diff for the latest commit - I want to see the exact code changes",
        "Show me the diff for svcs_discuss.py in the latest commit - display the raw diff output",
        
        # Exit
        "exit"
    ]
    
    print("Testing SVCS Discuss Module - Git Integration Features")
    print("=" * 60)
    
    # Create input for the subprocess
    input_text = "\n".join(test_queries)
    
    try:
        # Run the discuss module with our test queries
        result = subprocess.run(
            [sys.executable, "svcs_discuss.py"],
            input=input_text,
            text=True,
            capture_output=True,
            cwd="/Users/markomanninen/Documents/GitHub/svcs"
        )
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        print(f"\nReturn code: {result.returncode}")
        
    except Exception as e:
        print(f"Error running test: {e}")

if __name__ == "__main__":
    # Set the required environment variable if not set
    if not os.getenv("GOOGLE_API_KEY"):
        print("Warning: GOOGLE_API_KEY not set. The discuss module requires this.")
        print("Please run: export GOOGLE_API_KEY='your_key_here'")
        sys.exit(1)
    
    test_discuss_git_integration()

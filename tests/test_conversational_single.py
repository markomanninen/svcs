#!/usr/bin/env python3
"""
Simple test to verify the conversational interface works with a single query.
"""
import sys
import subprocess

def test_single_query():
    """Test a single query through the conversational interface."""
    query = "Show me performance optimizations from the last 7 days\nexit\n"
    
    try:
        # Run the conversational interface with our test query
        process = subprocess.Popen(
            ["./.svcs/venv/bin/python", "svcs_discuss.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="/Users/markomanninen/Documents/GitHub/svcs"
        )
        
        stdout, stderr = process.communicate(input=query, timeout=30)
        
        print("STDOUT:")
        print(stdout)
        print("\nSTDERR:")
        print(stderr)
        print(f"\nReturn code: {process.returncode}")
        
    except subprocess.TimeoutExpired:
        print("❌ Test timed out - this might indicate the interface is working but waiting for more input")
        process.kill()
    except Exception as e:
        print(f"❌ Error running test: {e}")

if __name__ == "__main__":
    test_single_query()

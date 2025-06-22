#!/usr/bin/env python3
"""
Test script to verify the new git integration functions work correctly.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the SVCS project's .svcs directory to path for imports
svcs_root = Path(__file__).parent.parent  # Go up from tests/ to svcs/
sys.path.insert(0, str(svcs_root / '.svcs'))

def test_git_integration():
    """Test the new git integration functions."""
    print("🔍 Testing SVCS Git Integration Functions")
    print("=" * 50)
    
    # Change to SVCS project directory
    print(f"📂 Current directory: {os.getcwd()}")
    print(f"📂 SVCS root: {svcs_root}")
    os.chdir(svcs_root)
    print(f"📂 Changed to: {os.getcwd()}")
    
    # Check if .svcs directory exists
    svcs_dir = Path('.svcs')
    print(f"📂 Checking for: {svcs_dir.absolute()}")
    if not svcs_dir.exists():
        print("❌ .svcs directory not found. Please run 'python3 svcs.py' first to initialize the project.")
        return
    
    try:
        # Import from the project's .svcs directory
        sys.path.insert(0, '.svcs')
        from api import get_commit_changed_files, get_commit_diff, get_commit_summary
        print("✅ Successfully imported new API functions")
    except ImportError as e:
        print(f"❌ Failed to import API functions: {e}")
        print(f"   Make sure the SVCS project has been initialized with semantic events.")
        return
    
    # Get latest commit hash
    try:
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                              capture_output=True, text=True, check=True)
        latest_commit = result.stdout.strip()
        print(f"📝 Testing with latest commit: {latest_commit[:8]}")
    except subprocess.CalledProcessError:
        print("❌ Failed to get latest commit hash")
        return
    
    # Test get_commit_changed_files
    print("\n1. Testing get_commit_changed_files():")
    try:
        changed_files = get_commit_changed_files(latest_commit)
        print(f"   ✅ Found {len(changed_files)} changed files:")
        for i, file_path in enumerate(changed_files[:5], 1):  # Show first 5
            print(f"   {i}. {file_path}")
        if len(changed_files) > 5:
            print(f"   ... and {len(changed_files) - 5} more files")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test get_commit_diff (first 500 chars)
    print("\n2. Testing get_commit_diff():")
    try:
        diff_output = get_commit_diff(latest_commit)
        print(f"   ✅ Retrieved diff ({len(diff_output)} characters)")
        print("   📄 First 500 characters:")
        print("   " + "─" * 60)
        print("   " + diff_output[:500].replace('\n', '\n   '))
        if len(diff_output) > 500:
            print("   ...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test get_commit_summary
    print("\n3. Testing get_commit_summary():")
    try:
        summary = get_commit_summary(latest_commit)
        print(f"   ✅ Retrieved commit summary:")
        commit_info = summary['commit_info']
        print(f"   📋 Commit: {commit_info['commit_hash'][:8]}")
        print(f"   👤 Author: {commit_info['author']}")
        print(f"   📅 Date: {commit_info['date']}")
        print(f"   💬 Message: {commit_info['message']}")
        print(f"   📁 Files changed: {summary['file_count']}")
        print(f"   🧠 Semantic events: {summary['semantic_event_count']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test with file filter
    if 'changed_files' in locals() and changed_files:
        print(f"\n4. Testing get_commit_diff() with file filter:")
        test_file = changed_files[0]
        try:
            filtered_diff = get_commit_diff(latest_commit, test_file)
            print(f"   ✅ Retrieved filtered diff for {test_file} ({len(filtered_diff)} characters)")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n🎉 Git integration testing completed!")

if __name__ == "__main__":
    test_git_integration()

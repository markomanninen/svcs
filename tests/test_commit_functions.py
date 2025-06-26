#!/usr/bin/env python3
"""
Test commit-specific API functions with actual commit hashes
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from svcs_repo_discuss import (
    get_commit_details,
    get_commit_changed_files,
    get_commit_diff,
    get_commit_summary
)

def test_commit_functions():
    # Get the latest commit hash
    recent_commit = "b8fe974"  # Latest commit
    
    print(f"🧪 Testing commit-specific functions with commit: {recent_commit}")
    print("=" * 60)
    
    # Test get_commit_details
    try:
        print("\n📋 Testing get_commit_details...")
        details = get_commit_details(recent_commit)
        print(f"   ✅ Returned: {details}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test get_commit_changed_files
    try:
        print("\n📁 Testing get_commit_changed_files...")
        files = get_commit_changed_files(recent_commit)
        print(f"   ✅ Returned list with {len(files)} files")
        if files:
            print(f"   📄 Sample files: {files[:3]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test get_commit_diff
    try:
        print("\n🔄 Testing get_commit_diff...")
        diff = get_commit_diff(recent_commit)
        print(f"   ✅ Returned diff (length: {len(diff)} chars)")
        if len(diff) > 100:
            print(f"   📄 Sample: {diff[:100]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test get_commit_summary
    try:
        print("\n📊 Testing get_commit_summary...")
        summary = get_commit_summary(recent_commit)
        print(f"   ✅ Returned dict with keys: {list(summary.keys())}")
        if 'commit_metadata' in summary:
            print(f"   📄 Commit metadata: {summary['commit_metadata']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Commit function testing complete!")

if __name__ == "__main__":
    test_commit_functions()

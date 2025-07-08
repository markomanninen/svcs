#!/usr/bin/env python3
"""
Companion test to verify semantic notes from GitHub collaboration test
Validates that semantic notes are properly stored and accessible on GitHub remote
"""

import subprocess
import tempfile
from pathlib import Path
import sys

def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    print(f"📂 {cwd or 'current'}: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if result.stdout.strip():
            print(f"  ✅ {result.stdout.strip()}")
        if result.stderr.strip():
            print(f"  ⚠️  {result.stderr.strip()}")
        return result
    except Exception as e:
        print(f"  ❌ Command failed: {e}")
        return None

def test_remote_notes_access():
    """Test that we can clone a repo and access semantic notes from remote."""
    
    # Try to get repo URL from environment or use a default test repo
    import os
    repo_url = os.getenv('SVCS_TEST_REPO_URL')
    
    if not repo_url:
        # Default to a known test repo - you can change this
        repo_url = "https://github.com/markomanninen/svcs-test-1236.git"
        print(f"💡 Using default test repository: {repo_url}")
        print("💡 To test a different repo, set SVCS_TEST_REPO_URL environment variable")
    else:
        print(f"🎯 Using repository from environment: {repo_url}")
    
    print(f"\n🔍 Testing semantic notes access from: {repo_url}")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        test_repo = temp_path / "test_clone"
        
        print(f"\n📂 Cloning repository to: {test_repo}")
        
        # Clone the repository
        result = run_command(['git', 'clone', repo_url, str(test_repo)])
        if not result or result.returncode != 0:
            print("❌ Failed to clone repository")
            print("💡 Make sure the repository exists and is accessible")
            return False
        
        print("\n🔍 Checking what's on the remote...")
        
        # List all remote refs including notes
        print("\n📡 All remote refs:")
        result = run_command(['git', 'ls-remote', 'origin'], cwd=test_repo)
        
        print("\n📋 Specifically notes refs:")
        result = run_command(['git', 'ls-remote', 'origin', 'refs/notes/*'], cwd=test_repo)
        
        if not result or result.returncode != 0 or not result.stdout.strip():
            print("❌ No notes refs found on remote")
            print("💡 This repository may not have semantic notes yet")
            print("💡 Try running the GitHub collaboration test first:")
            print("   python tests/test_github_collaboration.py")
            return False
        
        # Fetch notes explicitly
        print("\n📥 Fetching notes from remote...")
        result = run_command(['git', 'fetch', 'origin', '+refs/notes/*:refs/notes/*'], cwd=test_repo)
        
        if result and result.returncode == 0:
            print("✅ Notes fetched successfully")
        else:
            print("❌ Failed to fetch notes")
            return False
        
        # List local notes after fetch
        print("\n💾 Local notes after fetch:")
        result = run_command(['git', 'notes', '--ref=svcs-semantic', 'list'], cwd=test_repo)
        
        if not result or result.returncode != 0 or not result.stdout.strip():
            print("❌ No local notes found after fetch")
            return False
        
        notes = result.stdout.strip().split('\n')
        print(f"✅ Found {len(notes)} semantic notes")
        
        # Show content of first note to verify it contains semantic data
        if notes:
            first_commit = notes[0].split()[1] if len(notes[0].split()) > 1 else notes[0]
            print(f"\n📄 Content of note for commit {first_commit[:8]}:")
            result = run_command(['git', 'notes', '--ref=svcs-semantic', 'show', first_commit], cwd=test_repo)
            
            if result and result.returncode == 0 and result.stdout.strip():
                content = result.stdout.strip()
                if 'semantic_events' in content or 'event_type' in content:
                    print("✅ Note contains semantic event data!")
                    # Show first few lines
                    lines = content.split('\n')[:10]
                    for line in lines:
                        print(f"  📋 {line}")
                    if len(content.split('\n')) > 10:
                        print("  ... (truncated)")
                    return True
                else:
                    print("❌ Note content doesn't look like semantic data")
                    print(f"  Content: {content[:200]}...")
            else:
                print("❌ Could not read note content")
        
        return False

if __name__ == "__main__":
    print("🚀 SVCS GitHub Notes Verification Test")
    print("=" * 50)
    print("💡 Companion test to validate semantic notes from GitHub collaboration test")
    print("💡 Use this to verify that semantic notes are accessible after running the main test")
    print()
    
    success = test_remote_notes_access()
    
    if success:
        print("\n🎉 ✅ VERIFICATION PASSED!")
        print("✅ Semantic notes are properly stored and accessible on GitHub")
        print("✅ The GitHub web UI limitation doesn't affect functionality")
        print("\n💡 Note: GitHub's web interface can't display git notes content,")
        print("   but the notes are there and accessible via git commands.")
        print("   This is normal behavior - the semantic collaboration works perfectly!")
    else:
        print("\n❌ VERIFICATION FAILED!")
        print("❌ Semantic notes are not properly synchronized")
        print("💡 Try running the main GitHub collaboration test first:")
        print("   python tests/test_github_collaboration.py")
    
    sys.exit(0 if success else 1)

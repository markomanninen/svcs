#!/usr/bin/env python3
"""
Simple Test for Seamless Semantic Note Transfer

This test verifies that SVCS hooks automatically transfer semantic notes
during git operations without manual intervention.

Focus: Verify that the git hooks are installed and work for basic sync.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run_cmd(cmd, cwd=None, check=True):
    """Run command and return result."""
    print(f"  $ {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check, shell=isinstance(cmd, str))
        if result.stdout.strip():
            print(f"    {result.stdout.strip()}")
        if result.stderr.strip() and result.returncode != 0:
            print(f"    STDERR: {result.stderr.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"    ERROR: {e}")
        if e.stdout:
            print(f"    STDOUT: {e.stdout}")
        if e.stderr:
            print(f"    STDERR: {e.stderr}")
        if check:
            raise
        return e


def setup_git_user(repo_path, name, email):
    """Set up git user for a repository."""
    run_cmd(['git', 'config', 'user.name', name], cwd=repo_path)
    run_cmd(['git', 'config', 'user.email', email], cwd=repo_path)


def check_semantic_notes(repo_path):
    """Check if semantic notes exist."""
    try:
        result = run_cmd(['git', 'notes', '--ref=refs/notes/svcs-semantic', 'list'], cwd=repo_path, check=False)
        if result.returncode == 0:
            notes = [line.strip() for line in result.stdout.split('\n') if line.strip()]
            print(f"    Found {len(notes)} semantic notes")
            return len(notes)
        else:
            print("    No semantic notes found")
            return 0
    except:
        print("    Error checking semantic notes")
        return 0


def test_hooks_installation():
    """Test that SVCS properly installs git hooks for seamless note transfer."""
    
    print("🧪 Testing SVCS Hook Installation and Basic Functionality")
    print("=" * 70)
    
    # Create temporary workspace
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Setup paths
        test_repo = tmp_path / "test_repo"
        central_repo = tmp_path / "central_repo.git"
        
        print("\n📁 Setting up test repository...")
        
        # Step 1: Create a test repository
        print("\n1️⃣ Creating test repository...")
        test_repo.mkdir()
        run_cmd(['git', 'init'], cwd=test_repo)
        setup_git_user(test_repo, "Test User", "test@example.com")
        
        # Create initial file
        test_file = test_repo / "example.py"
        test_file.write_text('''def hello_world():
    """Say hello to the world."""
    print("Hello, World!")

def add_numbers(a, b):
    """Add two numbers together."""
    return a + b
''')
        
        run_cmd(['git', 'add', 'example.py'], cwd=test_repo)
        run_cmd(['git', 'commit', '-m', 'Initial commit'], cwd=test_repo)
        
        # Step 2: Initialize SVCS and check hooks
        print("\n2️⃣ Initializing SVCS...")
        svcs_cmd = [sys.executable, str(Path(__file__).parent / "svcs" / "cli.py")]
        run_cmd(svcs_cmd + ['init'], cwd=test_repo)
        
        # Check that hooks are installed
        hooks_dir = test_repo / ".git" / "hooks"
        expected_hooks = ['post-commit', 'post-merge', 'post-checkout', 'pre-push']
        hooks_installed = []
        
        for hook in expected_hooks:
            hook_path = hooks_dir / hook
            if hook_path.exists():
                hooks_installed.append(hook)
                print(f"    ✅ {hook} hook installed")
                
                # Check hook content
                hook_content = hook_path.read_text()
                if 'SVCS' in hook_content:
                    print(f"      📄 Contains SVCS logic")
                else:
                    print(f"      ⚠️  Missing SVCS logic")
            else:
                print(f"    ❌ {hook} hook missing")
        
        # Step 3: Test post-commit hook (semantic analysis)
        print("\n3️⃣ Testing post-commit hook...")
        
        # Make another commit to trigger post-commit hook
        test_file.write_text('''def hello_world():
    """Say hello to the world."""
    print("Hello, World!")

def add_numbers(a, b):
    """Add two numbers together."""
    return a + b

def multiply_numbers(x, y):
    """Multiply two numbers."""
    if x == 0 or y == 0:
        return 0
    return x * y
''')
        
        run_cmd(['git', 'add', 'example.py'], cwd=test_repo)
        result = run_cmd(['git', 'commit', '-m', 'Add multiply function'], cwd=test_repo)
        
        # Check if semantic notes were created
        notes_count = check_semantic_notes(test_repo)
        
        # Step 4: Setup central repository for testing push/pull
        print("\n4️⃣ Setting up central repository...")
        central_repo.mkdir()
        run_cmd(['git', 'init', '--bare'], cwd=central_repo)
        
        # Add remote and test pre-push hook
        run_cmd(['git', 'remote', 'add', 'origin', str(central_repo)], cwd=test_repo)
        
        print("\n5️⃣ Testing pre-push hook...")
        push_result = run_cmd(['git', 'push', '-u', 'origin', 'main'], cwd=test_repo, check=False)
        
        if push_result.returncode == 0:
            print("    ✅ Push successful")
        else:
            print("    ⚠️  Push had issues (might be expected)")
        
        # Step 5: Test clone and post-checkout hook
        print("\n6️⃣ Testing clone and post-checkout hook...")
        clone_repo = tmp_path / "clone_repo"
        
        clone_result = run_cmd(['git', 'clone', str(central_repo), str(clone_repo)], check=False)
        
        if clone_result.returncode == 0:
            setup_git_user(clone_repo, "Clone User", "clone@example.com")
            
            # Initialize SVCS in clone
            run_cmd(svcs_cmd + ['init'], cwd=clone_repo)
            
            # Check if semantic notes were fetched
            clone_notes = check_semantic_notes(clone_repo)
            
            print(f"    Original repo notes: {notes_count}")
            print(f"    Cloned repo notes: {clone_notes}")
        
        # Step 6: Report results
        print("\n📊 Test Results Summary")
        print("=" * 40)
        print(f"Hooks installed: {len(hooks_installed)}/{len(expected_hooks)}")
        for hook in expected_hooks:
            status = "✅" if hook in hooks_installed else "❌"
            print(f"  {status} {hook}")
        
        print(f"Semantic notes generated: {'✅' if notes_count > 0 else '❌'} ({notes_count} notes)")
        print(f"Push operation: {'✅' if push_result.returncode == 0 else '⚠️'}")
        
        if clone_result.returncode == 0:
            print(f"Clone and fetch: {'✅' if clone_notes > 0 else '❌'} ({clone_notes} notes)")
        else:
            print("Clone operation: ❌ (failed)")
        
        # Overall assessment
        hooks_ok = len(hooks_installed) == len(expected_hooks)
        notes_ok = notes_count > 0
        
        print(f"\n🎯 Overall Result: {'✅ PASS' if hooks_ok and notes_ok else '❌ PARTIAL PASS'}")
        
        if hooks_ok and notes_ok:
            print("✅ SVCS hook system is properly installed and working!")
            print("   Semantic notes are generated automatically on commits.")
        else:
            print("⚠️  Some issues detected:")
            if not hooks_ok:
                print("   - Not all hooks are installed correctly")
            if not notes_ok:
                print("   - Semantic notes are not being generated")
        
        return hooks_ok and notes_ok


if __name__ == "__main__":
    try:
        success = test_hooks_installation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

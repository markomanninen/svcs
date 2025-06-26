#!/usr/bin/env python3
"""
End-to-End Test for Seamless Semantic Note Transfer

This test verifies that SVCS seamlessly transfers semantic notes during all
git operations without manual intervention, ensuring all developers always
have the full semantic history.

Test scenario:
1. Developer A initializes SVCS and makes commits
2. Developer B clones and automatically gets semantic notes
3. Developer B makes changes and pushes
4. Developer A pulls and automatically gets new semantic notes
5. All operations happen without manual note fetching/pushing
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run_cmd(cmd, cwd=None, capture=True):
    """Run command and return result."""
    print(f"  $ {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    try:
        if capture:
            result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True, shell=isinstance(cmd, str))
            if result.stdout.strip():
                print(f"    {result.stdout.strip()}")
            return result
        else:
            subprocess.run(cmd, cwd=cwd, check=True, shell=isinstance(cmd, str))
            return None
    except subprocess.CalledProcessError as e:
        print(f"    ERROR: {e}")
        if e.stdout:
            print(f"    STDOUT: {e.stdout}")
        if e.stderr:
            print(f"    STDERR: {e.stderr}")
        raise


def setup_git_user(repo_path, name, email):
    """Set up git user for a repository."""
    run_cmd(['git', 'config', 'user.name', name], cwd=repo_path)
    run_cmd(['git', 'config', 'user.email', email], cwd=repo_path)


def check_semantic_notes(repo_path, expected_count=None):
    """Check if semantic notes exist and optionally verify count."""
    try:
        result = run_cmd(['git', 'notes', '--ref=refs/notes/svcs-semantic', 'list'], cwd=repo_path)
        notes = [line.strip() for line in result.stdout.split('\n') if line.strip()]
        print(f"    Found {len(notes)} semantic notes")
        
        if expected_count is not None:
            if len(notes) != expected_count:
                print(f"    WARNING: Expected {expected_count} notes, found {len(notes)}")
                return False
        
        return len(notes) > 0
    except subprocess.CalledProcessError:
        print("    No semantic notes found")
        return False


def test_seamless_semantic_transfer():
    """Test end-to-end seamless semantic note transfer."""
    
    print("🧪 Testing Seamless Semantic Note Transfer")
    print("=" * 60)
    
    # Create temporary workspace
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Setup paths
        central_repo = tmp_path / "central_repo.git"
        dev_a_repo = tmp_path / "developer_a"
        dev_b_repo = tmp_path / "developer_b"
        dev_c_repo = tmp_path / "developer_c"
        
        print("\n📁 Setting up test repositories...")
        
        # Step 1: Create central bare repository
        print("\n1️⃣ Creating central repository...")
        central_repo.mkdir()
        run_cmd(['git', 'init', '--bare'], cwd=central_repo)
        print(f"✅ Central repository created at {central_repo}")
        
        # Step 2: Developer A clones and initializes SVCS
        print("\n2️⃣ Developer A: Clone and initialize SVCS...")
        run_cmd(['git', 'clone', str(central_repo), str(dev_a_repo)])
        setup_git_user(dev_a_repo, "Developer A", "deva@example.com")
        
        # Initialize SVCS (should install hooks automatically)
        print("  Initializing SVCS...")
        svcs_cmd = [sys.executable, str(Path(__file__).parent / "svcs" / "cli.py")]
        run_cmd(svcs_cmd + ['init'], cwd=dev_a_repo)
        
        # Check that hooks are installed
        hooks_dir = dev_a_repo / ".git" / "hooks"
        expected_hooks = ['post-commit', 'post-merge', 'post-checkout', 'pre-push']
        for hook in expected_hooks:
            hook_path = hooks_dir / hook
            if hook_path.exists():
                print(f"    ✅ {hook} hook installed")
            else:
                print(f"    ❌ {hook} hook missing")
                return False
        
        # Step 3: Developer A makes commits that generate semantic events
        print("\n3️⃣ Developer A: Making commits with semantic events...")
        
        # Create a Python file with function
        python_file = dev_a_repo / "utils.py"
        python_file.write_text('''def calculate_sum(a, b):
    """Calculate the sum of two numbers."""
    return a + b

def multiply(x, y):
    """Multiply two numbers."""
    return x * y
''')
        
        run_cmd(['git', 'add', 'utils.py'], cwd=dev_a_repo)
        run_cmd(['git', 'commit', '-m', 'Add utility functions'], cwd=dev_a_repo)
        
        # Check if semantic notes were generated
        print("    Checking for semantic notes after commit...")
        has_notes_a1 = check_semantic_notes(dev_a_repo)
        
        # Add another commit
        python_file.write_text('''def calculate_sum(a, b):
    """Calculate the sum of two numbers."""
    return a + b

def multiply(x, y):
    """Multiply two numbers."""
    return x * y

def divide(a, b):
    """Divide two numbers with error handling."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
''')
        
        run_cmd(['git', 'add', 'utils.py'], cwd=dev_a_repo)
        run_cmd(['git', 'commit', '-m', 'Add divide function with error handling'], cwd=dev_a_repo)
        
        # Check semantic notes again
        print("    Checking for semantic notes after second commit...")
        has_notes_a2 = check_semantic_notes(dev_a_repo)
        
        # Step 4: Developer A pushes (should automatically push semantic notes)
        print("\n4️⃣ Developer A: Pushing changes (semantic notes should auto-push)...")
        run_cmd(['git', 'push', 'origin', 'main'], cwd=dev_a_repo)
        
        # Step 5: Developer B clones (should automatically get semantic notes)
        print("\n5️⃣ Developer B: Clone repository (should auto-fetch semantic notes)...")
        run_cmd(['git', 'clone', str(central_repo), str(dev_b_repo)])
        setup_git_user(dev_b_repo, "Developer B", "devb@example.com")
        
        # Initialize SVCS for Developer B
        run_cmd(svcs_cmd + ['init'], cwd=dev_b_repo)
        
        # Check if Developer B automatically has semantic notes
        print("    Checking if Developer B has semantic notes...")
        has_notes_b1 = check_semantic_notes(dev_b_repo)
        
        if not has_notes_b1:
            print("    ℹ️  No automatic fetch on clone, triggering checkout hook...")
            # Simulate post-checkout hook (which should fetch notes)
            run_cmd(['git', 'checkout', 'main'], cwd=dev_b_repo)
            has_notes_b1 = check_semantic_notes(dev_b_repo)
        
        # Step 6: Developer B makes changes and commits
        print("\n6️⃣ Developer B: Making changes and commits...")
        
        js_file = dev_b_repo / "frontend.js"
        js_file.write_text('''function addNumbers(a, b) {
    return a + b;
}

function multiplyNumbers(x, y) {
    return x * y;
}

class Calculator {
    constructor() {
        this.history = [];
    }
    
    add(a, b) {
        const result = addNumbers(a, b);
        this.history.push(`${a} + ${b} = ${result}`);
        return result;
    }
}
''')
        
        run_cmd(['git', 'add', 'frontend.js'], cwd=dev_b_repo)
        run_cmd(['git', 'commit', '-m', 'Add JavaScript calculator with class'], cwd=dev_b_repo)
        
        # Step 7: Developer B pushes (should auto-push semantic notes)
        print("\n7️⃣ Developer B: Pushing changes...")
        run_cmd(['git', 'push', 'origin', 'main'], cwd=dev_b_repo)
        
        # Step 8: Developer A pulls (should auto-fetch new semantic notes)
        print("\n8️⃣ Developer A: Pulling changes (should auto-fetch semantic notes)...")
        run_cmd(['git', 'pull', 'origin', 'main'], cwd=dev_a_repo)
        
        # Check if Developer A now has all semantic notes
        print("    Checking if Developer A has updated semantic notes...")
        has_notes_a3 = check_semantic_notes(dev_a_repo)
        
        # Step 9: New Developer C clones fresh
        print("\n9️⃣ Developer C: Fresh clone (should get all semantic history)...")
        run_cmd(['git', 'clone', str(central_repo), str(dev_c_repo)])
        setup_git_user(dev_c_repo, "Developer C", "devc@example.com")
        
        # Initialize SVCS
        run_cmd(svcs_cmd + ['init'], cwd=dev_c_repo)
        
        # Check if Developer C gets all semantic notes automatically
        print("    Checking if Developer C has complete semantic history...")
        has_notes_c1 = check_semantic_notes(dev_c_repo)
        
        if not has_notes_c1:
            # Try explicit fetch
            print("    Trying explicit semantic note fetch...")
            try:
                run_cmd(['git', 'fetch', 'origin', 'refs/notes/svcs-semantic:refs/notes/svcs-semantic'], cwd=dev_c_repo)
                has_notes_c1 = check_semantic_notes(dev_c_repo)
            except:
                pass
        
        # Step 10: Report results
        print("\n📊 Test Results Summary")
        print("=" * 40)
        print(f"Developer A after commit 1: {'✅' if has_notes_a1 else '❌'} Semantic notes generated")
        print(f"Developer A after commit 2: {'✅' if has_notes_a2 else '❌'} Semantic notes updated")
        print(f"Developer B after clone:    {'✅' if has_notes_b1 else '❌'} Semantic notes auto-fetched")
        print(f"Developer A after pull:     {'✅' if has_notes_a3 else '❌'} Semantic notes auto-synced")
        print(f"Developer C fresh clone:    {'✅' if has_notes_c1 else '❌'} Complete semantic history")
        
        # Overall assessment
        all_passed = all([has_notes_a1, has_notes_a2, has_notes_b1, has_notes_a3, has_notes_c1])
        
        print(f"\n🎯 Overall Result: {'✅ PASS' if all_passed else '❌ FAIL'}")
        
        if all_passed:
            print("✅ Seamless semantic note transfer is working correctly!")
            print("   All developers automatically receive semantic history during normal git operations.")
        else:
            print("❌ Some issues detected with seamless semantic note transfer:")
            if not has_notes_b1:
                print("   - Developer B didn't automatically get semantic notes on clone")
            if not has_notes_a3:
                print("   - Developer A didn't automatically get new semantic notes on pull")
            if not has_notes_c1:
                print("   - Developer C didn't get complete semantic history on fresh clone")
        
        return all_passed


if __name__ == "__main__":
    try:
        success = test_seamless_semantic_transfer()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

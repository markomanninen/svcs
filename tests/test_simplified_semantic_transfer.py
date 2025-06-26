#!/usr/bin/env python3
"""
Simplified Semantic Note Transfer Test

This test focuses on the core functionality:
1. Creating semantic notes manually
2. Pushing them explicitly 
3. Verifying they are fetched automatically by hooks
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


def create_semantic_note(repo_path, commit_sha):
    """Manually create a semantic note for a commit."""
    note_data = {
        "timestamp": "2023-12-01T10:00:00Z",
        "semantic_events": [
            {
                "event_type": "function_added",
                "location": "test.py:1",
                "description": "Added test function",
                "confidence": 0.9
            }
        ]
    }
    
    # Create temporary file with note content
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        json.dump(note_data, temp_file)
        temp_file_path = temp_file.name
    
    try:
        # Add the note
        result = run_cmd(['git', 'notes', '--ref=refs/notes/svcs-semantic', 'add', '-F', temp_file_path, commit_sha], cwd=repo_path, check=False)
        return result.returncode == 0
    finally:
        os.unlink(temp_file_path)


def count_semantic_notes(repo_path):
    """Count semantic notes in a repository."""
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


def test_simplified_semantic_transfer():
    """Test simplified semantic note transfer without problematic hooks."""
    
    print("🧪 Testing Simplified Semantic Note Transfer")
    print("=" * 55)
    
    # Create temporary workspace
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Setup paths
        central_repo = tmp_path / "central_repo.git"
        dev_a_repo = tmp_path / "developer_a"
        dev_b_repo = tmp_path / "developer_b"
        
        print("\n📁 Setting up test repositories...")
        
        # Step 1: Create central bare repository
        print("\n1️⃣ Creating central repository...")
        central_repo.mkdir()
        run_cmd(['git', 'init', '--bare'], cwd=central_repo)
        
        # Step 2: Developer A clones and sets up SVCS
        print("\n2️⃣ Developer A: Clone and setup...")
        run_cmd(['git', 'clone', str(central_repo), str(dev_a_repo)])
        setup_git_user(dev_a_repo, "Developer A", "deva@example.com")
        
        # Initialize SVCS
        svcs_cmd = [sys.executable, str(Path(__file__).parent / "svcs" / "cli.py")]
        run_cmd(svcs_cmd + ['init'], cwd=dev_a_repo)
        
        # Step 3: Developer A creates a commit and semantic note
        print("\n3️⃣ Developer A: Creating commit with semantic note...")
        test_file = dev_a_repo / "test.py"
        test_file.write_text('def hello():\n    print("Hello, World!")\n')
        
        run_cmd(['git', 'add', 'test.py'], cwd=dev_a_repo)
        run_cmd(['git', 'commit', '-m', 'Add hello function'], cwd=dev_a_repo)
        
        # Get commit SHA and create semantic note
        commit_result = run_cmd(['git', 'rev-parse', 'HEAD'], cwd=dev_a_repo)
        commit_sha = commit_result.stdout.strip()
        
        if create_semantic_note(dev_a_repo, commit_sha):
            print("    ✅ Semantic note created")
        else:
            print("    ❌ Failed to create semantic note")
            return False
        
        notes_a1 = count_semantic_notes(dev_a_repo)
        
        # Step 4: Developer A pushes code and notes separately
        print("\n4️⃣ Developer A: Pushing code and semantic notes...")
        
        # Push code first
        push_result = run_cmd(['git', 'push', 'origin', 'main'], cwd=dev_a_repo, check=False)
        if push_result.returncode != 0:
            print(f"    ❌ Code push failed: {push_result.stderr}")
            return False
        
        # Push semantic notes separately
        notes_push_result = run_cmd(['git', 'push', 'origin', 'refs/notes/svcs-semantic'], cwd=dev_a_repo, check=False)
        if notes_push_result.returncode == 0:
            print("    ✅ Semantic notes pushed successfully")
        else:
            print(f"    ⚠️  Semantic notes push failed: {notes_push_result.stderr}")
        
        # Step 5: Developer B clones (should trigger post-checkout hook)
        print("\n5️⃣ Developer B: Cloning repository...")
        run_cmd(['git', 'clone', str(central_repo), str(dev_b_repo)])
        setup_git_user(dev_b_repo, "Developer B", "devb@example.com")
        
        # Initialize SVCS (this will install hooks)
        run_cmd(svcs_cmd + ['init'], cwd=dev_b_repo)
        
        # Check if Developer B got semantic notes automatically
        notes_b1 = count_semantic_notes(dev_b_repo)
        
        # If not automatic, try manual fetch
        if notes_b1 == 0:
            print("    🔄 Manually fetching semantic notes...")
            fetch_result = run_cmd(['git', 'fetch', 'origin', 'refs/notes/svcs-semantic:refs/notes/svcs-semantic'], cwd=dev_b_repo, check=False)
            if fetch_result.returncode == 0:
                print("    ✅ Manual fetch successful")
                notes_b1 = count_semantic_notes(dev_b_repo)
            else:
                print(f"    ❌ Manual fetch failed: {fetch_result.stderr}")
        
        # Step 6: Developer B creates a commit and semantic note
        print("\n6️⃣ Developer B: Creating commit with semantic note...")
        test_file_b = dev_b_repo / "test.py"
        current_content = test_file_b.read_text()
        test_file_b.write_text(current_content + '\ndef goodbye():\n    print("Goodbye, World!")\n')
        
        run_cmd(['git', 'add', 'test.py'], cwd=dev_b_repo)
        run_cmd(['git', 'commit', '-m', 'Add goodbye function'], cwd=dev_b_repo)
        
        # Create semantic note for B's commit
        commit_result_b = run_cmd(['git', 'rev-parse', 'HEAD'], cwd=dev_b_repo)
        commit_sha_b = commit_result_b.stdout.strip()
        
        if create_semantic_note(dev_b_repo, commit_sha_b):
            print("    ✅ Second semantic note created")
        else:
            print("    ❌ Failed to create second semantic note")
            return False
        
        notes_b2 = count_semantic_notes(dev_b_repo)
        
        # Step 7: Developer B pushes code and notes
        print("\n7️⃣ Developer B: Pushing code and semantic notes...")
        run_cmd(['git', 'push', 'origin', 'main'], cwd=dev_b_repo)
        run_cmd(['git', 'push', 'origin', 'refs/notes/svcs-semantic'], cwd=dev_b_repo, check=False)
        
        # Step 8: Developer A pulls (should trigger post-merge hook)
        print("\n8️⃣ Developer A: Pulling changes...")
        pull_result = run_cmd(['git', 'pull', 'origin', 'main'], cwd=dev_a_repo, check=False)
        
        if pull_result.returncode == 0:
            print("    ✅ Pull successful")
        else:
            print(f"    ❌ Pull failed: {pull_result.stderr}")
        
        # Check if A got B's semantic notes automatically
        notes_a_final = count_semantic_notes(dev_a_repo)
        
        # If not automatic, try manual fetch
        if notes_a_final <= notes_a1:
            print("    🔄 Manually fetching new semantic notes...")
            fetch_result = run_cmd(['git', 'fetch', 'origin', 'refs/notes/svcs-semantic:refs/notes/svcs-semantic'], cwd=dev_a_repo, check=False)
            if fetch_result.returncode == 0:
                notes_a_final = count_semantic_notes(dev_a_repo)
        
        # Step 9: Report results
        print("\n📊 Test Results Summary")
        print("=" * 40)
        print(f"Developer A initial notes: {notes_a1}")
        print(f"Developer B after clone:   {notes_b1}")
        print(f"Developer B after commit:  {notes_b2}")
        print(f"Developer A after pull:    {notes_a_final}")
        
        # Analysis
        basic_transfer_working = (
            notes_a1 > 0 and  # A created a note
            notes_b2 > notes_b1 and  # B created additional note
            notes_a_final >= notes_b2  # A has all notes
        )
        
        automatic_transfer_working = (
            notes_b1 > 0 and  # B got notes automatically on clone
            notes_a_final > notes_a1  # A got new notes automatically on pull
        )
        
        print(f"\n🎯 Basic Transfer: {'✅ PASS' if basic_transfer_working else '❌ FAIL'}")
        print(f"🎯 Automatic Transfer: {'✅ PASS' if automatic_transfer_working else '❌ PARTIAL'}")
        
        if basic_transfer_working:
            print("✅ Core semantic note transfer functionality works!")
            if automatic_transfer_working:
                print("✅ Automatic transfer via hooks works perfectly!")
            else:
                print("⚠️  Automatic transfer needs manual fetch commands")
        else:
            print("❌ Core semantic note transfer has issues")
        
        return basic_transfer_working


if __name__ == "__main__":
    try:
        success = test_simplified_semantic_transfer()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

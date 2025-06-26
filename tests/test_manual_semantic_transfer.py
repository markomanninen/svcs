#!/usr/bin/env python3
"""
Manual Semantic Note Transfer Test

This test manually creates semantic notes and verifies that the SVCS hooks
transfer them correctly during git operations.
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


def create_semantic_note(repo_path, commit_sha, note_content):
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


def test_manual_semantic_transfer():
    """Test manual semantic note creation and transfer."""
    
    print("🧪 Testing Manual Semantic Note Transfer")
    print("=" * 50)
    
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
        
        # Step 3: Developer A creates a commit
        print("\n3️⃣ Developer A: Creating commit...")
        test_file = dev_a_repo / "test.py"
        test_file.write_text('def hello():\n    print("Hello, World!")\n')
        
        run_cmd(['git', 'add', 'test.py'], cwd=dev_a_repo)
        result = run_cmd(['git', 'commit', '-m', 'Add hello function'], cwd=dev_a_repo)
        
        # Get the commit SHA
        commit_result = run_cmd(['git', 'rev-parse', 'HEAD'], cwd=dev_a_repo)
        commit_sha = commit_result.stdout.strip()
        print(f"    Commit SHA: {commit_sha[:8]}")
        
        # Step 4: Manually create semantic note
        print("\n4️⃣ Developer A: Creating semantic note...")
        if create_semantic_note(dev_a_repo, commit_sha, "test note"):
            print("    ✅ Semantic note created successfully")
        else:
            print("    ❌ Failed to create semantic note")
            return False
        
        notes_a1 = count_semantic_notes(dev_a_repo)
        
        # Step 5: Push changes (should trigger pre-push hook)
        print("\n5️⃣ Developer A: Pushing changes...")
        push_result = run_cmd(['git', 'push', 'origin', 'main'], cwd=dev_a_repo, check=False)
        
        if push_result.returncode == 0:
            print("    ✅ Push successful")
        else:
            print(f"    ❌ Push failed: {push_result.stderr}")
            return False
        
        # Step 6: Developer B clones (should trigger post-checkout hook)
        print("\n6️⃣ Developer B: Cloning repository...")
        run_cmd(['git', 'clone', str(central_repo), str(dev_b_repo)])
        setup_git_user(dev_b_repo, "Developer B", "devb@example.com")
        
        # Initialize SVCS
        run_cmd(svcs_cmd + ['init'], cwd=dev_b_repo)
        
        # Check if Developer B has semantic notes
        notes_b1 = count_semantic_notes(dev_b_repo)
        
        # Step 7: Developer B creates another commit with semantic note
        print("\n7️⃣ Developer B: Creating commit with semantic note...")
        test_file_b = dev_b_repo / "test.py"
        current_content = test_file_b.read_text()
        test_file_b.write_text(current_content + '\ndef goodbye():\n    print("Goodbye, World!")\n')
        
        run_cmd(['git', 'add', 'test.py'], cwd=dev_b_repo)
        run_cmd(['git', 'commit', '-m', 'Add goodbye function'], cwd=dev_b_repo)
        
        # Get new commit SHA
        commit_result_b = run_cmd(['git', 'rev-parse', 'HEAD'], cwd=dev_b_repo)
        commit_sha_b = commit_result_b.stdout.strip()
        
        # Create semantic note for Developer B's commit
        if create_semantic_note(dev_b_repo, commit_sha_b, "second test note"):
            print("    ✅ Second semantic note created")
        else:
            print("    ❌ Failed to create second semantic note")
            return False
        
        notes_b2 = count_semantic_notes(dev_b_repo)
        
        # Step 8: Developer B pushes
        print("\n8️⃣ Developer B: Pushing changes...")
        push_result_b = run_cmd(['git', 'push', 'origin', 'main'], cwd=dev_b_repo, check=False)
        
        if push_result_b.returncode == 0:
            print("    ✅ Developer B push successful")
        else:
            print(f"    ❌ Developer B push failed: {push_result_b.stderr}")
        
        # Step 9: Developer A pulls (should trigger post-merge hook)
        print("\n9️⃣ Developer A: Pulling changes...")
        pull_result = run_cmd(['git', 'pull', 'origin', 'main'], cwd=dev_a_repo, check=False)
        
        if pull_result.returncode == 0:
            print("    ✅ Developer A pull successful")
        else:
            print(f"    ❌ Developer A pull failed: {pull_result.stderr}")
        
        # Check final semantic notes
        notes_a_final = count_semantic_notes(dev_a_repo)
        
        # Step 10: Report results
        print("\n📊 Test Results Summary")
        print("=" * 40)
        print(f"Developer A initial notes: {notes_a1}")
        print(f"Developer B after clone:   {notes_b1}")
        print(f"Developer B after commit:  {notes_b2}")
        print(f"Developer A after pull:    {notes_a_final}")
        
        # Analysis
        transfer_working = (
            notes_a1 > 0 and  # A created a note
            notes_b1 > 0 and  # B got the note from central
            notes_b2 > notes_b1 and  # B created additional note
            notes_a_final > notes_a1  # A got B's note
        )
        
        print(f"\n🎯 Overall Result: {'✅ PASS' if transfer_working else '❌ FAIL'}")
        
        if transfer_working:
            print("✅ Semantic note transfer is working correctly!")
        else:
            print("❌ Issues detected with semantic note transfer:")
            if notes_a1 == 0:
                print("   - Developer A couldn't create semantic notes")
            if notes_b1 == 0:
                print("   - Developer B didn't get semantic notes on clone")
            if notes_b2 <= notes_b1:
                print("   - Developer B couldn't create additional semantic notes")
            if notes_a_final <= notes_a1:
                print("   - Developer A didn't get new semantic notes on pull")
        
        return transfer_working


if __name__ == "__main__":
    try:
        success = test_manual_semantic_transfer()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

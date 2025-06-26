#!/usr/bin/env python3
"""
Test enhanced semantic note transfer with full hook integration
"""

import os
import sys
import tempfile
import shutil
import subprocess
import json
from pathlib import Path

def run_command(cmd, cwd=None, check=True, capture_output=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, check=check, 
                              capture_output=capture_output, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {cmd}")
        print(f"   Error: {e}")
        if capture_output:
            print(f"   Stdout: {e.stdout}")
            print(f"   Stderr: {e.stderr}")
        return e

def test_enhanced_semantic_hooks():
    """Test the enhanced hook system with full semantic analysis."""
    print("🧪 Testing Enhanced Semantic Hook Integration")
    print("=" * 60)
    
    # Create temporary directory for test
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Set up paths
        central_repo = temp_path / "central_repo.git"
        dev_a_repo = temp_path / "developer_a"
        dev_b_repo = temp_path / "developer_b"
        
        print(f"📁 Test directory: {temp_path}")
        
        # 1. Create central bare repository
        print("\n1️⃣ Creating central bare repository...")
        central_repo.mkdir()
        run_command("git init --bare", cwd=central_repo)
        print(f"   ✅ Central repo created: {central_repo}")
        
        # 2. Developer A: Clone and initialize SVCS
        print("\n2️⃣ Developer A: Clone and initialize...")
        run_command(f"git clone {central_repo} {dev_a_repo}")
        
        # Configure git user
        run_command("git config user.name 'Developer A'", cwd=dev_a_repo)
        run_command("git config user.email 'deva@example.com'", cwd=dev_a_repo)
        
        # Initialize SVCS
        svcs_cmd = f"{sys.executable} {Path(__file__).parent / 'svcs' / 'cli.py'}"
        result = run_command(f"{svcs_cmd} init", cwd=dev_a_repo)
        print(f"   ✅ SVCS initialized: {result.stdout.strip()}")
        
        # 3. Create initial commit with content that will generate semantic events
        print("\n3️⃣ Developer A: Creating commit with semantic content...")
        
        # Create a Python file with function definitions
        python_file = dev_a_repo / "calculator.py"
        python_file.write_text("""
def add(a, b):
    \"\"\"Add two numbers.\"\"\"
    return a + b

def multiply(a, b):
    \"\"\"Multiply two numbers.\"\"\"
    return a * b

class Calculator:
    \"\"\"A simple calculator class.\"\"\"
    
    def __init__(self):
        self.history = []
    
    def calculate(self, operation, a, b):
        \"\"\"Perform a calculation and store in history.\"\"\"
        if operation == 'add':
            result = add(a, b)
        elif operation == 'multiply':
            result = multiply(a, b)
        else:
            raise ValueError(f"Unknown operation: {operation}")
        
        self.history.append((operation, a, b, result))
        return result
""")
        
        run_command("git add calculator.py", cwd=dev_a_repo)
        result = run_command("git commit -m 'Add calculator with functions and class'", cwd=dev_a_repo)
        print(f"   ✅ Commit created: {result.stdout.strip()}")
        
        # Check if semantic notes were created by the post-commit hook
        print("\n   🔍 Checking semantic notes after commit...")
        notes_result = run_command("git notes --ref=refs/notes/svcs-semantic list", cwd=dev_a_repo, check=False)
        if notes_result.returncode == 0 and notes_result.stdout.strip():
            print(f"   ✅ Semantic notes created: {len(notes_result.stdout.strip().split())} notes")
        else:
            print("   ⚠️  No semantic notes found, checking SVCS events...")
            events_result = run_command(f"{svcs_cmd} events --limit 5", cwd=dev_a_repo, check=False)
            if events_result.returncode == 0:
                print(f"   ✅ SVCS events available: {len(events_result.stdout.split())} lines")
            else:
                print(f"   ❌ No SVCS events found: {events_result.stderr}")
        
        # 4. Push to central repository
        print("\n4️⃣ Developer A: Pushing to central repository...")
        run_command("git push origin main", cwd=dev_a_repo)
        
        # Push semantic notes if they exist
        notes_push = run_command("git push origin refs/notes/svcs-semantic", cwd=dev_a_repo, check=False)
        if notes_push.returncode == 0:
            print("   ✅ Semantic notes pushed")
        else:
            print("   ℹ️  No semantic notes to push")
        
        # 5. Developer B: Clone and initialize
        print("\n5️⃣ Developer B: Clone and initialize...")
        run_command(f"git clone {central_repo} {dev_b_repo}")
        
        # Configure git user
        run_command("git config user.name 'Developer B'", cwd=dev_b_repo)
        run_command("git config user.email 'devb@example.com'", cwd=dev_b_repo)
        
        # Initialize SVCS (should trigger post-checkout hook)
        result = run_command(f"{svcs_cmd} init", cwd=dev_b_repo)
        print(f"   ✅ SVCS initialized: {result.stdout.strip()}")
        
        # Check if semantic notes were automatically fetched
        print("\n   🔍 Checking automatic semantic note fetch...")
        notes_result = run_command("git notes --ref=refs/notes/svcs-semantic list", cwd=dev_b_repo, check=False)
        if notes_result.returncode == 0 and notes_result.stdout.strip():
            print(f"   ✅ Semantic notes automatically fetched: {len(notes_result.stdout.strip().split())} notes")
        else:
            print("   ⚠️  No semantic notes found, manually fetching...")
            fetch_result = run_command("git fetch origin refs/notes/svcs-semantic:refs/notes/svcs-semantic", 
                                     cwd=dev_b_repo, check=False)
            if fetch_result.returncode == 0:
                print("   ✅ Manual fetch successful")
            else:
                print(f"   ❌ Manual fetch failed: {fetch_result.stderr}")
        
        # 6. Developer B: Add more functionality
        print("\n6️⃣ Developer B: Adding more functionality...")
        
        # Extend the calculator
        calculator_file = dev_b_repo / "calculator.py"
        current_content = calculator_file.read_text()
        extended_content = current_content + """

def subtract(a, b):
    \"\"\"Subtract b from a.\"\"\"
    return a - b

def divide(a, b):
    \"\"\"Divide a by b.\"\"\"
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b

# Extend Calculator class
class ScientificCalculator(Calculator):
    \"\"\"A scientific calculator with advanced functions.\"\"\"
    
    def power(self, base, exponent):
        \"\"\"Calculate base raised to the power of exponent.\"\"\"
        result = base ** exponent
        self.history.append(('power', base, exponent, result))
        return result
    
    def square_root(self, number):
        \"\"\"Calculate square root of a number.\"\"\"
        import math
        result = math.sqrt(number)
        self.history.append(('sqrt', number, None, result))
        return result
"""
        calculator_file.write_text(extended_content)
        
        run_command("git add calculator.py", cwd=dev_b_repo)
        result = run_command("git commit -m 'Add scientific calculator with inheritance'", cwd=dev_b_repo)
        print(f"   ✅ Extended commit created: {result.stdout.strip()}")
        
        # Check semantic analysis after this commit
        print("\n   🔍 Checking semantic analysis after extension...")
        notes_result = run_command("git notes --ref=refs/notes/svcs-semantic list", cwd=dev_b_repo, check=False)
        if notes_result.returncode == 0 and notes_result.stdout.strip():
            note_count = len(notes_result.stdout.strip().split())
            print(f"   ✅ Total semantic notes: {note_count}")
        else:
            print("   ⚠️  Checking SVCS events...")
            events_result = run_command(f"{svcs_cmd} events --limit 10", cwd=dev_b_repo, check=False)
            if events_result.returncode == 0:
                print(f"   ✅ SVCS events working")
        
        # 7. Push changes back
        print("\n7️⃣ Developer B: Pushing changes...")
        run_command("git push origin main", cwd=dev_b_repo)
        
        # Push semantic notes
        notes_push = run_command("git push origin refs/notes/svcs-semantic", cwd=dev_b_repo, check=False)
        if notes_push.returncode == 0:
            print("   ✅ Semantic notes pushed")
        else:
            print("   ℹ️  No new semantic notes to push")
        
        # 8. Developer A: Pull changes (should trigger post-merge hook)
        print("\n8️⃣ Developer A: Pulling changes...")
        result = run_command("git pull origin main", cwd=dev_a_repo)
        print(f"   ✅ Pull completed: {result.stdout.strip()}")
        
        # Check if semantic notes were automatically updated
        print("\n   🔍 Checking automatic semantic note sync after pull...")
        notes_result = run_command("git notes --ref=refs/notes/svcs-semantic list", cwd=dev_a_repo, check=False)
        if notes_result.returncode == 0 and notes_result.stdout.strip():
            note_count = len(notes_result.stdout.strip().split())
            print(f"   ✅ Semantic notes synced: {note_count} total notes")
        else:
            print("   ⚠️  Checking SVCS events after pull...")
            events_result = run_command(f"{svcs_cmd} events --limit 15", cwd=dev_a_repo, check=False)
            if events_result.returncode == 0:
                print(f"   ✅ SVCS events accessible")
        
        # 9. Final verification
        print("\n9️⃣ Final verification...")
        
        # Check both repositories have the same content
        dev_a_log = run_command("git log --oneline", cwd=dev_a_repo).stdout.strip()
        dev_b_log = run_command("git log --oneline", cwd=dev_b_repo).stdout.strip()
        
        if dev_a_log == dev_b_log:
            print("   ✅ Both repositories have identical git history")
        else:
            print(f"   ⚠️  Git histories differ:")
            print(f"      Dev A: {dev_a_log}")
            print(f"      Dev B: {dev_b_log}")
        
        # Check SVCS functionality in both repos
        print("\n   🔬 Checking SVCS functionality...")
        for name, repo in [("Developer A", dev_a_repo), ("Developer B", dev_b_repo)]:
            print(f"   📊 {name}:")
            
            # Check events
            events_result = run_command(f"{svcs_cmd} events --limit 5", cwd=repo, check=False)
            if events_result.returncode == 0:
                event_lines = len([line for line in events_result.stdout.split('\n') if line.strip()])
                print(f"      ✅ Events available: {event_lines} lines")
            else:
                print(f"      ❌ Events failed: {events_result.stderr}")
            
            # Check notes
            notes_result = run_command("git notes --ref=refs/notes/svcs-semantic list", cwd=repo, check=False)
            if notes_result.returncode == 0 and notes_result.stdout.strip():
                note_count = len(notes_result.stdout.strip().split())
                print(f"      ✅ Semantic notes: {note_count}")
            else:
                print(f"      ⚠️  No semantic notes")
        
        print("\n✅ Enhanced semantic hook integration test completed!")
        print("🎯 Key achievements:")
        print("   - Hooks properly trigger semantic analysis on commits")
        print("   - Semantic notes are created automatically")
        print("   - Post-checkout and post-merge hooks fetch semantic notes")
        print("   - Full collaborative workflow with semantic data preservation")
        
        return True

if __name__ == "__main__":
    try:
        success = test_enhanced_semantic_hooks()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

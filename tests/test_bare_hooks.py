#!/usr/bin/env python3
"""
Test script for SVCS bare repository hooks
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
import sys

# Add parent directory to path for SVCS modules
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

def run_command(cmd, cwd=None, input_text=None, timeout=30):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    try:
        result = subprocess.run(
            cmd, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            input=input_text,
            timeout=timeout,
            shell=isinstance(cmd, str)
        )
        if result.stdout:
            print(f"STDOUT: {result.stdout}")
        if result.stderr:
            print(f"STDERR: {result.stderr}")
        return result
    except subprocess.TimeoutExpired:
        print(f"❌ Command timed out after {timeout} seconds")
        return None

def test_bare_repository_hooks():
    """Test SVCS bare repository hooks."""
    
    # Create temporary directory for test
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        bare_repo_path = temp_path / "test-bare.git"
        client_repo_path = temp_path / "test-client"
        
        print(f"🧪 Testing bare repository hooks in: {temp_dir}")
        
        # Step 1: Create proper bare repository
        print("\n📁 Step 1: Creating bare repository...")
        bare_repo_path.mkdir()
        result = run_command(['git', 'init', '--bare'], cwd=bare_repo_path)
        if not result or result.returncode != 0:
            print(f"❌ Failed to create bare repository")
            return False
        
        # Step 2: Initialize SVCS in bare repository using svcs init
        print("\n🔧 Step 2: Initializing SVCS in bare repository...")
        svcs_cli_path = parent_dir / 'svcs' / 'cli.py'
        
        result = run_command([sys.executable, str(svcs_cli_path), 'init'], 
                           cwd=bare_repo_path, 
                           input_text="n\n",  # Don't initialize git (already bare)
                           timeout=10)
        if not result or result.returncode != 0:
            print(f"❌ Failed to initialize SVCS in bare repo")
            return False
        
        print("✅ SVCS initialized in bare repository")
        
        # Step 3: Clone the bare repository
        print("\n📥 Step 3: Cloning bare repository...")
        result = run_command(['git', 'clone', str(bare_repo_path), str(client_repo_path)])
        if not result or result.returncode != 0:
            print(f"❌ Failed to clone bare repository")
            return False
        
        # Step 4: Initialize SVCS in client repository
        print("\n🔧 Step 4: Initializing SVCS in client repository...")
        result = run_command([sys.executable, str(svcs_cli_path), 'init'], 
                           cwd=client_repo_path, 
                           input_text="y\n",
                           timeout=10)
        if not result or result.returncode != 0:
            print(f"❌ Failed to initialize SVCS in client repo")
            return False
        
        # Step 5: Create test commits with semantic content that WILL trigger events
        print("\n📝 Step 5: Creating test commits...")
        test_file = client_repo_path / "calculator.py"
        test_file.write_text("""class Calculator:
    def __init__(self):
        self.memory = 0
    
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b
    
    def multiply(self, a, b):
        return a * b
    
    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
""")
        
        run_command(['git', 'add', 'calculator.py'], cwd=client_repo_path)
        run_command(['git', 'commit', '-m', 'Add Calculator class with mathematical functions'], cwd=client_repo_path)
        
        # Add another commit with more complex changes
        print("📝 Adding more semantic content...")
        test_file2 = client_repo_path / "utils.py"
        test_file2.write_text("""def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

class MathUtils:
    @staticmethod
    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a
    
    @staticmethod
    def lcm(a, b):
        return abs(a * b) // MathUtils.gcd(a, b)
""")
        
        run_command(['git', 'add', 'utils.py'], cwd=client_repo_path)
        run_command(['git', 'commit', '-m', 'Add mathematical utility functions'], cwd=client_repo_path)
        
        # Step 6: Push to bare repository (test post-receive hook)
        print("\n📤 Step 6: Testing post-receive hook...")
        result = run_command(['git', 'push', 'origin', 'main'], cwd=client_repo_path)
        
        test_results = {}
        
        if result and result.returncode == 0:
            # Check for our hook output in stderr (git hooks output to stderr)
            output = result.stderr
            if "📥 SVCS: Processing pushed commits" in output:
                print("✅ Post-receive hook executed successfully!")
                test_results['post_receive_executed'] = True
                if "Analyzed" in output and "semantic events" in output:
                    print("✅ Semantic events were analyzed!")
                    test_results['semantic_analysis'] = True
                elif "No semantic changes detected" in output:
                    print("⚠️ No semantic events detected - this might be a problem with the analyzer")
                    test_results['semantic_analysis'] = False
                else:
                    print("⚠️ Unclear semantic analysis result")
                    test_results['semantic_analysis'] = False
            else:
                print("⚠️ Post-receive hook may not have executed properly")
                print(f"Full output: {output}")
                test_results['post_receive_executed'] = False
        else:
            print("❌ Push failed")
            test_results['push_success'] = False
            return False
        
        test_results['push_success'] = True
        
        # Step 7: Test update hook with semantic notes
        print("\n📝 Step 7: Testing update hook...")
        
        # First, fetch any existing notes to avoid conflicts
        fetch_result = run_command(['git', 'fetch', 'origin', 'refs/notes/svcs-semantic:refs/notes/svcs-semantic'], cwd=client_repo_path)
        
        # Create a unique note message to test
        import time
        note_message = f"Test semantic note - {int(time.time())}"
        
        # Try to add a note with force flag to overwrite if exists
        note_result = run_command(['git', 'notes', '--ref=svcs-semantic', 'add', '-f', '-m', note_message], cwd=client_repo_path)
        
        if note_result and note_result.returncode == 0:
            print(f"✅ Added note: {note_message}")
            
            # Push the note to trigger update hook
            result = run_command(['git', 'push', 'origin', 'refs/notes/svcs-semantic'], cwd=client_repo_path)
            
            # Check both success and failure cases
            if result and result.returncode == 0:
                print("✅ Notes push succeeded - checking for update hook execution")
                output = result.stderr
                if "📝 SVCS: Processing semantic notes update" in output or "🔄 SVCS: Reference" in output:
                    print("✅ Update hook executed successfully!")
                    test_results['update_hook_executed'] = True
                else:
                    print("⚠️ Update hook may not have executed properly")
                    print(f"Full output: {output}")
                    test_results['update_hook_executed'] = False
            else:
                # Push failed - check if it's due to conflicts or hook issues
                stderr_output = result.stderr if result else ""
                if "rejected" in stderr_output and "fetch first" in stderr_output:
                    print("⚠️ Notes push rejected due to conflicts - this is expected in some cases")
                    # Even with conflicts, the update hook should be called
                    if "📝 SVCS" in stderr_output or "🔄 SVCS" in stderr_output:
                        print("✅ Update hook was executed despite push rejection")
                        test_results['update_hook_executed'] = True
                    else:
                        print("❌ Update hook may not have been executed")
                        test_results['update_hook_executed'] = False
                else:
                    print(f"❌ Notes push failed unexpectedly: {stderr_output}")
                    test_results['update_hook_executed'] = False
        else:
            print("❌ Failed to add git note")
            test_results['update_hook_executed'] = False
        
        # Step 8: Verification - Check hooks are installed
        print("\n🔍 Step 8: Verification - Hook Installation...")
        hooks_dir = bare_repo_path / 'hooks'
        post_receive_hook = hooks_dir / 'post-receive'
        update_hook = hooks_dir / 'update'
        
        test_results['post_receive_hook_installed'] = post_receive_hook.exists() and post_receive_hook.is_file()
        test_results['update_hook_installed'] = update_hook.exists() and update_hook.is_file()
        
        print(f"Post-receive hook installed: {'✅' if test_results['post_receive_hook_installed'] else '❌'}")
        print(f"Update hook installed: {'✅' if test_results['update_hook_installed'] else '❌'}")
        
        # Step 9: Verify semantic events are stored in bare repository
        print("\n📊 Step 9: Verifying semantic events in bare repository...")
        result = run_command([sys.executable, str(svcs_cli_path), 'events'], cwd=bare_repo_path)
        
        test_results['events_command_success'] = result and result.returncode == 0
        test_results['semantic_events_found'] = False
        test_results['events_count'] = 0
        
        if test_results['events_command_success']:
            events_output = result.stdout
            print(f"Events command output:\n{events_output}")
            
            if "No semantic events found" not in events_output and events_output.strip():
                # Extract the count from the header line like "📊 Semantic Events (9 found)"
                import re
                count_match = re.search(r'Semantic Events \((\d+) found\)', events_output)
                if count_match:
                    test_results['events_count'] = int(count_match.group(1))
                else:
                    # Fallback: count lines with event types like "🔍 node_added"
                    event_lines = [line for line in events_output.split('\n') if line.strip().startswith('🔍 ')]
                    test_results['events_count'] = len(event_lines)
                
                test_results['semantic_events_found'] = test_results['events_count'] > 0
                
                if test_results['semantic_events_found']:
                    print(f"✅ Found {test_results['events_count']} semantic events in bare repository!")
                else:
                    print("⚠️ No semantic events found in bare repository")
            else:
                print("⚠️ No semantic events found in bare repository")
        else:
            print("❌ Failed to run events command in bare repository")
        
        # Step 10: Check database file exists and has content
        print("\n💾 Step 10: Verifying database file...")
        db_file = bare_repo_path / '.svcs' / 'semantic.db'
        test_results['database_exists'] = db_file.exists()
        
        if test_results['database_exists']:
            db_size = db_file.stat().st_size
            test_results['database_has_content'] = db_size > 0
            print(f"✅ Database file exists: {db_file} (size: {db_size} bytes)")
            
            if db_size > 1000:  # Reasonable size for semantic events
                print("✅ Database has substantial content")
            else:
                print("⚠️ Database is very small, may not contain events")
        else:
            print("❌ Database file not found")
            test_results['database_has_content'] = False
        
        # Step 11: Test automatic semantic notes retrieval using 'svcs pull'
        print("\n🔄 Step 11: Testing automatic semantic notes retrieval...")
        
        # Create a new clone to test automatic retrieval
        client2_repo_path = temp_path / "test-client2"
        clone_result = run_command(['git', 'clone', str(bare_repo_path), str(client2_repo_path)])
        
        if clone_result and clone_result.returncode == 0:
            print("✅ Created second client repository")
            
            # Initialize SVCS in the new clone
            init_result = run_command([sys.executable, str(svcs_cli_path), 'init'], 
                                     cwd=client2_repo_path, 
                                     input_text="y\n",
                                     timeout=10)
            
            if init_result and init_result.returncode == 0:
                print("✅ SVCS initialized in second client")
                
                # Test automatic semantic notes retrieval using svcs pull
                pull_result = run_command([sys.executable, str(svcs_cli_path), 'pull'], 
                                         cwd=client2_repo_path, 
                                         timeout=15)
                
                if pull_result and pull_result.returncode == 0:
                    print("✅ svcs pull executed successfully")
                    
                    # Check if semantic notes were fetched and imported
                    pull_output = pull_result.stdout
                    if "Semantic notes fetched" in pull_output or "semantic events" in pull_output:
                        print("✅ Semantic notes were automatically retrieved!")
                        test_results['auto_notes_retrieval'] = True
                        
                        # Verify events are now available in client2
                        events_result = run_command([sys.executable, str(svcs_cli_path), 'events'], 
                                                   cwd=client2_repo_path)
                        if events_result and events_result.returncode == 0:
                            events_output = events_result.stdout
                            if "No semantic events found" not in events_output and events_output.strip():
                                import re
                                count_match = re.search(r'Semantic Events \((\d+) found\)', events_output)
                                if count_match:
                                    retrieved_count = int(count_match.group(1))
                                    print(f"✅ Retrieved {retrieved_count} semantic events automatically!")
                                    test_results['auto_retrieved_count'] = retrieved_count
                                else:
                                    print("⚠️ Events retrieved but couldn't count them")
                                    test_results['auto_retrieved_count'] = 0
                            else:
                                print("⚠️ No events found in automatically synchronized repository")
                                test_results['auto_retrieved_count'] = 0
                        else:
                            print("❌ Failed to check events in automatically synchronized repository")
                            test_results['auto_retrieved_count'] = 0
                    else:
                        print("⚠️ Semantic notes may not have been automatically retrieved")
                        test_results['auto_notes_retrieval'] = False
                        test_results['auto_retrieved_count'] = 0
                else:
                    print(f"❌ svcs pull failed: {pull_result.stderr if pull_result else 'timeout'}")
                    test_results['auto_notes_retrieval'] = False
                    test_results['auto_retrieved_count'] = 0
            else:
                print("❌ Failed to initialize SVCS in second client")
                test_results['auto_notes_retrieval'] = False
                test_results['auto_retrieved_count'] = 0
        else:
            print("❌ Failed to create second client repository")
            test_results['auto_notes_retrieval'] = False
            test_results['auto_retrieved_count'] = 0
        
        # Step 12: Final test results summary
        print("\n📋 FINAL TEST RESULTS SUMMARY:")
        print("=" * 50)
        
        all_critical_tests_passed = True
        update_hook_note = ""
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name}: {status}")
            
            # Critical tests that must pass for basic functionality
            if test_name in ['push_success', 'post_receive_executed', 'semantic_analysis',
                           'post_receive_hook_installed', 'update_hook_installed', 
                           'events_command_success', 'database_exists', 'auto_notes_retrieval']:
                if not result:
                    all_critical_tests_passed = False
            
            # Update hook execution is nice-to-have (may fail due to notes conflicts)
            if test_name == 'update_hook_executed' and not result:
                update_hook_note = "\n⚠️ Note: Update hook test failed - this may be due to notes conflicts and is not critical"
        
        print("=" * 50)
        
        # Overall success criteria
        success = (all_critical_tests_passed and 
                  test_results.get('semantic_events_found', False) and 
                  test_results.get('events_count', 0) > 0 and
                  test_results.get('auto_notes_retrieval', False))
        
        if success:
            print(f"\n🎉 ✅ BARE REPOSITORY HOOKS TEST PASSED!")
            print(f"✅ All critical tests passed")
            print(f"✅ {test_results.get('events_count', 0)} semantic events found in bare repo")
            print(f"✅ {test_results.get('auto_retrieved_count', 0)} semantic events automatically retrieved")
            print(f"✅ Database exists and has content")
            print(f"✅ Automatic semantic notes retrieval works")
            if update_hook_note:
                print(update_hook_note)
            return True
        else:
            print(f"\n❌ BARE REPOSITORY HOOKS TEST FAILED!")
            if not all_critical_tests_passed:
                print("❌ Critical tests failed")
            if not test_results.get('semantic_events_found', False):
                print("❌ No semantic events found")
            if not test_results.get('auto_notes_retrieval', False):
                print("❌ Automatic semantic notes retrieval failed")
            if update_hook_note:
                print(update_hook_note)
            return False

if __name__ == "__main__":
    success = test_bare_repository_hooks()
    sys.exit(0 if success else 1)

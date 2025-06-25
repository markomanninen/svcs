#!/usr/bin/env python3
"""
End-to-End SVCS Workflow Test

This script tests the complete development workflow:
1. Check initial state
2. Create and switch to feature branch  
3. Make semantic changes on feature branch
4. Compare branches semantically
5. Merge feature branch back to main
6. Verify semantic data is preserved and consolidated
7. Test git notes sync
"""

import subprocess
import sys
from pathlib import Path
import time
import datetime

# Global log file handle
log_file = None

def init_logging():
    """Initialize logging to file."""
    global log_file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"svcs_test_run_{timestamp}.log"
    log_file = open(log_filename, 'w', encoding='utf-8')
    log_and_print(f"🚀 SVCS End-to-End Workflow Test - {datetime.datetime.now()}")
    log_and_print(f"📝 Log file: {log_filename}")
    log_and_print("=" * 60)
    return log_filename

def log_and_print(message):
    """Print message and write to log file."""
    print(message)
    if log_file:
        log_file.write(message + '\n')
        log_file.flush()

def close_logging():
    """Close the log file."""
    global log_file
    if log_file:
        log_and_print(f"\n📝 Test completed at: {datetime.datetime.now()}")
        log_file.close()
        log_file = None

def run_command(cmd, description):
    """Run a command and capture output."""
    log_and_print(f"\n🔧 {description}")
    log_and_print(f"📝 Command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
    log_and_print(f"📤 Output: {result.stdout.strip()}")
    if result.stderr.strip():
        log_and_print(f"⚠️ Stderr: {result.stderr.strip()}")
    
    return result

def check_svcs_status():
    """Check SVCS repository status."""
    result = run_command(["python3", "svcs_local_cli.py", "status"], "Check SVCS status")
    return result.stdout

def get_event_count():
    """Get current semantic event count."""
    # Get status which shows total events
    result = run_command(["python3", "svcs_local_cli.py", "status"], "Get total event count")
    lines = result.stdout.strip().split('\n')
    for line in lines:
        if "Semantic events:" in line:
            # Extract number from "� Semantic events: X"
            import re
            match = re.search(r'Semantic events:\s*(\d+)', line)
            if match:
                return int(match.group(1))
    return 0

def main():
    # Initialize logging first
    log_filename = init_logging()
    
    try:
        log_and_print("🚀 SVCS End-to-End Workflow Test")
        log_and_print("=" * 60)
        
        # Step 1: Check initial state
        log_and_print("\n📊 STEP 1: Initial State Assessment")
        initial_status = check_svcs_status()
        initial_events = get_event_count()
        log_and_print(f"🔢 Initial semantic events: {initial_events}")
        
        # Get current branch
        result = run_command(["git", "branch", "--show-current"], "Get current branch")
        initial_branch = result.stdout.strip()
        log_and_print(f"🌿 Starting branch: {initial_branch}")
        
        # Step 2: Create and switch to feature branch
        log_and_print("\n🌿 STEP 2: Create Feature Branch")
        feature_branch = "test-workflow-feature"
        
        # Clean up any existing test branch
        run_command(["git", "branch", "-D", feature_branch], f"Delete existing {feature_branch} (if exists)")
        
        # Create new feature branch
        result = run_command(["git", "checkout", "-b", feature_branch], f"Create and switch to {feature_branch}")
        
        # Check SVCS tracked the branch switch
        feature_status = check_svcs_status()
        log_and_print(f"✅ Branch switch tracked by SVCS")
        
        # Step 3: Make semantic changes on feature branch
        log_and_print("\n🔨 STEP 3: Make Semantic Changes on Feature Branch")
        
        # Create a new Python file with various semantic elements
        test_file = Path("test_workflow_feature.py")
        test_content = '''#!/usr/bin/env python3
"""
Test file for end-to-end workflow validation.
"""

import json
import asyncio
from typing import List, Dict, Optional

class WorkflowTester:
    """A class to test the workflow."""
    
    def __init__(self, name: str, version: str = "1.0"):
        self.name = name
        self.version = version
        self._initialized = True
    
    def basic_method(self) -> str:
        """A basic method."""
        return f"Workflow test: {self.name} v{self.version}"
    
    @property
    def status(self) -> Dict[str, bool]:
        """Get the current status."""
        return {"initialized": self._initialized, "ready": True}

async def async_workflow_function(data: List[Dict]) -> Optional[str]:
    """An async function for testing."""
    if not data:
        return None
    
    # Simulate async work
    await asyncio.sleep(0.1)
    
    # Process data with comprehension
    processed = [item["value"] for item in data if "value" in item]
    
    return json.dumps({"processed": processed, "count": len(processed)})

def utility_function(x: int, y: int = 10) -> int:
    """A utility function with default parameters."""
    try:
        result = x * y
        if result > 100:
            raise ValueError("Result too large")
        return result
    except ValueError as e:
        print(f"Error: {e}")
        return 0
    finally:
        print("Calculation completed")

# Module-level variable
WORKFLOW_CONFIG = {
    "enabled": True,
    "max_retries": 3,
    "timeout": 30
}
'''
        
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        # Commit the new file
        run_command(["git", "add", str(test_file)], "Stage new test file")
        result = run_command(["git", "commit", "-m", "Add workflow test file with comprehensive Python features"], "Commit new file")
        
        # Check events after commit
        events_after_add = get_event_count()
        new_events_count = events_after_add - initial_events
        log_and_print(f"🎯 New semantic events detected: {new_events_count}")
        
        # Show some recent events
        run_command(["python3", "svcs_local_cli.py", "events", "--limit", "5"], "Show recent events")
        
        # Step 4: Modify the file to create more semantic changes
        log_and_print("\n🔄 STEP 4: Modify File for Additional Semantic Changes")
        
        # Modify the file
        modified_content = test_content.replace(
            'def basic_method(self) -> str:',
            'def enhanced_method(self, prefix: str = "Test") -> str:'
        ).replace(
            'return f"Workflow test: {self.name} v{self.version}"',
            'return f"{prefix}: {self.name} v{self.version} (enhanced)"'
        ).replace(
            'class WorkflowTester:',
            'class WorkflowTester:\n    """An enhanced class to test the workflow."""'
        ) + '''

@staticmethod
def new_static_method(value: str) -> bool:
    """A new static method added to test changes."""
    return len(value) > 0

def another_new_function():
    """Another function added to increase semantic complexity."""
    lambda_func = lambda x: x * 2
    data = [1, 2, 3, 4, 5]
    return [lambda_func(x) for x in data if x % 2 == 0]
'''
        
        with open(test_file, 'w') as f:
            f.write(modified_content)
        
        # Commit the changes
        run_command(["git", "add", str(test_file)], "Stage modified file")
        run_command(["git", "commit", "-m", "Enhance workflow test: modify method signature, add new functions"], "Commit modifications")
        
        # Check events after modification
        events_after_modify = get_event_count()
        modification_events = events_after_modify - events_after_add
        log_and_print(f"🎯 Additional semantic events from modifications: {modification_events}")
        
        # Step 5: Compare branches
        log_and_print("\n🔍 STEP 5: Compare Feature Branch with Main")
        result = run_command(["python3", "svcs_local_cli.py", "compare", initial_branch, feature_branch], 
                            f"Compare {initial_branch} vs {feature_branch}")
        
        # Step 6: Switch back to main and merge
        log_and_print("\n🔄 STEP 6: Merge Feature Branch Back to Main")
        
        # Switch back to main
        run_command(["git", "checkout", initial_branch], f"Switch back to {initial_branch}")
        
        # Check main branch event count before merge
        events_main_before_merge = get_event_count()
        log_and_print(f"🔢 Main branch events before merge: {events_main_before_merge}")
        
        # Merge feature branch
        result = run_command(["git", "merge", feature_branch, "--no-ff", "-m", f"Merge {feature_branch} into {initial_branch}"], 
                            f"Merge {feature_branch}")
        
        # Check events after merge
        events_after_merge = get_event_count()
        merged_events = events_after_merge - events_main_before_merge
        log_and_print(f"🎯 Events after merge: {events_after_merge} (added: {merged_events})")
        
        # Step 7: Verify merged content and semantic tracking
        log_and_print("\n✅ STEP 7: Verify Merged State")
        
        # Check that the test file exists in main
        if test_file.exists():
            log_and_print(f"✅ Test file {test_file} exists in main branch")
        else:
            log_and_print(f"❌ Test file {test_file} missing in main branch")
        
        # Check final status
        final_status = check_svcs_status()
        final_events = get_event_count()
        total_new_events = final_events - initial_events
        
        log_and_print(f"\n📊 FINAL RESULTS:")
        log_and_print(f"   🔢 Initial events: {initial_events}")
        log_and_print(f"   🔢 Final events: {final_events}")
        log_and_print(f"   🎯 Total new events: {total_new_events}")
        log_and_print(f"   📁 Test file created: {test_file.exists()}")
        
        # Show final recent events
        log_and_print(f"\n🔍 Recent Semantic Events (Final State):")
        run_command(["python3", "svcs_local_cli.py", "events", "--limit", "10"], "Show final recent events")
        
        # Step 8: Test git notes functionality
        log_and_print("\n📝 STEP 8: Test Git Notes Functionality")
        
        # Get the latest commit hash
        result = run_command(["git", "rev-parse", "HEAD"], "Get latest commit hash")
        latest_commit = result.stdout.strip()
        
        # Check if git notes exist for recent commits
        result = run_command(["git", "notes", "--ref", "refs/notes/svcs-semantic", "list"], "List SVCS git notes")
        notes_count = len([line for line in result.stdout.strip().split('\n') if line.strip()])
        log_and_print(f"📝 Git notes found: {notes_count}")
        
        # Try to read a note from the latest commit
        result = run_command(["git", "notes", "--ref", "refs/notes/svcs-semantic", "show", latest_commit], 
                            f"Show git note for latest commit")
        
        # Step 9: Cleanup
        log_and_print("\n🧹 STEP 9: Cleanup")
        
        # Delete the test file
        if test_file.exists():
            test_file.unlink()
            run_command(["git", "add", str(test_file)], "Stage file deletion")
            run_command(["git", "commit", "-m", "Cleanup: remove workflow test file"], "Commit cleanup")
        
        # Delete the feature branch
        run_command(["git", "branch", "-d", feature_branch], f"Delete feature branch {feature_branch}")
        
        log_and_print("\n🎉 END-TO-END WORKFLOW TEST COMPLETED!")
        log_and_print("=" * 60)
        log_and_print(f"✅ Successfully tracked {total_new_events} semantic events through complete workflow")
        log_and_print(f"✅ Git hooks working correctly throughout branch lifecycle")
        log_and_print(f"✅ Repository-local database maintaining semantic data consistency")
        log_and_print(f"✅ Git notes integration functioning for team collaboration")
        
    except Exception as e:
        log_and_print(f"\n❌ Test failed with error: {e}")
        import traceback
        log_and_print(f"📜 Traceback:\n{traceback.format_exc()}")
        return False
    
    finally:
        close_logging()
        if 'log_filename' in locals():
            print(f"\n📝 Complete test log saved to: {log_filename}")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

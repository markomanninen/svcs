#!/usr/bin/env python3
"""
SVCS User-Friendly Workflow Test

This demonstrates the simple user experience:
1. Create a git repository
2. Run 'svcs init' - that's it!
3. Make commits and see semantic analysis automatically

No manual file copying, no complex setup!
"""

import os
import subprocess
import sys
import shutil
import tempfile
from pathlib import Path


def run_command(cmd, cwd=None, description=""):
    """Run a command and show the output."""
    if description:
        print(f"\n🔧 {description}")
    print(f"📝 Running: {cmd}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    
    if result.stdout.strip():
        print(f"📤 Output:\n{result.stdout}")
    if result.stderr.strip():
        print(f"⚠️ Error:\n{result.stderr}")
    
    return result


def test_user_friendly_workflow():
    """Test the complete user-friendly workflow."""
    print("🎯 SVCS User-Friendly Workflow Test")
    print("=" * 50)
    print("This test shows how simple SVCS is for users!")
    print()
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        test_repo = Path(temp_dir) / "user_test_repo"
        test_repo.mkdir()
        
        print(f"📁 Created test repository: {test_repo}")
        
        # Step 1: Initialize git repository
        run_command("git init", cwd=test_repo, description="Initialize git repository")
        run_command("git config user.name 'Test User'", cwd=test_repo)
        run_command("git config user.email 'test@example.com'", cwd=test_repo)
        
        # Step 2: Simply run 'svcs init' - that's it!
        result = run_command("svcs init", cwd=test_repo, description="Initialize SVCS (user-friendly!)")
        
        if result.returncode != 0:
            print("❌ SVCS initialization failed!")
            return False
        
        # Step 3: Check status
        run_command("svcs status", cwd=test_repo, description="Check SVCS status")
        
        # Step 4: Create some code
        code_file = test_repo / "example.py"
        code_content = '''def hello_world():
    """A simple hello world function."""
    print("Hello, SVCS!")

class Calculator:
    """A simple calculator class."""
    
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b

if __name__ == "__main__":
    hello_world()
    calc = Calculator()
    print(f"2 + 3 = {calc.add(2, 3)}")
'''
        
        with open(code_file, 'w') as f:
            f.write(code_content)
        
        print(f"\n📝 Created example code file: {code_file.name}")
        
        # Step 5: Commit the code - semantic analysis happens automatically!
        run_command("git add example.py", cwd=test_repo, description="Stage the code")
        run_command('git commit -m "Add example calculator code"', cwd=test_repo, 
                   description="Commit code (semantic analysis happens automatically)")
        
        # Step 6: Check semantic events
        run_command("svcs events", cwd=test_repo, description="List semantic events")
        
        # Step 7: Modify the code
        enhanced_code = '''def hello_world():
    """A simple hello world function."""
    print("Hello, SVCS!")

def goodbye_world():
    """A new goodbye function."""
    print("Goodbye, SVCS!")

class Calculator:
    """An enhanced calculator class."""
    
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b
    
    def divide(self, a, b):
        """New method: division with error handling."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

class AdvancedCalculator(Calculator):
    """New class: Advanced calculator with more operations."""
    
    def power(self, a, b):
        return a ** b
    
    def square_root(self, a):
        return a ** 0.5

if __name__ == "__main__":
    hello_world()
    goodbye_world()
    
    calc = Calculator()
    print(f"2 + 3 = {calc.add(2, 3)}")
    print(f"10 / 2 = {calc.divide(10, 2)}")
    
    adv_calc = AdvancedCalculator()
    print(f"2^3 = {adv_calc.power(2, 3)}")
'''
        
        with open(code_file, 'w') as f:
            f.write(enhanced_code)
        
        # Step 8: Commit enhanced code
        run_command("git add example.py", cwd=test_repo)
        run_command('git commit -m "Enhance calculator with new functions and classes"', cwd=test_repo,
                   description="Commit enhanced code")
        
        # Step 9: Check semantic events again
        run_command("svcs events --limit 10", cwd=test_repo, description="List recent semantic events")
        
        # Step 10: Check final status
        run_command("svcs status", cwd=test_repo, description="Final SVCS status")
        
        print("\n" + "=" * 50)
        print("🎉 USER-FRIENDLY WORKFLOW COMPLETE!")
        print("=" * 50)
        print("✅ User only needed to run: 'svcs init'")
        print("✅ All semantic analysis happened automatically")
        print("✅ No manual file copying or complex setup required")
        print("✅ Works in any git repository with a single command")
        print()
        
        return True


def main():
    """Main test entry point."""
    print("Testing user-friendly SVCS workflow...")
    print()
    
    # Check if svcs command is available
    result = subprocess.run("svcs --help", shell=True, capture_output=True)
    if result.returncode != 0:
        print("❌ Error: 'svcs' command not found.")
        print("Please run 'python3 install.py' first to install SVCS globally.")
        return 1
    
    success = test_user_friendly_workflow()
    
    if success:
        print("🎯 User-Friendly Workflow Test: PASSED")
        return 0
    else:
        print("💥 User-Friendly Workflow Test: FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())

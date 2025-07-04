#!/usr/bin/env python3
"""
SVCS Full Git Workflow Test

This script tests the complete git workflow with SVCS semantic tracking:
1. Initialize a test repository
2. Set up SVCS repository-local tracking
3. Create initial commits with semantic changes
4. Create a feature branch
5. Make semantic changes on the feature branch
6. Merge the feature branch back to main
7. Verify semantic events are tracked throughout the process
8. Test branch comparison and merged event visibility
"""

import os
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path
import sqlite3
import json

class GitWorkflowTester:
    def __init__(self):
        self.test_repo = None
        self.original_dir = os.getcwd()
        self.svcs_dir = Path(self.original_dir)
        
    def run_command(self, cmd, check=True, capture_output=True):
        """Run a shell command and return the result"""
        print(f"Running: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, 
                              text=True, check=check)
        if capture_output and result.stdout.strip():
            print(f"Output: {result.stdout.strip()}")
        if result.stderr and result.stderr.strip():
            print(f"Error: {result.stderr.strip()}")
        return result
    
    def setup_test_repo(self):
        """Create a temporary git repository for testing"""
        self.test_repo = tempfile.mkdtemp(prefix="svcs_test_")
        print(f"\n🏗️  Setting up test repository: {self.test_repo}")
        
        os.chdir(self.test_repo)
        
        # Initialize git repo
        self.run_command("git init")
        self.run_command("git config user.name 'SVCS Test'")
        self.run_command("git config user.email 'test@svcs.local'")
        
        # Create initial Python file
        initial_code = '''def hello_world():
    """A simple hello world function"""
    return "Hello, World!"

class Calculator:
    """A basic calculator class"""
    
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b

if __name__ == "__main__":
    print(hello_world())
    calc = Calculator()
    print(f"2 + 3 = {calc.add(2, 3)}")
'''
        
        with open("main.py", "w") as f:
            f.write(initial_code)
        
        # Initial commit
        self.run_command("git add main.py")
        self.run_command("git commit -m 'Initial commit with basic Python code'")
        
        print(f"✅ Test repository initialized at: {self.test_repo}")
    
    def setup_svcs(self):
        """Initialize SVCS in the test repository"""
        print("\n🔧 Setting up SVCS repository-local tracking...")
        
        # Copy SVCS files to test repo
        svcs_files = [
            "svcs_repo_local.py",
            "svcs_local_cli.py", 
            "svcs_repo_hooks.py",
            "svcs_repo_local.py",
            "svcs_multilang.py"
        ]
        
        for file in svcs_files:
            src = self.svcs_dir / file
            dst = Path(self.test_repo) / file
            if src.exists():
                shutil.copy2(src, dst)
                print(f"Copied {file}")
        
        # Copy .svcs directory with analyzer
        svcs_src_dir = self.svcs_dir / ".svcs"
        svcs_dst_dir = Path(self.test_repo) / ".svcs"
        if svcs_src_dir.exists():
            shutil.copytree(svcs_src_dir, svcs_dst_dir)
            print("Copied .svcs directory")
        
        # Copy svcs_mcp directory for branch comparison
        svcs_mcp_src = self.svcs_dir / "svcs_mcp"
        svcs_mcp_dst = Path(self.test_repo) / "svcs_mcp"
        if svcs_mcp_src.exists():
            shutil.copytree(svcs_mcp_src, svcs_mcp_dst)
            print("Copied svcs_mcp directory")
        
        # Initialize SVCS
        self.run_command(f"python3 svcs_local_cli.py init")
        
        print("✅ SVCS repository-local tracking initialized")
    
    def check_semantic_events(self, description=""):
        """Check and display current semantic events"""
        print(f"\n📊 Checking semantic events {description}...")
        
        # Check database directly
        db_path = Path(self.test_repo) / ".svcs" / "semantic.db"
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM semantic_events")
            count = cursor.fetchone()[0]
            print(f"Total semantic events in database: {count}")
            
            # Get recent events
            cursor.execute("""
                SELECT commit_hash, event_type, location, confidence, layer
                FROM semantic_events 
                ORDER BY created_at DESC 
                LIMIT 10
            """)
            
            events = cursor.fetchall()
            if events:
                print("Recent semantic events:")
                for event in events:
                    commit_hash, event_type, location, confidence, layer = event
                    print(f"  - {event_type} at {location} (confidence: {confidence:.2f}, layer: {layer}) [{commit_hash[:8]}]")
            else:
                print("No semantic events found")
            
            conn.close()
        else:
            print("No semantic database found")
        
        # Also use CLI to check events
        result = self.run_command("python3 svcs_local_cli.py events --limit 5", check=False)
        
        return count if 'count' in locals() else 0
    
    def create_feature_branch(self):
        """Create and switch to a feature branch"""
        print("\n🌿 Creating feature branch...")
        
        self.run_command("git checkout -b feature/add-multiplication")
        
        # Add new functionality
        feature_code = '''def hello_world():
    """A simple hello world function"""
    return "Hello, World!"

def greet_user(name):
    """Greet a specific user - NEW FUNCTION"""
    return f"Hello, {name}!"

class Calculator:
    """A basic calculator class"""
    
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b
    
    def multiply(self, a, b):
        """NEW METHOD: Multiply two numbers"""
        return a * b
    
    def divide(self, a, b):
        """NEW METHOD: Divide two numbers"""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

class AdvancedCalculator(Calculator):
    """NEW CLASS: Advanced calculator with more operations"""
    
    def power(self, base, exponent):
        """Calculate power"""
        return base ** exponent
    
    def square_root(self, number):
        """Calculate square root"""
        if number < 0:
            raise ValueError("Cannot calculate square root of negative number")
        return number ** 0.5

if __name__ == "__main__":
    print(hello_world())
    print(greet_user("SVCS User"))
    
    calc = Calculator()
    print(f"2 + 3 = {calc.add(2, 3)}")
    print(f"5 * 4 = {calc.multiply(5, 4)}")
    
    adv_calc = AdvancedCalculator()
    print(f"2^3 = {adv_calc.power(2, 3)}")
    print(f"√16 = {adv_calc.square_root(16)}")
'''
        
        with open("main.py", "w") as f:
            f.write(feature_code)
        
        # Commit the changes
        self.run_command("git add main.py")
        self.run_command("git commit -m 'Add multiplication, division, and advanced calculator features'")
        
        print("✅ Feature branch created with new functionality")
    
    def merge_feature_branch(self):
        """Merge the feature branch back to main"""
        print("\n🔀 Merging feature branch to main...")
        
        # Switch back to main
        self.run_command("git checkout main")
        
        # Merge the feature branch
        self.run_command("git merge feature/add-multiplication")
        
        print("✅ Feature branch merged to main")
    
    def test_branch_comparison(self):
        """Test branch comparison functionality"""
        print("\n🔍 Testing branch comparison...")
        
        # Switch back to feature branch
        self.run_command("git checkout feature/add-multiplication")
        
        # Compare branches
        result = self.run_command("python3 svcs_local_cli.py compare main feature/add-multiplication", check=False)
        
        # Switch back to main
        self.run_command("git checkout main")
        
        print("✅ Branch comparison tested")
    
    def test_merged_events(self):
        """Test merged events visibility"""
        print("\n📈 Testing merged events visibility...")
        
        result = self.run_command("python3 svcs_local_cli.py merged-events --limit 10", check=False)
        
        print("✅ Merged events visibility tested")
    
    def cleanup(self):
        """Clean up test repository"""
        os.chdir(self.original_dir)
        if self.test_repo and Path(self.test_repo).exists():
            shutil.rmtree(self.test_repo)
            print(f"\n🧹 Cleaned up test repository: {self.test_repo}")
    
    def run_full_test(self):
        """Run the complete workflow test"""
        try:
            print("🚀 Starting SVCS Full Git Workflow Test")
            print("=" * 50)
            
            # Step 1: Setup
            self.setup_test_repo()
            self.setup_svcs()
            
            # Step 2: Check initial state
            initial_events = self.check_semantic_events("(initial state)")
            
            # Step 3: Create feature branch
            self.create_feature_branch()
            
            # Step 4: Check events after feature development
            feature_events = self.check_semantic_events("(after feature development)")
            
            # Step 5: Test branch comparison
            self.test_branch_comparison()
            
            # Step 6: Merge feature branch
            self.merge_feature_branch()
            
            # Step 7: Check events after merge
            merged_events = self.check_semantic_events("(after merge)")
            
            # Step 8: Test merged events visibility
            self.test_merged_events()
            
            # Step 9: Summary
            print("\n" + "=" * 50)
            print("🎯 WORKFLOW TEST SUMMARY")
            print("=" * 50)
            print(f"Initial semantic events: {initial_events}")
            print(f"Events after feature development: {feature_events}")
            print(f"Events after merge: {merged_events}")
            
            if merged_events > initial_events:
                print("✅ SUCCESS: Semantic events were tracked throughout the git workflow!")
                print("✅ Repository-local SVCS tracking is working correctly")
            else:
                print("❌ WARNING: Expected more semantic events after workflow")
            
            # Show git log
            print("\n📋 Git commit history:")
            self.run_command("git log --oneline --graph")
            
            # Show current branch
            print("\n🌿 Current branch:")
            self.run_command("git branch")
            
            print("\n🎉 Full Git Workflow Test Completed!")
            
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.cleanup()

if __name__ == "__main__":
    tester = GitWorkflowTester()
    tester.run_full_test()

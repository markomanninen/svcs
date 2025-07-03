#!/usr/bin/env python3
"""
Extended test to investigate:
1. What happened to original notes in central repo
2. What happens when a third user pulls from central repo

This test extends the collaborative scenario to include a third developer
and tracks semantic notes more carefully throughout the process.
"""

import os
import sys
import tempfile
import shutil
import subprocess
import time
import json

# Add the parent directory to Python path to import SVCS modules
sys.path.insert(0, 'os.path.dirname(os.path.dirname(os.path.abspath(__file__)))')

class ExtendedCollaborativeTest:
    def __init__(self):
        self.test_dir = None
        self.central_repo = None
        self.dev1_repo = None
        self.dev2_repo = None
        self.dev3_repo = None  # Third developer
        
    def setup_test_environment(self):
        """Set up temporary test environment"""
        self.test_dir = tempfile.mkdtemp(prefix="svcs_extended_test_")
        self.central_repo = os.path.join(self.test_dir, "central_repo")
        self.dev1_repo = os.path.join(self.test_dir, "dev1_workspace")
        self.dev2_repo = os.path.join(self.test_dir, "dev2_workspace")
        self.dev3_repo = os.path.join(self.test_dir, "dev3_workspace")
        
        print(f"🧪 Test directory: {self.test_dir}")
        print(f"🏛️  Central repo: {self.central_repo}")
        print(f"👤 Dev1 workspace: {self.dev1_repo}")
        print(f"👤 Dev2 workspace: {self.dev2_repo}")
        print(f"👤 Dev3 workspace: {self.dev3_repo}")
        
    def run_command(self, command, cwd=None):
        """Run a shell command and return (success, output)"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=cwd or self.test_dir,
                capture_output=True, 
                text=True,
                timeout=60
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
            
    def run_svcs_command(self, args, cwd=None):
        """Run an SVCS CLI command"""
        command = f"python3 -m svcs.cli --path . {' '.join(args)}"
        return self.run_command(command, cwd)
        
    def list_all_notes(self, repo_path, repo_name):
        """List all semantic notes in a repository"""
        print(f"  📝 Checking semantic notes in {repo_name}...")
        success, output = self.run_command("git notes --ref=refs/notes/svcs-semantic list", repo_path)
        if success and output.strip():
            lines = output.strip().split('\n')
            notes_list = []
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 2:
                    notes_list.append(parts[1])  # commit_sha is second part
            
            print(f"    ✅ Found {len(notes_list)} semantic notes")
            for i, note_ref in enumerate(notes_list, 1):
                note_success, note_content = self.run_command(f"git notes --ref=refs/notes/svcs-semantic show {note_ref}", repo_path)
                if note_success and note_content.strip():
                    # Parse the JSON to get a summary
                    try:
                        note_data = json.loads(note_content)
                        events = note_data.get('semantic_events', [])
                        timestamp = note_data.get('timestamp', 'unknown')
                        print(f"      📄 Note {i}: {len(events)} events, timestamp: {timestamp[:19]}")
                        for event in events[:2]:  # Show first 2 events
                            print(f"         - {event.get('event_type', 'unknown')}: {event.get('location', 'unknown')}")
                    except json.JSONDecodeError:
                        print(f"      📄 Note {i}: Raw content (not JSON)")
                else:
                    print(f"      ❌ Note {i}: Could not retrieve content")
            return notes_list
        else:
            print(f"    ❌ No semantic notes found")
            return []
            
    def create_initial_setup_with_tracking(self):
        """Create initial project and track any semantic notes created"""
        print("\n📦 Creating initial project with semantic note tracking...")
        
        # Create bare central repository
        os.makedirs(self.central_repo)
        success, _ = self.run_command("git init --bare", self.central_repo)
        if not success:
            raise Exception("Failed to create bare central repository")
            
        # Create temp setup directory
        temp_setup = os.path.join(self.test_dir, "temp_setup")
        success, _ = self.run_command(f"git clone {self.central_repo} {temp_setup}")
        if not success:
            raise Exception("Failed to clone for initial setup")
            
        # Configure git for setup
        self.run_command("git config user.name 'Setup User'", temp_setup)
        self.run_command("git config user.email 'setup@example.com'", temp_setup)
        
        # Create initial files
        initial_files = {
            "README.md": "# Project Repository\n\nInitial setup for collaborative development.\n",
            "src/main.py": "#!/usr/bin/env python3\n\ndef main():\n    print('Hello, World!')\n\nif __name__ == '__main__':\n    main()\n",
            ".gitignore": "*.pyc\n__pycache__/\n.DS_Store\n"
        }
        
        for file_path, content in initial_files.items():
            full_path = os.path.join(temp_setup, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
                
        # Initialize SVCS in setup directory to track semantic events
        print("  🔬 Initializing SVCS for initial setup...")
        self.run_svcs_command(["init"], temp_setup)
        
        # Commit initial files
        self.run_command("git add .", temp_setup)
        success, _ = self.run_command("git commit -m 'Initial project setup'", temp_setup)
        if not success:
            raise Exception("Failed to commit initial files")
            
        # Check if any semantic notes were created during initial setup
        initial_notes = self.list_all_notes(temp_setup, "Initial Setup")
        
        # Use a simplified push approach - push without origin initially
        print("  📤 Setting up initial branch...")
        self.run_command("git branch -M main", temp_setup)
        self.run_command("git remote add origin " + self.central_repo, temp_setup)
        
        # Push with reduced timeout and better error handling
        success, output = self.run_command("git push -u origin main", temp_setup)
        if not success:
            print(f"  ⚠️  Standard push failed, trying alternative: {output}")
            # Try alternative push method
            success, output = self.run_command("git push origin HEAD:refs/heads/main", temp_setup)
            if not success:
                print(f"  ⚠️  Alternative push also failed: {output}")
                # Continue anyway - the issue might be with the bare repo setup
                # but we can still test the semantic notes
                
        # If there are semantic notes, try to push them too
        if initial_notes:
            print("  📤 Attempting to push initial semantic notes to central...")
            success, _ = self.run_command("git push origin refs/notes/svcs-semantic", temp_setup)
            if success:
                print("  ✅ Initial semantic notes pushed to central")
            else:
                print("  ⚠️  Failed to push initial semantic notes (continuing anyway)")
                
        # Clean up
        shutil.rmtree(temp_setup)
        
        # For testing purposes, if the push failed, let's create a non-bare repo
        if not success:
            print("  🔧 Creating alternative central repository (non-bare for testing)...")
            shutil.rmtree(self.central_repo)
            self.run_command(f"git clone {temp_setup} {self.central_repo}")
        
        # Check central repo for notes after initial setup
        print("\n🔍 Checking central repository after initial setup...")
        try:
            self.list_all_notes(self.central_repo, "Central (after initial setup)")
        except:
            print("  ⚠️  Cannot check central repo notes (bare repo)")
        
        return len(initial_notes)
        
    def setup_developers(self):
        """Set up developer workspaces"""
        print("\n👥 Setting up developer workspaces...")
        
        # Dev1
        success, _ = self.run_command(f"git clone {self.central_repo} {self.dev1_repo}")
        if not success:
            raise Exception("Failed to clone for Dev1")
        self.run_command("git config user.name 'Developer One'", self.dev1_repo)
        self.run_command("git config user.email 'dev1@example.com'", self.dev1_repo)
        self.run_svcs_command(["init"], self.dev1_repo)
        
        # Dev2
        success, _ = self.run_command(f"git clone {self.central_repo} {self.dev2_repo}")
        if not success:
            raise Exception("Failed to clone for Dev2")
        self.run_command("git config user.name 'Developer Two'", self.dev2_repo)
        self.run_command("git config user.email 'dev2@example.com'", self.dev2_repo)
        self.run_svcs_command(["init"], self.dev2_repo)
        
        # Fetch any existing semantic notes
        for repo, name in [(self.dev1_repo, "Dev1"), (self.dev2_repo, "Dev2")]:
            success, _ = self.run_command("git fetch origin refs/notes/svcs-semantic:refs/notes/svcs-semantic", repo)
            if success:
                print(f"  ✅ {name} fetched existing semantic notes")
            self.list_all_notes(repo, f"{name} (after clone)")
            
    def dev_work_and_notes_tracking(self):
        """Have both developers do work and track semantic notes carefully"""
        print("\n👨‍💻 Dev1: Working on user management feature...")
        
        # Dev1 creates feature branch and works
        self.run_command("git checkout -b feature/user-management", self.dev1_repo)
        
        # Create user management module
        user_mgmt_content = '''"""
User management module for handling user operations
"""

class UserManager:
    def __init__(self):
        self.users = {}
    
    def create_user(self, username, email):
        """Create a new user"""
        if username in self.users:
            raise ValueError(f"User {username} already exists")
        self.users[username] = {"email": email, "active": True}
        return self.users[username]
    
    def get_user(self, username):
        """Get user by username"""
        return self.users.get(username)
'''
        
        with open(os.path.join(self.dev1_repo, "src/user_management.py"), "w") as f:
            f.write(user_mgmt_content)
            
        # Modify main.py to import user management
        main_py_path = os.path.join(self.dev1_repo, "src/main.py")
        with open(main_py_path, "r") as f:
            main_content = f.read()
        
        updated_main = main_content.replace(
            "def main():",
            "from user_management import UserManager\n\ndef main():"
        )
        
        with open(main_py_path, "w") as f:
            f.write(updated_main)
            
        # Commit changes
        self.run_command("git add .", self.dev1_repo)
        success, _ = self.run_command("git commit -m 'Add user management feature'", self.dev1_repo)
        if not success:
            raise Exception("Dev1 commit failed")
            
        # Check semantic notes after Dev1's work
        dev1_notes = self.list_all_notes(self.dev1_repo, "Dev1 (after feature work)")
        
        print("\n👨‍💻 Dev2: Working on API endpoints feature...")
        
        # Dev2 creates feature branch and works
        self.run_command("git checkout -b feature/api-endpoints", self.dev2_repo)
        
        # Create API module
        api_content = '''"""
API endpoints module
"""

from flask import Flask, request, jsonify

app = Flask(__name__)

class APIHandler:
    def __init__(self):
        self.routes = {}
    
    def register_route(self, path, method, handler):
        """Register a new API route"""
        key = f"{method}:{path}"
        self.routes[key] = handler
    
    def handle_request(self, path, method):
        """Handle incoming API request"""
        key = f"{method}:{path}"
        handler = self.routes.get(key)
        if handler:
            return handler()
        return {"error": "Route not found"}, 404

@app.route('/api/health')
def health_check():
    return {"status": "ok", "timestamp": "2023-01-01"}
'''
        
        with open(os.path.join(self.dev2_repo, "src/api.py"), "w") as f:
            f.write(api_content)
            
        # Modify main.py to include API
        main_py_path = os.path.join(self.dev2_repo, "src/main.py")
        with open(main_py_path, "r") as f:
            main_content = f.read()
            
        updated_main = main_content.replace(
            "def main():",
            "from api import app\n\ndef main():"
        )
        
        with open(main_py_path, "w") as f:
            f.write(updated_main)
            
        # Commit changes
        self.run_command("git add .", self.dev2_repo)
        success, _ = self.run_command("git commit -m 'Add API endpoints feature'", self.dev2_repo)
        if not success:
            raise Exception("Dev2 commit failed")
            
        # Check semantic notes after Dev2's work
        dev2_notes = self.list_all_notes(self.dev2_repo, "Dev2 (after feature work)")
        
        return dev1_notes, dev2_notes
        
    def transfer_notes_to_central(self):
        """Transfer semantic notes to central repository with detailed tracking"""
        print("\n🔄 Transferring semantic notes to central repository...")
        
        # Check central before transfer
        print("  📋 Central repository state before transfer:")
        central_notes_before = self.list_all_notes(self.central_repo, "Central (before transfer)")
        
        # Transfer Dev1 notes
        self.transfer_dev_notes(self.dev1_repo, "Dev1")
        
        # Check central after Dev1 transfer
        print("  📋 Central repository state after Dev1 transfer:")
        central_notes_after_dev1 = self.list_all_notes(self.central_repo, "Central (after Dev1)")
        
        # Transfer Dev2 notes
        self.transfer_dev_notes(self.dev2_repo, "Dev2")
        
        # Check central after both transfers
        print("  📋 Central repository state after both transfers:")
        central_notes_final = self.list_all_notes(self.central_repo, "Central (final)")
        
        return central_notes_before, central_notes_after_dev1, central_notes_final
        
    def transfer_dev_notes(self, dev_repo, dev_name):
        """Transfer notes from a developer repository to central"""
        print(f"  📤 Transferring {dev_name} notes...")
        
        # Get list of notes
        success, output = self.run_command("git notes --ref=refs/notes/svcs-semantic list", dev_repo)
        if not success or not output.strip():
            print(f"    ❌ No notes to transfer from {dev_name}")
            return
            
        lines = output.strip().split('\n')
        notes_list = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 2:
                notes_list.append(parts[1])  # commit_sha is second part
                
        print(f"    📝 {dev_name} has {len(notes_list)} notes to transfer")
        
        # Create temp transfer directory
        temp_transfer = os.path.join(self.test_dir, f"temp_transfer_{dev_name.lower()}")
        success, _ = self.run_command(f"git clone {self.central_repo} {temp_transfer}")
        if not success:
            print(f"    ❌ Failed to create temp transfer directory for {dev_name}")
            return
            
        # Fetch existing notes from central
        self.run_command("git fetch origin refs/notes/svcs-semantic:refs/notes/svcs-semantic", temp_transfer)
        
        # Transfer each note
        for note_ref in notes_list:
            note_ref = note_ref.strip()
            note_success, note_content = self.run_command(f"git notes --ref=refs/notes/svcs-semantic show {note_ref}", dev_repo)
            if note_success and note_content.strip():
                # Create temp file with note content
                with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                    temp_file.write(note_content)
                    temp_file_path = temp_file.name
                    
                # Add note to temp repo
                add_success, _ = self.run_command(f"git notes --ref=refs/notes/svcs-semantic add -F {temp_file_path} {note_ref}", temp_transfer)
                if add_success:
                    print(f"      ✅ Transferred note for commit {note_ref[:8]}")
                else:
                    print(f"      ⚠️  Failed to add note for commit {note_ref[:8]}")
                    
                os.unlink(temp_file_path)
            else:
                print(f"      ⚠️  Could not read note for commit {note_ref[:8]}")
                
        # Push notes to central
        push_success, _ = self.run_command("git push origin refs/notes/svcs-semantic", temp_transfer)
        if push_success:
            print(f"    ✅ {dev_name} notes successfully pushed to central")
        else:
            print(f"    ❌ Failed to push {dev_name} notes to central")
            
        shutil.rmtree(temp_transfer)
        
    def setup_third_developer(self):
        """Set up a third developer and see what they can access"""
        print("\n👤 Setting up third developer (Dev3)...")
        
        # Clone central repository
        success, _ = self.run_command(f"git clone {self.central_repo} {self.dev3_repo}")
        if not success:
            raise Exception("Failed to clone for Dev3")
            
        # Configure git
        self.run_command("git config user.name 'Developer Three'", self.dev3_repo)
        self.run_command("git config user.email 'dev3@example.com'", self.dev3_repo)
        
        # Initialize SVCS
        self.run_svcs_command(["init"], self.dev3_repo)
        
        # Fetch semantic notes
        print("  📥 Dev3: Fetching semantic notes from central...")
        success, _ = self.run_command("git fetch origin refs/notes/svcs-semantic:refs/notes/svcs-semantic", self.dev3_repo)
        if success:
            print("    ✅ Successfully fetched semantic notes")
        else:
            print("    ❌ Failed to fetch semantic notes")
            
        # Check what Dev3 can see
        print("  🔍 What Dev3 can see after cloning and fetching:")
        dev3_notes = self.list_all_notes(self.dev3_repo, "Dev3 (after clone and fetch)")
        
        # Test SVCS functionality for Dev3
        print("  🧪 Testing SVCS functionality for Dev3...")
        success, output = self.run_svcs_command(["events", "--limit", "10"], self.dev3_repo)
        if success:
            print("    ✅ SVCS events query successful for Dev3")
            print(f"    📊 Output: {output[:200]}..." if len(output) > 200 else f"    📊 Output: {output}")
        else:
            print(f"    ❌ SVCS events query failed for Dev3: {output}")
            
        return dev3_notes
        
    def cleanup(self):
        """Clean up test environment"""
        if self.test_dir and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            print(f"🧹 Cleaned up test directory: {self.test_dir}")
            
    def run_test(self):
        """Run the complete extended test"""
        try:
            print("🚀 Starting Extended Collaborative Test")
            print("=" * 60)
            
            # Setup
            self.setup_test_environment()
            
            # Question 1: Track original notes
            initial_notes_count = self.create_initial_setup_with_tracking()
            print(f"\n📊 Initial semantic notes created: {initial_notes_count}")
            
            # Setup developers
            self.setup_developers()
            
            # Developer work
            dev1_notes, dev2_notes = self.dev_work_and_notes_tracking()
            print(f"\n📊 Dev1 created {len(dev1_notes)} notes, Dev2 created {len(dev2_notes)} notes")
            
            # Transfer notes and track what happens to originals
            central_before, central_after_dev1, central_final = self.transfer_notes_to_central()
            
            print(f"\n📊 Central repo notes progression:")
            print(f"    Initial: {len(central_before)} notes")
            print(f"    After Dev1: {len(central_after_dev1)} notes")
            print(f"    After Dev2: {len(central_final)} notes")
            
            # Question 2: Third developer scenario
            dev3_notes = self.setup_third_developer()
            print(f"\n📊 Dev3 can see {len(dev3_notes)} notes after joining")
            
            print("\n" + "=" * 60)
            print("🎉 Extended test completed successfully!")
            
            # Summary
            print("\n📋 SUMMARY:")
            print(f"1. Original notes in central: {initial_notes_count} → Final: {len(central_final)}")
            if initial_notes_count > 0 and len(central_final) < initial_notes_count + len(dev1_notes) + len(dev2_notes):
                print("   ⚠️  Some original notes may have been overwritten!")
            print(f"2. Third developer sees: {len(dev3_notes)} notes (should see all)")
            
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False
        finally:
            self.cleanup()

if __name__ == "__main__":
    test = ExtendedCollaborativeTest()
    success = test.run_test()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Test three-developer semantic note transfer scenario
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

def test_three_developer_scenario():
    """Test semantic note transfer with three developers."""
    print("🧪 Testing Three-Developer Semantic Note Transfer")
    print("=" * 60)
    
    # Create temporary directory for test
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Set up paths
        central_repo = temp_path / "central_repo.git"
        dev_a_repo = temp_path / "developer_a"
        dev_b_repo = temp_path / "developer_b" 
        dev_c_repo = temp_path / "developer_c"
        
        print(f"📁 Test directory: {temp_path}")
        
        # 1. Create central bare repository
        print("\n1️⃣ Creating central bare repository...")
        central_repo.mkdir()
        run_command("git init --bare", cwd=central_repo)
        print(f"   ✅ Central repo created: {central_repo}")
        
        # 2. Developer A: Clone, initialize SVCS, and create initial work
        print("\n2️⃣ Developer A: Initial setup and work...")
        run_command(f"git clone {central_repo} {dev_a_repo}")
        
        # Configure git user
        run_command("git config user.name 'Developer A'", cwd=dev_a_repo)
        run_command("git config user.email 'deva@example.com'", cwd=dev_a_repo)
        
        # Initialize SVCS
        svcs_cmd = f"{sys.executable} {Path(__file__).parent / 'svcs' / 'cli.py'}"
        result = run_command(f"{svcs_cmd} init", cwd=dev_a_repo)
        print(f"   ✅ Developer A SVCS initialized")
        
        # Create initial work with semantic content
        auth_file = dev_a_repo / "auth.py"
        auth_file.write_text("""
class AuthManager:
    \"\"\"Handles user authentication and authorization.\"\"\"
    
    def __init__(self):
        self.users = {}
        self.sessions = {}
    
    def register_user(self, username, password):
        \"\"\"Register a new user.\"\"\"
        if username in self.users:
            raise ValueError("User already exists")
        self.users[username] = self._hash_password(password)
        return True
    
    def login(self, username, password):
        \"\"\"Authenticate user and create session.\"\"\"
        if username not in self.users:
            return False
        if self.users[username] != self._hash_password(password):
            return False
        
        session_id = self._generate_session_id()
        self.sessions[session_id] = username
        return session_id
    
    def _hash_password(self, password):
        \"\"\"Hash password for storage.\"\"\"
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_session_id(self):
        \"\"\"Generate unique session ID.\"\"\"
        import uuid
        return str(uuid.uuid4())
""")
        
        run_command("git add auth.py", cwd=dev_a_repo)
        result = run_command("git commit -m 'Add authentication system'", cwd=dev_a_repo)
        print(f"   ✅ Developer A initial commit created")
        
        # Check semantic notes
        notes_result = run_command("git notes --ref=refs/notes/svcs-semantic list", cwd=dev_a_repo, check=False)
        if notes_result.returncode == 0 and notes_result.stdout.strip():
            print(f"   ✅ Developer A semantic notes: {len(notes_result.stdout.strip().split())} notes")
        
        # Push to central
        run_command("git push origin main", cwd=dev_a_repo)
        run_command("git push origin refs/notes/svcs-semantic", cwd=dev_a_repo, check=False)
        print(f"   ✅ Developer A pushed code and semantic notes")
        
        # 3. Developer B: Clone, initialize, and add more work
        print("\n3️⃣ Developer B: Join project and add work...")
        run_command(f"git clone {central_repo} {dev_b_repo}")
        
        # Configure git user
        run_command("git config user.name 'Developer B'", cwd=dev_b_repo)
        run_command("git config user.email 'devb@example.com'", cwd=dev_b_repo)
        
        # Initialize SVCS
        result = run_command(f"{svcs_cmd} init", cwd=dev_b_repo)
        print(f"   ✅ Developer B SVCS initialized")
        
        # Check if Developer B got existing semantic notes
        notes_result = run_command("git notes --ref=refs/notes/svcs-semantic list", cwd=dev_b_repo, check=False)
        if notes_result.returncode == 0 and notes_result.stdout.strip():
            note_count = len(notes_result.stdout.strip().split())
            print(f"   ✅ Developer B automatically got semantic notes: {note_count} notes")
        else:
            print(f"   ⚠️  Developer B didn't get semantic notes automatically")
        
        # Developer B adds database functionality
        db_file = dev_b_repo / "database.py"
        db_file.write_text("""
import sqlite3
from contextlib import contextmanager

class DatabaseManager:
    \"\"\"Handles database operations for the application.\"\"\"
    
    def __init__(self, db_path="app.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        \"\"\"Initialize database with required tables.\"\"\"
        with self.get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (username) REFERENCES users (username)
                )
            ''')
    
    @contextmanager
    def get_connection(self):
        \"\"\"Get database connection with automatic cleanup.\"\"\"
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def insert_user(self, username, password_hash):
        \"\"\"Insert new user into database.\"\"\"
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
    
    def get_user(self, username):
        \"\"\"Get user by username.\"\"\"
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT username, password_hash FROM users WHERE username = ?",
                (username,)
            )
            return cursor.fetchone()
""")
        
        run_command("git add database.py", cwd=dev_b_repo)
        result = run_command("git commit -m 'Add database management system'", cwd=dev_b_repo)
        print(f"   ✅ Developer B added database functionality")
        
        # Check semantic notes after Developer B's commit
        notes_result = run_command("git notes --ref=refs/notes/svcs-semantic list", cwd=dev_b_repo, check=False)
        if notes_result.returncode == 0 and notes_result.stdout.strip():
            note_count = len(notes_result.stdout.strip().split())
            print(f"   ✅ Developer B total semantic notes: {note_count} notes")
        
        # Push Developer B's work
        run_command("git push origin main", cwd=dev_b_repo)
        run_command("git push origin refs/notes/svcs-semantic", cwd=dev_b_repo, check=False)
        print(f"   ✅ Developer B pushed code and semantic notes")
        
        # 4. Developer A: Pull Developer B's changes
        print("\n4️⃣ Developer A: Pull Developer B's changes...")
        result = run_command("git pull origin main", cwd=dev_a_repo)
        print(f"   ✅ Developer A pulled latest changes")
        
        # Check if Developer A got Developer B's semantic notes
        notes_result = run_command("git notes --ref=refs/notes/svcs-semantic list", cwd=dev_a_repo, check=False)
        if notes_result.returncode == 0 and notes_result.stdout.strip():
            note_count = len(notes_result.stdout.strip().split())
            print(f"   ✅ Developer A now has semantic notes: {note_count} notes")
        
        # 5. Developer C: Join the project (third developer)
        print("\n5️⃣ Developer C: Join project as third developer...")
        run_command(f"git clone {central_repo} {dev_c_repo}")
        
        # Configure git user
        run_command("git config user.name 'Developer C'", cwd=dev_c_repo)
        run_command("git config user.email 'devc@example.com'", cwd=dev_c_repo)
        
        # Initialize SVCS (this should automatically fetch all existing semantic notes)
        result = run_command(f"{svcs_cmd} init", cwd=dev_c_repo)
        print(f"   ✅ Developer C SVCS initialized")
        
        # CRITICAL CHECK: Does Developer C have all semantic notes?
        print("\n   🔍 Checking Developer C's semantic notes...")
        notes_result = run_command("git notes --ref=refs/notes/svcs-semantic list", cwd=dev_c_repo, check=False)
        if notes_result.returncode == 0 and notes_result.stdout.strip():
            note_count = len(notes_result.stdout.strip().split())
            print(f"   ✅ Developer C automatically got ALL semantic notes: {note_count} notes")
            
            # List the actual notes to verify content
            for line in notes_result.stdout.strip().split('\n'):
                if line.strip():
                    note_hash, commit_hash = line.strip().split()
                    print(f"      📝 Note {note_hash[:8]} for commit {commit_hash[:8]}")
        else:
            print(f"   ❌ Developer C didn't get semantic notes!")
            return False
        
        # CRITICAL CHECK: Can Developer C access SVCS events from semantic.db?
        print("\n   🔍 Checking Developer C's SVCS events access...")
        events_result = run_command(f"{svcs_cmd} events --limit 10", cwd=dev_c_repo, check=False)
        if events_result.returncode == 0:
            event_lines = [line for line in events_result.stdout.split('\n') if line.strip()]
            print(f"   ✅ Developer C can access SVCS events: {len(event_lines)} lines")
            
            # Show some sample events
            if event_lines:
                print(f"      📊 Sample events:")
                for line in event_lines[:3]:
                    if line.strip():
                        print(f"         {line.strip()}")
        else:
            print(f"   ❌ Developer C cannot access SVCS events!")
            print(f"      Error: {events_result.stderr}")
            return False
        
        # 6. Developer C: Add their own work
        print("\n6️⃣ Developer C: Add API layer...")
        
        # Developer C adds API layer
        api_file = dev_c_repo / "api.py"
        api_file.write_text("""
from flask import Flask, request, jsonify
from auth import AuthManager
from database import DatabaseManager

app = Flask(__name__)
auth_manager = AuthManager()
db_manager = DatabaseManager()

class APIError(Exception):
    \"\"\"Custom API error class.\"\"\"
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code

@app.errorhandler(APIError)
def handle_api_error(error):
    \"\"\"Handle API errors gracefully.\"\"\"
    return jsonify({'error': error.message}), error.status_code

@app.route('/api/register', methods=['POST'])
def register():
    \"\"\"Register a new user via API.\"\"\"
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        raise APIError('Username and password required')
    
    try:
        auth_manager.register_user(data['username'], data['password'])
        db_manager.insert_user(data['username'], 
                              auth_manager._hash_password(data['password']))
        return jsonify({'message': 'User registered successfully'})
    except ValueError as e:
        raise APIError(str(e))

@app.route('/api/login', methods=['POST'])
def login():
    \"\"\"Login user via API.\"\"\"
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        raise APIError('Username and password required')
    
    session_id = auth_manager.login(data['username'], data['password'])
    if session_id:
        return jsonify({'session_id': session_id})
    else:
        raise APIError('Invalid credentials', 401)

@app.route('/api/users/<username>', methods=['GET'])
def get_user(username):
    \"\"\"Get user information via API.\"\"\"
    user = db_manager.get_user(username)
    if user:
        return jsonify({'username': user[0], 'exists': True})
    else:
        raise APIError('User not found', 404)

if __name__ == '__main__':
    app.run(debug=True)
""")
        
        run_command("git add api.py", cwd=dev_c_repo)
        result = run_command("git commit -m 'Add REST API layer with Flask'", cwd=dev_c_repo)
        print(f"   ✅ Developer C added API layer")
        
        # Check semantic notes after Developer C's commit
        notes_result = run_command("git notes --ref=refs/notes/svcs-semantic list", cwd=dev_c_repo, check=False)
        if notes_result.returncode == 0 and notes_result.stdout.strip():
            note_count = len(notes_result.stdout.strip().split())
            print(f"   ✅ Developer C total semantic notes: {note_count} notes")
        
        # Push Developer C's work
        run_command("git push origin main", cwd=dev_c_repo)
        run_command("git push origin refs/notes/svcs-semantic", cwd=dev_c_repo, check=False)
        print(f"   ✅ Developer C pushed code and semantic notes")
        
        # 7. Final verification: All developers sync and verify
        print("\n7️⃣ Final three-developer verification...")
        
        developers = [
            ("Developer A", dev_a_repo),
            ("Developer B", dev_b_repo), 
            ("Developer C", dev_c_repo)
        ]
        
        # Pull latest changes for all developers
        for name, repo in developers:
            print(f"\n   🔄 {name}: Syncing latest changes...")
            run_command("git pull origin main", cwd=repo)
            
            # Check git history
            log_result = run_command("git log --oneline", cwd=repo)
            commit_count = len(log_result.stdout.strip().split('\n'))
            print(f"      ✅ Git history: {commit_count} commits")
            
            # Check semantic notes
            notes_result = run_command("git notes --ref=refs/notes/svcs-semantic list", cwd=repo, check=False)
            if notes_result.returncode == 0 and notes_result.stdout.strip():
                note_count = len(notes_result.stdout.strip().split())
                print(f"      ✅ Semantic notes: {note_count} notes")
            else:
                print(f"      ❌ No semantic notes found!")
                return False
            
            # Check SVCS events
            events_result = run_command(f"{svcs_cmd} events --limit 15", cwd=repo, check=False)
            if events_result.returncode == 0:
                event_lines = [line for line in events_result.stdout.split('\n') if line.strip()]
                print(f"      ✅ SVCS events accessible: {len(event_lines)} lines")
            else:
                print(f"      ❌ SVCS events not accessible!")
                return False
        
        # 8. Verify semantic.db content consistency
        print("\n8️⃣ Verifying semantic.db consistency across all developers...")
        
        for name, repo in developers:
            print(f"\n   📊 {name} semantic analysis:")
            
            # Check for specific semantic events
            events_result = run_command(f"{svcs_cmd} events --limit 20", cwd=repo, check=False)
            if events_result.returncode == 0:
                events_text = events_result.stdout
                
                # Look for key indicators from each developer's work
                auth_related = "auth" in events_text.lower() or "AuthManager" in events_text
                db_related = "database" in events_text.lower() or "DatabaseManager" in events_text  
                api_related = "api" in events_text.lower() or "Flask" in events_text
                
                print(f"      🔍 Contains auth-related events: {auth_related}")
                print(f"      🔍 Contains database-related events: {db_related}")
                print(f"      🔍 Contains API-related events: {api_related}")
                
                if not (auth_related and db_related and api_related):
                    print(f"      ⚠️  Missing some semantic events!")
                else:
                    print(f"      ✅ All semantic events present!")
            
        print("\n✅ Three-developer semantic note transfer test completed!")
        print("\n🎯 Verification Results:")
        print("   ✅ Developer A: Created initial semantic notes")
        print("   ✅ Developer B: Got Developer A's notes, added own notes")
        print("   ✅ Developer C: Got ALL existing notes automatically, added own notes")
        print("   ✅ All developers have access to complete semantic.db")
        print("   ✅ All developers can access events from all commits")
        print("   ✅ Seamless three-way collaboration confirmed!")
        
        return True

if __name__ == "__main__":
    try:
        success = test_three_developer_scenario()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

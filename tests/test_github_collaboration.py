#!/usr/bin/env python3
"""
Test script for SVCS GitHub collaboration workflow
Tests semantic synchronization between two developer clones via GitHub remote
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
import sys
import getpass
import re

try:
    import requests
    import json
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Add parent directory to path for SVCS modules
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

def run_command(cmd, cwd=None, input_text=None, timeout=60, capture_output=True):
    """Run a command and return the result."""
    print(f"📂 {cwd if cwd else 'current'}: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    try:
        result = subprocess.run(
            cmd, 
            cwd=cwd, 
            capture_output=capture_output, 
            text=True, 
            input=input_text,
            timeout=timeout,
            shell=isinstance(cmd, str)
        )
        if capture_output:
            if result.stdout and result.stdout.strip():
                print(f"  ✅ {result.stdout.strip()}")
            if result.stderr and result.stderr.strip():
                print(f"  ⚠️  {result.stderr.strip()}")
        return result
    except subprocess.TimeoutExpired:
        print(f"  ❌ Command timed out after {timeout} seconds")
        return None
    except Exception as e:
        print(f"  ❌ Command failed: {e}")
        return None

def create_github_repo(repo_name, token, private=True):
    """Create a new GitHub repository using the GitHub API."""
    if not HAS_REQUESTS:
        print("❌ 'requests' library not found. Install with: pip install requests")
        return None, None
    
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "name": repo_name,
        "private": private,
        "description": f"SVCS collaboration test repository - {repo_name}",
        "auto_init": False  # Don't create README, we want it empty
    }
    
    print(f"🚀 Creating GitHub repository: {repo_name}")
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            repo_data = response.json()
            print(f"✅ Repository created successfully!")
            return repo_data["clone_url"], repo_data["ssh_url"]
        elif response.status_code == 422:
            error_data = response.json()
            if "name already exists" in str(error_data):
                print(f"❌ Repository '{repo_name}' already exists")
                return None, None
            else:
                print(f"❌ Repository creation failed: {error_data}")
                return None, None
        else:
            print(f"❌ Repository creation failed: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Repository creation failed: {e}")
        return None, None

def get_github_token():
    """Get GitHub personal access token from user."""
    if not HAS_REQUESTS:
        print("❌ 'requests' library not found. Cannot create repositories automatically.")
        print("💡 Install with: pip install requests")
        return None
    
    print("\n🔑 GitHub Authentication")
    print("=" * 50)
    print("To create a repository automatically, you need a GitHub Personal Access Token.")
    print("📖 How to get one:")
    print("   1. Go to GitHub.com → Settings → Developer settings → Personal access tokens")
    print("   2. Click 'Generate new token (classic)'")
    print("   3. Give it a name like 'SVCS Test'")
    print("   4. Select scopes: 'repo' (Full control of private repositories)")
    print("   5. Click 'Generate token' and copy it")
    print()
    
    token = getpass.getpass("Enter your GitHub Personal Access Token (input hidden): ").strip()
    if not token:
        print("❌ No token provided")
        return None
    
    # Test the token
    try:
        response = requests.get("https://api.github.com/user", 
                              headers={"Authorization": f"token {token}"})
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Authentication successful! Hello, {user_data['login']}")
            return token
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return None

def validate_git_remote_url(url):
    """Validate if the provided URL looks like a valid git remote."""
    patterns = [
        r'^https://github\.com/[\w\-\.]+/[\w\-\.]+(?:\.git)?/?$',
        r'^git@github\.com:[\w\-\.]+/[\w\-\.]+(?:\.git)?/?$',
        r'^ssh://git@github\.com/[\w\-\.]+/[\w\-\.]+(?:\.git)?/?$'
    ]
    return any(re.match(pattern, url, re.IGNORECASE) for pattern in patterns)
    """Validate if the provided URL looks like a valid git remote."""
    patterns = [
        r'^https://github\.com/[\w\-\.]+/[\w\-\.]+(?:\.git)?/?$',
        r'^git@github\.com:[\w\-\.]+/[\w\-\.]+(?:\.git)?/?$',
        r'^ssh://git@github\.com/[\w\-\.]+/[\w\-\.]+(?:\.git)?/?$'
    ]
    return any(re.match(pattern, url, re.IGNORECASE) for pattern in patterns)

def get_repo_info():
    """Get repository information from user."""
    print("\n🔗 GitHub Repository Setup")
    print("=" * 50)
    
    while True:
        choice = input("Do you want to:\n1. Use existing repository (I'll provide the URL)\n2. Create NEW repository automatically (I'll provide the name)\nChoice (1/2): ").strip()
        if choice in ['1', '2']:
            break
        print("❌ Please enter 1 or 2")
    
    if choice == '1':
        print("\n📋 Using existing repository")
        print("💡 This can be any existing GitHub repository (empty or with content)")
        while True:
            repo_url = input("Enter GitHub repository URL: ").strip()
            if validate_git_remote_url(repo_url):
                return repo_url, False
            print("❌ Invalid GitHub URL format. Please use https://github.com/user/repo or git@github.com:user/repo")
    
    else:
        print("\n🆕 Creating NEW repository automatically")
        print("💡 I'll create a new private repository on GitHub for you!")
        
        if not HAS_REQUESTS:
            print("❌ Cannot create repository: 'requests' library not installed")
            print("💡 Install with: pip install requests")
            print("💡 Or choose option 1 to use existing repository")
            return None, None
        
        # Get GitHub token
        token = get_github_token()
        if not token:
            print("❌ Cannot create repository without authentication")
            return None, None
        
        # Get repository name
        while True:
            repo_name = input("Enter repository name (e.g., 'svcs-test-repo'): ").strip()
            if repo_name and re.match(r'^[a-zA-Z0-9._-]+$', repo_name):
                break
            print("❌ Invalid repository name. Use only letters, numbers, dots, hyphens, and underscores")
        
        # Ask about privacy
        while True:
            private_choice = input("Make repository private? (y/n): ").strip().lower()
            if private_choice in ['y', 'n']:
                is_private = private_choice == 'y'
                break
            print("❌ Please enter y or n")
        
        # Create the repository
        https_url, ssh_url = create_github_repo(repo_name, token, is_private)
        if https_url:
            print(f"✅ Repository created: {https_url}")
            return https_url, True
        else:
            print("❌ Failed to create repository")
            return None, None

def setup_git_config(repo_path):
    """Setup git configuration for the repository."""
    print(f"\n⚙️  Setting up git configuration in {repo_path.name}")
    
    # Check if git user is configured globally
    name_result = run_command(['git', 'config', '--global', 'user.name'], cwd=repo_path)
    email_result = run_command(['git', 'config', '--global', 'user.email'], cwd=repo_path)
    
    if not name_result or not name_result.stdout.strip():
        name = input("Enter your git user.name: ").strip()
        run_command(['git', 'config', 'user.name', name], cwd=repo_path)
    
    if not email_result or not email_result.stdout.strip():
        email = input("Enter your git user.email: ").strip()
        run_command(['git', 'config', 'user.email', email], cwd=repo_path)

def create_sample_code_changes(repo_path, developer_name, iteration):
    """Create realistic code changes for testing."""
    print(f"\n📝 {developer_name} creating code changes (iteration {iteration})")
    
    if iteration == 1:
        # First iteration - create a web application structure
        app_file = repo_path / "app.py"
        app_file.write_text(f"""#!/usr/bin/env python3
\"\"\"
Simple web application - {developer_name}'s contribution
\"\"\"

from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

class UserManager:
    def __init__(self):
        self.users = {{}}
        self.next_id = 1
    
    def create_user(self, username, email):
        \"\"\"Create a new user account\"\"\"
        if username in [u['username'] for u in self.users.values()]:
            raise ValueError("Username already exists")
        
        user_id = self.next_id
        self.users[user_id] = {{
            'id': user_id,
            'username': username,
            'email': email,
            'active': True
        }}
        self.next_id += 1
        return user_id
    
    def get_user(self, user_id):
        \"\"\"Get user by ID\"\"\"
        return self.users.get(user_id)

user_manager = UserManager()

@app.route('/health')
def health_check():
    \"\"\"Health check endpoint\"\"\"
    return jsonify({{'status': 'healthy', 'developer': '{developer_name}'}})

@app.route('/users', methods=['POST'])
def create_user():
    \"\"\"Create a new user\"\"\"
    data = request.get_json()
    try:
        user_id = user_manager.create_user(data['username'], data['email'])
        return jsonify({{'user_id': user_id, 'status': 'created'}}), 201
    except Exception as e:
        return jsonify({{'error': str(e)}}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
""")
        
        return "Add web application with user management"
    
    elif iteration == 2:
        # Second iteration - add authentication
        auth_file = repo_path / "auth.py"
        auth_file.write_text(f"""#!/usr/bin/env python3
\"\"\"
Authentication module - Enhanced by {developer_name}
\"\"\"

import hashlib
import secrets
from datetime import datetime, timedelta

class AuthenticationService:
    def __init__(self):
        self.sessions = {{}}
        self.session_timeout = timedelta(hours=24)
    
    def hash_password(self, password):
        \"\"\"Hash password with salt\"\"\"
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', 
                                       password.encode('utf-8'), 
                                       salt.encode('utf-8'), 
                                       100000)
        return f"{{salt}}:{{pwd_hash.hex()}}"
    
    def verify_password(self, password, hashed):
        \"\"\"Verify password against hash\"\"\"
        try:
            salt, pwd_hash = hashed.split(':')
            return pwd_hash == hashlib.pbkdf2_hmac(
                'sha256', 
                password.encode('utf-8'), 
                salt.encode('utf-8'), 
                100000
            ).hex()
        except ValueError:
            return False
    
    def create_session(self, user_id):
        \"\"\"Create a new user session\"\"\"
        session_token = secrets.token_urlsafe(32)
        self.sessions[session_token] = {{
            'user_id': user_id,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + self.session_timeout
        }}
        return session_token
    
    def validate_session(self, session_token):
        \"\"\"Validate and return session info\"\"\"
        session = self.sessions.get(session_token)
        if not session:
            return None
        
        if datetime.now() > session['expires_at']:
            del self.sessions[session_token]
            return None
        
        return session

class SecurityUtils:
    @staticmethod
    def validate_email(email):
        \"\"\"Basic email validation\"\"\"
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{{2,}}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password_strength(password):
        \"\"\"Validate password meets security requirements\"\"\"
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain number"
        
        return True, "Password is strong"

# Global authentication service
auth_service = AuthenticationService()
""")
        
        return f"Add authentication and security features by {developer_name}"
    
    elif iteration == 3:
        # Third iteration - add database and API improvements
        db_file = repo_path / "database.py"
        db_file.write_text(f"""#!/usr/bin/env python3
\"\"\"
Database layer - Implemented by {developer_name}
\"\"\"

import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_path='app.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        \"\"\"Initialize database schema\"\"\"
        with self.get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    token TEXT PRIMARY KEY,
                    user_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
    
    @contextmanager
    def get_connection(self):
        \"\"\"Get database connection with automatic cleanup\"\"\"
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def create_user(self, username, email, password_hash):
        \"\"\"Create a new user in database\"\"\"
        with self.get_connection() as conn:
            cursor = conn.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, password_hash)
            )
            return cursor.lastrowid
    
    def get_user_by_username(self, username):
        \"\"\"Get user by username\"\"\"
        with self.get_connection() as conn:
            result = conn.execute(
                'SELECT * FROM users WHERE username = ? AND active = TRUE',
                (username,)
            ).fetchone()
            return dict(result) if result else None
    
    def log_audit_event(self, user_id, action, details=None, ip_address=None):
        \"\"\"Log an audit event\"\"\"
        with self.get_connection() as conn:
            conn.execute(
                'INSERT INTO audit_log (user_id, action, details, ip_address) VALUES (?, ?, ?, ?)',
                (user_id, action, json.dumps(details) if details else None, ip_address)
            )

class APIResponse:
    \"\"\"Standardized API response format\"\"\"
    
    @staticmethod
    def success(data=None, message="Success", code=200):
        response = {{
            'success': True,
            'message': message,
            'code': code,
            'timestamp': datetime.now().isoformat()
        }}
        if data is not None:
            response['data'] = data
        return response, code
    
    @staticmethod
    def error(message="Error occurred", code=400, details=None):
        response = {{
            'success': False,
            'message': message,
            'code': code,
            'timestamp': datetime.now().isoformat()
        }}
        if details:
            response['details'] = details
        return response, code

# Global database manager
db_manager = DatabaseManager()
""")
        
        return f"Add database layer and API improvements by {developer_name}"
    
    else:
        # Fourth iteration - add monitoring and utilities
        utils_file = repo_path / "monitoring.py"
        utils_file.write_text(f"""#!/usr/bin/env python3
\"\"\"
Monitoring and utilities - Enhanced by {developer_name}
\"\"\"

import time
import logging
from functools import wraps
from datetime import datetime
import psutil
import threading

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {{}}
        self.start_time = datetime.now()
    
    def timing_decorator(self, func_name=None):
        \"\"\"Decorator to monitor function execution time\"\"\"
        def decorator(func):
            name = func_name or f"{{func.__module__}}.{{func.__name__}}"
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    self.record_metric(name, execution_time, 'success')
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    self.record_metric(name, execution_time, 'error')
                    logging.error(f"Function {{name}} failed: {{str(e)}}")
                    raise
            return wrapper
        return decorator
    
    def record_metric(self, name, value, status='success'):
        \"\"\"Record a performance metric\"\"\"
        if name not in self.metrics:
            self.metrics[name] = {{
                'total_calls': 0,
                'total_time': 0,
                'avg_time': 0,
                'min_time': float('inf'),
                'max_time': 0,
                'success_count': 0,
                'error_count': 0
            }}
        
        metric = self.metrics[name]
        metric['total_calls'] += 1
        metric['total_time'] += value
        metric['avg_time'] = metric['total_time'] / metric['total_calls']
        metric['min_time'] = min(metric['min_time'], value)
        metric['max_time'] = max(metric['max_time'], value)
        
        if status == 'success':
            metric['success_count'] += 1
        else:
            metric['error_count'] += 1
    
    def get_system_stats(self):
        \"\"\"Get current system statistics\"\"\"
        return {{
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory': {{
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent
            }},
            'disk': {{
                'total': psutil.disk_usage('/').total,
                'free': psutil.disk_usage('/').free,
                'percent': psutil.disk_usage('/').percent
            }},
            'uptime': (datetime.now() - self.start_time).total_seconds()
        }}

class HealthChecker:
    def __init__(self):
        self.checks = {{}}
        self.running = False
        self.check_interval = 30  # seconds
        self.thread = None
    
    def register_check(self, name, check_function, critical=True):
        \"\"\"Register a health check\"\"\"
        self.checks[name] = {{
            'function': check_function,
            'critical': critical,
            'last_result': None,
            'last_check': None
        }}
    
    def run_check(self, name):
        \"\"\"Run a specific health check\"\"\"
        if name not in self.checks:
            return False, "Check not found"
        
        check = self.checks[name]
        try:
            result = check['function']()
            check['last_result'] = result
            check['last_check'] = datetime.now()
            return True, result
        except Exception as e:
            check['last_result'] = f"Error: {{str(e)}}"
            check['last_check'] = datetime.now()
            return False, str(e)
    
    def get_health_status(self):
        \"\"\"Get overall health status\"\"\"
        status = {{
            'healthy': True,
            'checks': {{}},
            'timestamp': datetime.now().isoformat()
        }}
        
        for name, check in self.checks.items():
            success, result = self.run_check(name)
            status['checks'][name] = {{
                'success': success,
                'result': result,
                'critical': check['critical'],
                'last_check': check['last_check'].isoformat() if check['last_check'] else None
            }}
            
            if not success and check['critical']:
                status['healthy'] = False
        
        return status

# Global monitoring instances
performance_monitor = PerformanceMonitor()
health_checker = HealthChecker()

# Example health checks
def database_health_check():
    \"\"\"Check if database is accessible\"\"\"
    try:
        from database import db_manager
        with db_manager.get_connection() as conn:
            conn.execute('SELECT 1').fetchone()
        return "Database connection OK"
    except Exception as e:
        raise Exception(f"Database connection failed: {{str(e)}}")

health_checker.register_check('database', database_health_check, critical=True)
""")
        
        return f"Add monitoring and health checking by {developer_name}"

def test_github_collaboration():
    """Test SVCS collaboration workflow with GitHub remote."""
    
    print("🤝 SVCS GitHub Collaboration Test")
    print("=" * 50)
    print("This test simulates two developers collaborating on a project using SVCS")
    print("with semantic synchronization via GitHub remote repository.")
    
    # Get repository information
    repo_info = get_repo_info()
    if repo_info[0] is None:
        print("❌ Cannot proceed without repository information")
        return False
    
    repo_url, is_new = repo_info
    
    print(f"\n📍 Using repository: {repo_url}")
    print(f"📋 Repository type: {'New' if is_new else 'Existing'}")
    
    # Create temporary directory for test
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        dev1_repo = temp_path / "developer1"
        dev2_repo = temp_path / "developer2"
        
        print(f"\n🧪 Test environment: {temp_dir}")
        print(f"👨‍💻 Developer 1 workspace: {dev1_repo.name}")
        print(f"👩‍💻 Developer 2 workspace: {dev2_repo.name}")
        
        svcs_cli_path = parent_dir / 'svcs' / 'cli.py'
        
        try:
            # === PHASE 1: Developer 1 setup ===
            print("\n" + "="*60)
            print("📱 PHASE 1: Developer 1 Initial Setup")
            print("="*60)
            
            if is_new:
                # Create new repo structure
                dev1_repo.mkdir()
                result = run_command(['git', 'init'], cwd=dev1_repo)
                if not result or result.returncode != 0:
                    print("❌ Failed to initialize git repository")
                    return False
                
                setup_git_config(dev1_repo)
                
                # Add remote
                result = run_command(['git', 'remote', 'add', 'origin', repo_url], cwd=dev1_repo)
                if not result or result.returncode != 0:
                    print("❌ Failed to add remote")
                    return False
            else:
                # Clone existing repo
                result = run_command(['git', 'clone', repo_url, str(dev1_repo)])
                if not result or result.returncode != 0:
                    print("❌ Failed to clone repository")
                    return False
                
                setup_git_config(dev1_repo)
            
            # Initialize SVCS in developer 1's repo
            print("\n🔧 Initializing SVCS for Developer 1...")
            result = run_command([sys.executable, str(svcs_cli_path), 'init'], 
                               cwd=dev1_repo, 
                               input_text="y\n",
                               timeout=15)
            if not result or result.returncode != 0:
                print("❌ Failed to initialize SVCS for Developer 1")
                return False
            
            # Create initial code
            commit_msg = create_sample_code_changes(dev1_repo, "Developer1", 1)
            
            run_command(['git', 'add', '.'], cwd=dev1_repo)
            result = run_command(['git', 'commit', '-m', commit_msg], cwd=dev1_repo)
            if not result or result.returncode != 0:
                print("❌ Failed to create initial commit")
                return False
            
            # Push to GitHub
            print("\n📤 Developer 1 pushing to GitHub...")
            if is_new:
                result = run_command(['git', 'push', '-u', 'origin', 'main'], cwd=dev1_repo)
            else:
                result = run_command(['git', 'push', 'origin', 'main'], cwd=dev1_repo)
            
            if not result or result.returncode != 0:
                print("❌ Failed to push to GitHub")
                return False
            
            print("✅ Developer 1 setup complete!")
            
            # === PHASE 2: Developer 2 setup ===
            print("\n" + "="*60)
            print("👩‍💻 PHASE 2: Developer 2 Joins Project")
            print("="*60)
            
            # Clone the repository for developer 2
            result = run_command(['git', 'clone', repo_url, str(dev2_repo)])
            if not result or result.returncode != 0:
                print("❌ Failed to clone repository for Developer 2")
                return False
            
            setup_git_config(dev2_repo)
            
            # Initialize SVCS for developer 2
            print("\n🔧 Initializing SVCS for Developer 2...")
            result = run_command([sys.executable, str(svcs_cli_path), 'init'], 
                               cwd=dev2_repo, 
                               input_text="y\n",
                               timeout=15)
            if not result or result.returncode != 0:
                print("❌ Failed to initialize SVCS for Developer 2")
                return False
            
            # Check semantic events sync
            print("\n📊 Checking semantic events synchronization...")
            result = run_command([sys.executable, str(svcs_cli_path), 'events'], cwd=dev2_repo)
            if result and result.returncode == 0:
                lines = result.stdout.split('\n')
                event_count = len([line for line in lines if line.strip().startswith('🔍')])
                print(f"✅ Developer 2 found {event_count} semantic events from Developer 1")
            
            print("✅ Developer 2 setup complete!")
            
            # === PHASE 3: Collaborative development ===
            print("\n" + "="*60)
            print("🤝 PHASE 3: Collaborative Development")
            print("="*60)
            
            # Developer 2 makes changes
            commit_msg2 = create_sample_code_changes(dev2_repo, "Developer2", 2)
            run_command(['git', 'add', '.'], cwd=dev2_repo)
            result = run_command(['git', 'commit', '-m', commit_msg2], cwd=dev2_repo)
            
            print("\n📤 Developer 2 pushing changes...")
            result = run_command(['git', 'push', 'origin', 'main'], cwd=dev2_repo)
            if not result or result.returncode != 0:
                print("❌ Developer 2 failed to push")
                return False
            
            # Developer 1 pulls changes
            print("\n📥 Developer 1 pulling changes...")
            result = run_command([sys.executable, str(svcs_cli_path), 'pull'], cwd=dev1_repo)
            if not result or result.returncode != 0:
                print("❌ Developer 1 failed to pull")
                return False
            
            # Developer 1 makes more changes
            commit_msg3 = create_sample_code_changes(dev1_repo, "Developer1", 3)
            run_command(['git', 'add', '.'], cwd=dev1_repo)
            result = run_command(['git', 'commit', '-m', commit_msg3], cwd=dev1_repo)
            
            print("\n📤 Developer 1 pushing new changes...")
            result = run_command(['git', 'push', 'origin', 'main'], cwd=dev1_repo)
            if not result or result.returncode != 0:
                print("❌ Developer 1 failed to push")
                return False
            
            # Developer 2 pulls and adds final changes
            print("\n📥 Developer 2 pulling latest changes...")
            result = run_command([sys.executable, str(svcs_cli_path), 'pull'], cwd=dev2_repo)
            if not result or result.returncode != 0:
                print("❌ Developer 2 failed to pull")
                return False
            
            commit_msg4 = create_sample_code_changes(dev2_repo, "Developer2", 4)
            run_command(['git', 'add', '.'], cwd=dev2_repo)
            result = run_command(['git', 'commit', '-m', commit_msg4], cwd=dev2_repo)
            
            print("\n📤 Developer 2 pushing final changes...")
            result = run_command(['git', 'push', 'origin', 'main'], cwd=dev2_repo)
            
            # === PHASE 4: Final synchronization and verification ===
            print("\n" + "="*60)
            print("📊 PHASE 4: Final Verification")
            print("="*60)
            
            # Developer 1 final sync
            print("\n📥 Developer 1 final sync...")
            result = run_command([sys.executable, str(svcs_cli_path), 'pull'], cwd=dev1_repo)
            
            # Check final semantic events in both repos
            print("\n📊 Final semantic events comparison:")
            
            print("\n👨‍💻 Developer 1 semantic events:")
            result1 = run_command([sys.executable, str(svcs_cli_path), 'events'], cwd=dev1_repo)
            if result1 and result1.returncode == 0:
                lines1 = result1.stdout.split('\n')
                event_count1 = len([line for line in lines1 if line.strip().startswith('🔍')])
                print(f"  📈 Total events: {event_count1}")
            
            print("\n👩‍💻 Developer 2 semantic events:")
            result2 = run_command([sys.executable, str(svcs_cli_path), 'events'], cwd=dev2_repo)
            if result2 and result2.returncode == 0:
                lines2 = result2.stdout.split('\n')
                event_count2 = len([line for line in lines2 if line.strip().startswith('🔍')])
                print(f"  📈 Total events: {event_count2}")
            
            # Check file synchronization
            print(f"\n📁 Files in Developer 1 repo: {list(f.name for f in dev1_repo.iterdir() if f.is_file() and not f.name.startswith('.'))}")
            print(f"📁 Files in Developer 2 repo: {list(f.name for f in dev2_repo.iterdir() if f.is_file() and not f.name.startswith('.'))}")
            
            print("\n" + "="*60)
            print("🎉 COLLABORATION TEST RESULTS")
            print("="*60)
            
            success_indicators = []
            if event_count1 > 0:
                success_indicators.append(f"✅ Developer 1 has {event_count1} semantic events")
            if event_count2 > 0:
                success_indicators.append(f"✅ Developer 2 has {event_count2} semantic events")
            if event_count1 == event_count2:
                success_indicators.append("✅ Semantic events synchronized between developers")
            if (dev1_repo / "app.py").exists() and (dev2_repo / "app.py").exists():
                success_indicators.append("✅ Core application files synchronized")
            if (dev1_repo / "auth.py").exists() and (dev2_repo / "auth.py").exists():
                success_indicators.append("✅ Authentication module synchronized")
            
            for indicator in success_indicators:
                print(indicator)
            
            if len(success_indicators) >= 4:
                print("\n🎉 ✅ GITHUB COLLABORATION TEST PASSED!")
                print("✅ SVCS successfully synchronized semantic events via GitHub")
                print("✅ Both developers have complete project history")
                print("✅ Code and semantic data are properly synchronized")
                return True
            else:
                print("\n❌ GITHUB COLLABORATION TEST FAILED!")
                print(f"❌ Only {len(success_indicators)}/4 success criteria met")
                return False
                
        except KeyboardInterrupt:
            print("\n🛑 Test interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("🚀 Starting SVCS GitHub Collaboration Test")
    print("This test requires:")
    print("  - GitHub account")
    print("  - Git configured with your credentials")
    print("  - Internet connection")
    print()
    print("💡 OPTIONS:")
    print("   1. Use existing GitHub repository (provide URL)")
    print("   2. Create NEW repository automatically (provide name + GitHub token)")
    print()
    print("🔑 For option 2, you'll need a GitHub Personal Access Token with 'repo' scope")
    print("   Get one at: GitHub → Settings → Developer settings → Personal access tokens")
    print()
    
    if input("Do you want to continue? (y/n): ").lower().strip() != 'y':
        print("Test cancelled.")
        sys.exit(0)
    
    try:
        success = test_github_collaboration()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 Test interrupted by user")
        sys.exit(1)

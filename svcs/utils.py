#!/usr/bin/env python3
"""
SVCS Utilities Module
Shared utility functions for SVCS CLI and commands

This module contains utility functions that are shared across multiple
SVCS modules to avoid duplication and improve maintainability.
"""

import os
import shutil
import sys
from pathlib import Path
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any


def find_svcs_files():
    """Find SVCS installation files."""
    svcs_files = ['svcs_repo_local.py', 'svcs_repo_analyzer.py', 'svcs_multilang.py']
    
    # Check environment variable first (set by global installation)
    install_dir = os.environ.get('SVCS_INSTALL_DIR')
    if install_dir:
        install_path = Path(install_dir)
        if all((install_path / f).exists() for f in svcs_files):
            return install_path
    
    # Check if we're in development mode (files in current directory)
    current_dir = Path(__file__).parent.parent  # Go up from svcs/utils.py to main directory
    
    # Check main directory first (development mode)
    if all((current_dir / f).exists() for f in svcs_files):
        return current_dir
    
    # Check parent directory of this script
    script_dir = Path(__file__).parent.parent
    if all((script_dir / f).exists() for f in svcs_files):
        return script_dir
    
    # Check if installed as package
    try:
        import svcs
        package_dir = Path(svcs.__file__).parent.parent
        if all((package_dir / f).exists() for f in svcs_files):
            return package_dir
    except ImportError:
        pass
    
    return None


def setup_repository_files(repo_path: Path):
    """Set up SVCS files in repository (user-friendly installation)."""
    svcs_dir = repo_path / '.svcs'
    svcs_dir.mkdir(exist_ok=True)
    
    # Find SVCS installation
    source_dir = find_svcs_files()
    if not source_dir:
        print("❌ Error: SVCS installation files not found.")
        print("   Please ensure SVCS is properly installed.")
        return False
    
    # Copy essential SVCS files to .svcs directory
    essential_files = [
        'svcs_repo_local.py',
        'svcs_repo_analyzer.py', 
        'svcs_multilang.py'
    ]
    
    for file in essential_files:
        src = source_dir / file
        dst = svcs_dir / file
        if src.exists():
            shutil.copy2(src, dst)
            print(f"📄 Installed {file}")
        else:
            print(f"⚠️ Warning: {file} not found in installation")
    
    # Copy analyzer if it exists
    analyzer_src = source_dir / 'analyzer.py'
    analyzer_dst = svcs_dir / 'analyzer.py'
    if analyzer_src.exists():
        shutil.copy2(analyzer_src, analyzer_dst)
        print("📄 Installed analyzer.py")
    elif (source_dir / '.svcs' / 'analyzer.py').exists():
        shutil.copy2(source_dir / '.svcs' / 'analyzer.py', analyzer_dst)
        print("📄 Installed analyzer.py")
    
    # Copy API module if it exists (for search/evolution functionality)
    api_src = source_dir / '.svcs' / 'api.py'
    api_dst = svcs_dir / 'api.py'
    if api_src.exists():
        shutil.copy2(api_src, api_dst)
        print("📄 Installed api.py")
        
        # Create a compatibility shim for database naming
        compat_content = '''#!/usr/bin/env python3
# API Compatibility Layer for Repository-Local SVCS
import os
import sys

# Update database path to match repository-local naming
original_db_path = os.path.join(".svcs", "history.db")
repo_local_db_path = os.path.join(".svcs", "semantic.db")

# Monkey patch the API module to use the correct database
if os.path.exists("api.py"):
    with open("api.py", "r") as f:
        api_content = f.read()
    
    # Replace database references
    api_content = api_content.replace('DB_PATH = os.path.join(SVCS_DIR, "history.db")', 
                                    'DB_PATH = os.path.join(SVCS_DIR, "semantic.db")')
    
    with open("api.py", "w") as f:
        f.write(api_content)
'''
        
        # Apply compatibility fix
        try:
            exec(compat_content)
            print("📄 Applied API compatibility fixes")
        except Exception as e:
            print(f"⚠️ Warning: Could not apply API compatibility fixes: {e}")
    else:
        print("⚠️ Warning: api.py not found - search/evolution features may not work")
    
    return True


def validate_repository(repo_path: Path):
    """Validate that the given path is a git repository with SVCS initialized."""
    if not (repo_path / '.git').exists():
        return False, "Not a git repository"
    
    if not (repo_path / '.svcs' / 'semantic.db').exists():
        return False, "SVCS not initialized"
    
    return True, "Valid SVCS repository"


def get_current_branch(repo_path: Path):
    """Get the current git branch."""
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return 'main'  # fallback


def format_timestamp(timestamp):
    """Format timestamp for display."""
    from datetime import datetime
    if isinstance(timestamp, (int, float)):
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(timestamp, str) and len(timestamp) > 19:
        return timestamp[:19]
    return str(timestamp)


def print_event(event, include_reasoning=True):
    """Print a semantic event in a standardized format."""
    timestamp = format_timestamp(event.get('created_at', event.get('timestamp', '')))
    
    confidence = event.get('confidence', 1.0)
    confidence_str = f" ({confidence:.1%})" if confidence < 1.0 else ""
    
    print(f"🔍 {event['event_type']}{confidence_str}")
    print(f"   📝 {event.get('commit_hash', 'N/A')[:8]} | {event.get('branch', 'N/A')} | {timestamp}")
    print(f"   🎯 {event.get('node_id', 'N/A')} @ {event.get('location', 'N/A')}")
    
    if 'details' in event:
        print(f"   💬 {event['details']}")
    
    if include_reasoning and 'reasoning' in event:
        print(f"   🧠 {event['reasoning']}")
    
    print()


def handle_import_error(module_name, suggestion=""):
    """Handle import errors with helpful messages."""
    print(f"❌ Error: {module_name} not available.")
    if suggestion:
        print(f"   {suggestion}")
    return False


def safe_json_dump(data, filepath, indent=2):
    """Safely write JSON data to file."""
    try:
        import json
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=indent)
        return True
    except Exception as e:
        print(f"❌ Error writing to {filepath}: {e}")
        return False


def smart_init_svcs(repo_path: Path):
    """Smart SVCS initialization with auto-detection."""
    import subprocess
    
    git_exists = (repo_path / '.git').exists()
    svcs_exists = (repo_path / '.svcs').exists()
    has_files = any(repo_path.iterdir()) if repo_path.exists() else False
    
    # Check if SVCS already initialized
    if svcs_exists:
        return "✅ SVCS already initialized. Use 'svcs status' to check repository status."
    
    # If git exists, proceed with SVCS initialization
    if git_exists:
        return init_svcs_centralized(repo_path)
    
    # If directory is empty, auto-initialize both git and SVCS
    if not has_files:
        print(f"📁 Empty directory detected. Initializing git repository and SVCS...")
        try:
            subprocess.run(['git', 'init'], cwd=repo_path, check=True, capture_output=True)
            print("✅ Git repository initialized")
            return init_svcs_centralized(repo_path)
        except subprocess.CalledProcessError as e:
            return f"❌ Error: Failed to initialize git repository: {e}"
    
    # Directory has files but no git - prompt user
    print("📁 Directory contains files but no git repository.")
    response = input("Initialize git repository? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        try:
            subprocess.run(['git', 'init'], cwd=repo_path, check=True, capture_output=True)
            print("✅ Git repository initialized")
            return init_svcs_centralized(repo_path)
        except subprocess.CalledProcessError as e:
            return f"❌ Error: Failed to initialize git repository: {e}"
    else:
        return "❌ SVCS requires a git repository. Please run 'git init' first, then 'svcs init'."


def init_svcs_centralized(repo_path: Path):
    """Initialize SVCS with centralized architecture (no file copying)."""
    svcs_dir = repo_path / '.svcs'
    svcs_dir.mkdir(exist_ok=True)
    
    print(f"🔧 Initializing SVCS for repository: {repo_path}")
    
    # Create minimal local configuration instead of copying files
    config = {
        "svcs_version": "1.0.0",
        "initialized": True,
        "centralized": True,
        "database_path": ".svcs/semantic.db"
    }
    
    import json
    config_path = svcs_dir / 'config.json'
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print("📄 Created SVCS configuration")
    
    # Set up centralized git hooks (reference global installation)
    if not setup_centralized_git_hooks(repo_path):
        return "❌ Failed to set up git hooks"
    
    # Initialize using the repository manager
    try:
        from svcs_repo_hooks import SVCSRepositoryManager
        manager = SVCSRepositoryManager(str(repo_path))
        result = manager.setup_repository()
        return f"✅ SVCS initialized with centralized architecture\n{result}"
    except Exception as e:
        return f"❌ Error during SVCS initialization: {e}"


def setup_centralized_git_hooks(repo_path: Path):
    """Set up git hooks that reference centralized SVCS installation."""
    hooks_dir = repo_path / '.git' / 'hooks'
    hooks_dir.mkdir(exist_ok=True)
    
    # Get path to centralized SVCS installation
    try:
        import subprocess
        import sys
        
        # Try to find svcs command in PATH
        try:
            svcs_cmd = subprocess.run(['which', 'svcs'], capture_output=True, text=True, check=True)
            svcs_path = svcs_cmd.stdout.strip()
        except:
            # Fallback to python module execution
            svcs_path = f"{sys.executable} -m svcs.cli"
        
        # Hook template that calls centralized SVCS
        hook_template = f"""#!/bin/bash
# SVCS Git Hook - Centralized Version
# This hook calls the centralized SVCS installation

{svcs_path} process-hook "$0" "$@"
"""
        
        # Install hooks
        hooks_to_install = ['post-commit', 'post-merge', 'post-checkout', 'pre-push']
        installed_hooks = []
        
        for hook_name in hooks_to_install:
            hook_path = hooks_dir / hook_name
            hook_path.write_text(hook_template)
            hook_path.chmod(0o755)  # Make executable
            installed_hooks.append(hook_name)
        
        print(f"✅ Installed centralized git hooks: {', '.join(installed_hooks)}")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up git hooks: {e}")
        return False


def migrate_legacy_installation(repo_path: Path):
    """Migrate from legacy file-copy installation to centralized architecture."""
    svcs_dir = repo_path / '.svcs'
    
    if not svcs_dir.exists():
        return False
    
    # Check if this is a legacy installation (has copied Python files)
    legacy_files = ['svcs_repo_local.py', 'svcs_repo_analyzer.py', 'svcs_multilang.py']
    has_legacy_files = any((svcs_dir / f).exists() for f in legacy_files)
    
    if not has_legacy_files:
        return False
    
    print("🔄 Legacy SVCS installation detected.")
    response = input("Migrate to centralized version? This will remove local copies but preserve your data. (y/n): ").lower().strip()
    
    if response not in ['y', 'yes']:
        return False
    
    # Backup semantic database
    db_path = svcs_dir / 'semantic.db'
    if db_path.exists():
        backup_path = svcs_dir / 'semantic.db.backup'
        import shutil
        shutil.copy2(db_path, backup_path)
        print("📦 Backed up semantic database")
    
    # Remove legacy files
    for file in legacy_files + ['analyzer.py', 'api.py']:
        file_path = svcs_dir / file
        if file_path.exists():
            file_path.unlink()
            print(f"🗑️ Removed {file}")
    
    # Initialize centralized version
    result = init_svcs_centralized(repo_path)
    print("✅ Migration completed successfully")
    return True


def init_database():
    """Initialize SVCS database for storing semantic events."""
    db_path = get_database_path()
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Create semantic events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS semantic_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                node_id TEXT NOT NULL,
                location TEXT NOT NULL,
                details TEXT,
                confidence REAL DEFAULT 1.0,
                layer TEXT DEFAULT 'core',
                additional_data TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                commit_hash TEXT
            )
        ''')
        
        # Create index for better query performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_event_type ON semantic_events(event_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_location ON semantic_events(location)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON semantic_events(timestamp)')
        
        conn.commit()


def get_database_path():
    """Get the path to the SVCS database."""
    return Path.cwd() / '.svcs' / 'semantic_events.db'


def store_events(events: List[Dict[str, Any]]):
    """Store semantic events in the database."""
    if not events:
        return
    
    db_path = get_database_path()
    
    # Ensure .svcs directory exists
    db_path.parent.mkdir(exist_ok=True)
    
    # Get current commit hash
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True,
            text=True
        )
        commit_hash = result.stdout.strip() if result.returncode == 0 else None
    except:
        commit_hash = None
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        for event in events:
            cursor.execute('''
                INSERT INTO semantic_events 
                (event_type, node_id, location, details, confidence, layer, additional_data, commit_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.get('event_type'),
                event.get('node_id'),
                event.get('location'),
                event.get('details'),
                event.get('confidence', 1.0),
                event.get('layer', 'core'),
                json.dumps(event.get('additional_data', {})),
                commit_hash
            ))
        
        conn.commit()


def get_recent_events(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent semantic events from the database."""
    db_path = get_database_path()
    
    if not db_path.exists():
        return []
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT event_type, node_id, location, details, confidence, layer, 
                   additional_data, timestamp, commit_hash
            FROM semantic_events 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        
        events = []
        for row in rows:
            event = {
                'event_type': row[0],
                'node_id': row[1],
                'location': row[2],
                'details': row[3],
                'confidence': row[4],
                'layer': row[5],
                'additional_data': json.loads(row[6]) if row[6] else {},
                'timestamp': row[7],
                'commit_hash': row[8]
            }
            events.append(event)
        
        return events


def get_event_statistics() -> Dict[str, Any]:
    """Get statistics about semantic events."""
    db_path = get_database_path()
    
    if not db_path.exists():
        return {}
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Total events
        cursor.execute('SELECT COUNT(*) FROM semantic_events')
        total_events = cursor.fetchone()[0]
        
        # Events by type
        cursor.execute('''
            SELECT event_type, COUNT(*) 
            FROM semantic_events 
            GROUP BY event_type 
            ORDER BY COUNT(*) DESC
        ''')
        events_by_type = dict(cursor.fetchall())
        
        # Events by location
        cursor.execute('''
            SELECT location, COUNT(*) 
            FROM semantic_events 
            GROUP BY location 
            ORDER BY COUNT(*) DESC 
            LIMIT 10
        ''')
        events_by_location = dict(cursor.fetchall())
        
        return {
            'total_events': total_events,
            'events_by_type': events_by_type,
            'events_by_location': events_by_location
        }


def find_svcs_files():
    """Find SVCS installation files."""
    svcs_files = ['svcs_repo_local.py', 'svcs_repo_analyzer.py', 'svcs_multilang.py']
    
    # Check environment variable first (set by global installation)
    install_dir = os.environ.get('SVCS_INSTALL_DIR')
    if install_dir:
        install_path = Path(install_dir)
        if all((install_path / f).exists() for f in svcs_files):
            return install_path
    
    # Check if we're in development mode (files in current directory)
    current_dir = Path(__file__).parent.parent  # Go up from svcs/utils.py to main directory
    
    # Check main directory first (development mode)
    if all((current_dir / f).exists() for f in svcs_files):
        return current_dir
    
    # Check parent directory of this script
    script_dir = Path(__file__).parent.parent
    if all((script_dir / f).exists() for f in svcs_files):
        return script_dir
    
    # Check if installed as package
    try:
        import svcs
        package_dir = Path(svcs.__file__).parent.parent
        if all((package_dir / f).exists() for f in svcs_files):
            return package_dir
    except ImportError:
        pass
    
    return None


def setup_repository_files(repo_path: Path):
    """Set up SVCS files in repository (user-friendly installation)."""
    svcs_dir = repo_path / '.svcs'
    svcs_dir.mkdir(exist_ok=True)
    
    # Find SVCS installation
    source_dir = find_svcs_files()
    if not source_dir:
        print("❌ Error: SVCS installation files not found.")
        print("   Please ensure SVCS is properly installed.")
        return False
    
    # Copy essential SVCS files to .svcs directory
    essential_files = [
        'svcs_repo_local.py',
        'svcs_repo_analyzer.py', 
        'svcs_multilang.py'
    ]
    
    for file in essential_files:
        src = source_dir / file
        dst = svcs_dir / file
        if src.exists():
            shutil.copy2(src, dst)
            print(f"📄 Installed {file}")
        else:
            print(f"⚠️ Warning: {file} not found in installation")
    
    # Copy analyzer if it exists
    analyzer_src = source_dir / 'analyzer.py'
    analyzer_dst = svcs_dir / 'analyzer.py'
    if analyzer_src.exists():
        shutil.copy2(analyzer_src, analyzer_dst)
        print("📄 Installed analyzer.py")
    elif (source_dir / '.svcs' / 'analyzer.py').exists():
        shutil.copy2(source_dir / '.svcs' / 'analyzer.py', analyzer_dst)
        print("📄 Installed analyzer.py")
    
    # Copy API module if it exists (for search/evolution functionality)
    api_src = source_dir / '.svcs' / 'api.py'
    api_dst = svcs_dir / 'api.py'
    if api_src.exists():
        shutil.copy2(api_src, api_dst)
        print("📄 Installed api.py")
        
        # Create a compatibility shim for database naming
        compat_content = '''#!/usr/bin/env python3
# API Compatibility Layer for Repository-Local SVCS
import os
import sys

# Update database path to match repository-local naming
original_db_path = os.path.join(".svcs", "history.db")
repo_local_db_path = os.path.join(".svcs", "semantic.db")

# Monkey patch the API module to use the correct database
if os.path.exists("api.py"):
    with open("api.py", "r") as f:
        api_content = f.read()
    
    # Replace database references
    api_content = api_content.replace('DB_PATH = os.path.join(SVCS_DIR, "history.db")', 
                                    'DB_PATH = os.path.join(SVCS_DIR, "semantic.db")')
    
    with open("api.py", "w") as f:
        f.write(api_content)
'''
        
        # Apply compatibility fix
        try:
            exec(compat_content)
            print("📄 Applied API compatibility fixes")
        except Exception as e:
            print(f"⚠️ Warning: Could not apply API compatibility fixes: {e}")
    else:
        print("⚠️ Warning: api.py not found - search/evolution features may not work")
    
    return True


def validate_repository(repo_path: Path):
    """Validate that the given path is a git repository with SVCS initialized."""
    if not (repo_path / '.git').exists():
        return False, "Not a git repository"
    
    if not (repo_path / '.svcs' / 'semantic.db').exists():
        return False, "SVCS not initialized"
    
    return True, "Valid SVCS repository"


def get_current_branch(repo_path: Path):
    """Get the current git branch."""
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return 'main'  # fallback


def format_timestamp(timestamp):
    """Format timestamp for display."""
    from datetime import datetime
    if isinstance(timestamp, (int, float)):
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(timestamp, str) and len(timestamp) > 19:
        return timestamp[:19]
    return str(timestamp)


def print_event(event, include_reasoning=True):
    """Print a semantic event in a standardized format."""
    timestamp = format_timestamp(event.get('created_at', event.get('timestamp', '')))
    
    confidence = event.get('confidence', 1.0)
    confidence_str = f" ({confidence:.1%})" if confidence < 1.0 else ""
    
    print(f"🔍 {event['event_type']}{confidence_str}")
    print(f"   📝 {event.get('commit_hash', 'N/A')[:8]} | {event.get('branch', 'N/A')} | {timestamp}")
    print(f"   🎯 {event.get('node_id', 'N/A')} @ {event.get('location', 'N/A')}")
    
    if 'details' in event:
        print(f"   💬 {event['details']}")
    
    if include_reasoning and 'reasoning' in event:
        print(f"   🧠 {event['reasoning']}")
    
    print()


def handle_import_error(module_name, suggestion=""):
    """Handle import errors with helpful messages."""
    print(f"❌ Error: {module_name} not available.")
    if suggestion:
        print(f"   {suggestion}")
    return False


def safe_json_dump(data, filepath, indent=2):
    """Safely write JSON data to file."""
    try:
        import json
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=indent)
        return True
    except Exception as e:
        print(f"❌ Error writing to {filepath}: {e}")
        return False


def smart_init_svcs(repo_path: Path):
    """Smart SVCS initialization with auto-detection."""
    import subprocess
    
    git_exists = (repo_path / '.git').exists()
    svcs_exists = (repo_path / '.svcs').exists()
    has_files = any(repo_path.iterdir()) if repo_path.exists() else False
    
    # Check if SVCS already initialized
    if svcs_exists:
        return "✅ SVCS already initialized. Use 'svcs status' to check repository status."
    
    # If git exists, proceed with SVCS initialization
    if git_exists:
        return init_svcs_centralized(repo_path)
    
    # If directory is empty, auto-initialize both git and SVCS
    if not has_files:
        print(f"📁 Empty directory detected. Initializing git repository and SVCS...")
        try:
            subprocess.run(['git', 'init'], cwd=repo_path, check=True, capture_output=True)
            print("✅ Git repository initialized")
            return init_svcs_centralized(repo_path)
        except subprocess.CalledProcessError as e:
            return f"❌ Error: Failed to initialize git repository: {e}"
    
    # Directory has files but no git - prompt user
    print("📁 Directory contains files but no git repository.")
    response = input("Initialize git repository? (y/n): ")
    
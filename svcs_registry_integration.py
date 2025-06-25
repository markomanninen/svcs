#!/usr/bin/env python3
"""
SVCS Registry Integration

Helper script for integrating repository registration with svcs init.
This can be called from the svcs init process to automatically register
repositories in the central registry.

Usage:
    python3 svcs_registry_integration.py register /path/to/repo [name]
    python3 svcs_registry_integration.py unregister /path/to/repo
    python3 svcs_registry_integration.py list
"""

import sys
import json
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from svcs_web_repository_manager import web_repository_manager
    MANAGER_AVAILABLE = True
except ImportError:
    MANAGER_AVAILABLE = False

def register_repository(repo_path: str, name: str = None):
    """Register repository in central registry."""
    if not MANAGER_AVAILABLE:
        print(json.dumps({'success': False, 'error': 'Repository manager not available'}))
        return 1
    
    result = web_repository_manager.auto_register_if_initialized(repo_path)
    print(json.dumps(result))
    return 0 if result['success'] else 1

def unregister_repository(repo_path: str):
    """Unregister repository from central registry."""
    if not MANAGER_AVAILABLE:
        print(json.dumps({'success': False, 'error': 'Repository manager not available'}))
        return 1
    
    result = web_repository_manager.unregister_repository(repo_path)
    print(json.dumps(result))
    return 0 if result['success'] else 1

def list_repositories():
    """List all registered repositories."""
    if not MANAGER_AVAILABLE:
        print(json.dumps({'success': False, 'error': 'Repository manager not available'}))
        return 1
    
    try:
        repositories = web_repository_manager.discover_repositories()
        registered = [r for r in repositories if r.get('registered', False)]
        
        result = {
            'success': True,
            'data': {
                'repositories': registered,
                'total': len(registered)
            }
        }
        print(json.dumps(result))
        return 0
    except Exception as e:
        print(json.dumps({'success': False, 'error': str(e)}))
        return 1

def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: svcs_registry_integration.py <command> [args...]")
        print("Commands:")
        print("  register <path> [name]   - Register repository")
        print("  unregister <path>        - Unregister repository") 
        print("  list                     - List registered repositories")
        return 1
    
    command = sys.argv[1]
    
    if command == 'register':
        if len(sys.argv) < 3:
            print(json.dumps({'success': False, 'error': 'Repository path required'}))
            return 1
        repo_path = sys.argv[2]
        name = sys.argv[3] if len(sys.argv) > 3 else None
        return register_repository(repo_path, name)
    
    elif command == 'unregister':
        if len(sys.argv) < 3:
            print(json.dumps({'success': False, 'error': 'Repository path required'}))
            return 1
        repo_path = sys.argv[2]
        return unregister_repository(repo_path)
    
    elif command == 'list':
        return list_repositories()
    
    else:
        print(json.dumps({'success': False, 'error': f'Unknown command: {command}'}))
        return 1

if __name__ == '__main__':
    sys.exit(main())

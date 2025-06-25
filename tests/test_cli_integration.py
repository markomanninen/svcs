#!/usr/bin/env python3
"""
Test CLI Integration with Repository Registry

This script tests that the svcs init command properly registers
repositories in the central registry.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
import sqlite3
import sys

# Add the project root to sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_svcs_init_registration():
    """Test that svcs init registers the repository in central registry."""
    print("🧪 Testing SVCS init with registry integration")
    print("=" * 50)
    
    # Create a temporary test directory
    with tempfile.TemporaryDirectory() as temp_dir:
        test_repo = Path(temp_dir) / "test_repo"
        test_repo.mkdir()
        
        print(f"📁 Created test repository: {test_repo}")
        
        # Initialize git repository
        subprocess.run(['git', 'init'], cwd=test_repo, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=test_repo, check=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=test_repo, check=True)
        print("✅ Git repository initialized")
        
        # Run svcs init (using the new CLI)
        try:
            result = subprocess.run([
                sys.executable, '-m', 'svcs.cli', 'init'
            ], cwd=test_repo, capture_output=True, text=True, check=True)
            
            print("✅ SVCS init completed successfully")
            print(f"Output: {result.stdout}")
            
            if result.stderr:
                print(f"Warnings: {result.stderr}")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ SVCS init failed: {e}")
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
            return False
        
        # Check that .svcs directory was created
        svcs_dir = test_repo / '.svcs'
        if not svcs_dir.exists():
            print("❌ .svcs directory was not created")
            return False
        print("✅ .svcs directory created")
        
        # Check that semantic.db was created
        db_path = svcs_dir / 'semantic.db'
        if not db_path.exists():
            print("❌ semantic.db was not created")
            return False
        print("✅ semantic.db created")
        
        # Check that the repository was registered in the central registry
        registry_path = Path.home() / '.svcs' / 'repos.db'
        if registry_path.exists():
            conn = sqlite3.connect(registry_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name, path FROM repositories WHERE path = ?", (str(test_repo),))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                print(f"✅ Repository registered in central registry: {result}")
            else:
                print("⚠️ Repository not found in central registry")
                return False
        else:
            print("⚠️ Central registry not found")
            return False
    
    print("\n🎉 All tests passed! CLI integration working correctly.")
    return True


def test_registry_functions():
    """Test the registry integration functions directly."""
    print("\n🧪 Testing registry integration functions")
    print("=" * 50)
    
    try:
        from svcs_repo_registry_integration import auto_register_after_init, list_registered_repos
        
        # Create a temporary test directory
        with tempfile.TemporaryDirectory() as temp_dir:
            test_repo = Path(temp_dir) / "test_repo_direct"
            test_repo.mkdir()
            
            # Initialize git and SVCS manually
            subprocess.run(['git', 'init'], cwd=test_repo, check=True, capture_output=True)
            svcs_dir = test_repo / '.svcs'
            svcs_dir.mkdir()
            
            # Create a dummy semantic.db
            (svcs_dir / 'semantic.db').touch()
            
            # Test auto-registration
            result = auto_register_after_init(str(test_repo))
            print(f"✅ Auto-registration result: {result}")
            
            # Test listing repos
            repos = list_registered_repos()
            print(f"✅ Found {len(repos)} registered repositories")
            
            # Check if our test repo is in the list
            test_repo_found = any(repo['path'] == str(test_repo) for repo in repos)
            if test_repo_found:
                print("✅ Test repository found in registry")
            else:
                print("❌ Test repository not found in registry")
                return False
                
    except Exception as e:
        print(f"❌ Registry function test failed: {e}")
        return False
    
    print("✅ Registry function tests passed!")
    return True


if __name__ == "__main__":
    print("🚀 Starting CLI Integration Tests")
    print("=" * 60)
    
    # Test 1: Direct registry functions
    if not test_registry_functions():
        print("❌ Registry function tests failed")
        sys.exit(1)
    
    # Test 2: Full CLI integration
    if not test_svcs_init_registration():
        print("❌ CLI integration tests failed")
        sys.exit(1)
    
    print("\n🎉 All integration tests passed!")
    print("✅ svcs init now properly registers repositories in the central registry!")

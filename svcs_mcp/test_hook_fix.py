#!/usr/bin/env python3
"""
Test script to verify SVCS hook installation now only uses post-commit
"""

import sys
import tempfile
import subprocess
from pathlib import Path

# Add the MCP directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from svcs_mcp.git_hooks import GitHookManager

def test_hook_installation():
    """Test that hook installation only creates post-commit hook."""
    
    print("🧪 Testing Updated Hook Installation")
    print("=" * 50)
    
    # Create a temporary git repository
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = Path(temp_dir)
        
        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=repo_path, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=repo_path)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=repo_path)
        
        print(f"📁 Created test repo: {repo_path}")
        
        # Install hooks using updated GitHookManager
        hook_manager = GitHookManager()
        success = hook_manager.install_project_hooks(str(repo_path))
        
        print(f"✅ Hook installation: {'Success' if success else 'Failed'}")
        
        # Check what hooks were installed
        hooks_dir = repo_path / ".git" / "hooks"
        post_commit = hooks_dir / "post-commit"
        pre_commit = hooks_dir / "pre-commit"
        
        print("\n📋 Hook Status:")
        print(f"   post-commit: {'✅ Installed' if post_commit.exists() else '❌ Not found'}")
        print(f"   pre-commit:  {'⚠️ Found (should not exist)' if pre_commit.exists() else '✅ Not installed (correct)'}")
        
        # Check hook status via API
        status = hook_manager.get_project_hook_status(str(repo_path))
        print(f"\n📊 Hook Status via API:")
        for hook_name, hook_status in status.items():
            status_emoji = "✅" if hook_status == "svcs_installed" else "❌" if hook_status == "not_installed" else "⚠️"
            print(f"   {hook_name}: {status_emoji} {hook_status}")
        
        # Verify only post-commit should be installed
        expected_result = (
            post_commit.exists() and 
            not pre_commit.exists() and
            status['post-commit'] == 'svcs_installed' and
            status['pre-commit'] == 'not_installed'
        )
        
        print(f"\n🎯 Test Result: {'✅ PASS' if expected_result else '❌ FAIL'}")
        
        if expected_result:
            print("   ✅ Only post-commit hook installed (correct behavior)")
        else:
            print("   ❌ Unexpected hook configuration")
        
        return expected_result

if __name__ == "__main__":
    success = test_hook_installation()
    if success:
        print("\n🎉 All tests passed! Hook installation is correctly updated.")
    else:
        print("\n💥 Test failed! Hook installation needs further fixes.")
    
    sys.exit(0 if success else 1)

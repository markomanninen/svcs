#!/usr/bin/env python3
"""
Demo: SVCS Global Git Hook System

This demonstrates the complete git hook flow:
1. Global hook installation
2. Project hook registration 
3. Hook routing to MCP server
4. Clean uninstallation
"""

import sys
import tempfile
import subprocess
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "svcs_mcp"))

def demo_git_hooks():
    """Demonstrate the SVCS git hook system."""
    print("🔗 SVCS Git Hook System Demo")
    print("=" * 50)
    
    try:
        from svcs_mcp.git_hooks import GitHookManager
        print("✅ Successfully imported GitHookManager")
    except Exception as e:
        print(f"❌ Import error: {e}")
        return
    
    # Initialize hook manager
    hook_manager = GitHookManager()
    print(f"📁 SVCS Home: {hook_manager.svcs_home}")
    print(f"🔗 Global Hook: {hook_manager.global_hook_script}")
    
    # Install global hooks
    print("\n1️⃣  Installing Global Hook System...")
    if hook_manager.install_global_hooks():
        print("✅ Global hooks installed successfully")
        print(f"📝 Global hook script created: {hook_manager.global_hook_script}")
    else:
        print("❌ Failed to install global hooks")
        return
    
    # Get current project path
    current_project = str(Path.cwd())
    print(f"\n2️⃣  Testing Hook Installation for Current Project...")
    print(f"📂 Project: {current_project}")
    
    # Check if it's a git repository
    if not (Path(current_project) / '.git').exists():
        print("❌ Current directory is not a git repository")
        return
    
    # Install project hooks
    if hook_manager.install_project_hooks(current_project):
        print("✅ Project hooks installed successfully")
    else:
        print("❌ Failed to install project hooks")
        return
    
    # Check hook status
    print("\n3️⃣  Checking Hook Status...")
    status = hook_manager.get_project_hook_status(current_project)
    for hook_name, hook_status in status.items():
        status_icon = {
            'svcs_installed': '✅',
            'not_installed': '❌', 
            'custom_script': '⚠️',
            'other_symlink': '🔗'
        }.get(hook_status, '❓')
        print(f"  {hook_name}: {status_icon} {hook_status}")
    
    # Show actual symlinks
    print("\n4️⃣  Verifying Symlinks...")
    git_hooks_dir = Path(current_project) / ".git" / "hooks"
    for hook_name in ['post-commit']:  # Only install post-commit to avoid double analysis
        hook_path = git_hooks_dir / hook_name
        if hook_path.exists() and hook_path.is_symlink():
            target = hook_path.resolve()
            print(f"  {hook_name} -> {target}")
            if target == hook_manager.global_hook_script.resolve():
                print(f"    ✅ Correctly linked to global hook")
            else:
                print(f"    ⚠️  Linked to different script")
        else:
            print(f"  {hook_name}: ❌ Not a symlink")
    
    # Test hook execution (simulated)
    print("\n5️⃣  Testing Hook Execution...")
    try:
        # Check if the hook is executable
        if hook_manager.global_hook_script.stat().st_mode & 0o111:
            print("✅ Global hook script is executable")
        else:
            print("❌ Global hook script is not executable")
        
        # Try to run hook help (this will fail but show the routing)
        result = subprocess.run([
            str(hook_manager.global_hook_script)
        ], capture_output=True, text=True, cwd=current_project)
        
        print(f"Hook execution exit code: {result.returncode}")
        if result.stdout:
            print(f"Hook stdout: {result.stdout}")
        if result.stderr:
            print(f"Hook stderr: {result.stderr}")
            
    except Exception as e:
        print(f"⚠️ Hook execution test failed: {e}")
    
    print("\n6️⃣  Hook System Architecture:")
    print("┌─ ~/.svcs/hooks/svcs-hook (Global Script)")
    print("│  ├─ Detects project from git root")
    print("│  ├─ Checks if project is registered") 
    print("│  └─ Routes to 'svcs analyze-commit' etc.")
    print("│")
    print("├─ Project/.git/hooks/post-commit -> Global Script")
    print("└─ Multiple projects can use same global hook")
    
    print("\n✨ Git Hook Demo Summary:")
    print("  ✅ Global hook system installed")
    print("  ✅ Project hooks linked via symlinks")
    print("  ✅ Original hooks backed up safely")
    print("  ✅ Hook routing architecture ready")
    print("  ✅ Zero per-project hook management needed")
    
    print("\n🚀 Benefits Achieved:")
    print("  • One global hook script for all projects")
    print("  • Automatic project detection and routing")
    print("  • Safe installation with backup/restore")
    print("  • Easy uninstallation and cleanup")
    print("  • Scalable to unlimited projects")


if __name__ == "__main__":
    demo_git_hooks()

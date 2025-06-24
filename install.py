#!/usr/bin/env python3
"""
SVCS Installation Script

This script makes SVCS available as a global command.
After running this, users can simply:

  svcs init      # in any git repository
  svcs status    # show semantic analysis status  
  svcs events    # list semantic events
  svcs compare   # compare branches

No manual file copying required!
"""

import os
import shutil
import sys
from pathlib import Path


def install_svcs():
    """Install SVCS globally."""
    print("🚀 Installing SVCS globally...")
    
    # Get current SVCS directory
    svcs_dir = Path(__file__).parent.resolve()
    
    # Check if all required files exist
    required_files = [
        'svcs_repo_local.py',
        'svcs_repo_analyzer.py', 
        'svcs_multilang.py',
        'svcs_repo_hooks.py',
        'svcs/cli.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not (svcs_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Error: Missing required files: {', '.join(missing_files)}")
        return False
    
    # Find Python bin directory
    python_bin = Path(sys.executable).parent
    svcs_command = python_bin / 'svcs'
    
    # Create the global 'svcs' command
    svcs_script = f'''#!/usr/bin/env python3
"""
SVCS Global Command

Automatically generated installer script.
"""

import sys
from pathlib import Path

# Add SVCS directory to Python path
SVCS_DIR = Path("{svcs_dir}")
if str(SVCS_DIR) not in sys.path:
    sys.path.insert(0, str(SVCS_DIR))

# Set environment variable for SVCS installation directory
import os
os.environ['SVCS_INSTALL_DIR'] = str(SVCS_DIR)

# Import and run SVCS CLI
try:
    from svcs.cli import main
    main()
except ImportError as e:
    print(f"❌ Error importing SVCS: {{e}}")
    print(f"SVCS installation directory: {{SVCS_DIR}}")
    sys.exit(1)
'''
    
    try:
        # Write the global command script
        with open(svcs_command, 'w') as f:
            f.write(svcs_script)
        
        # Make it executable
        svcs_command.chmod(0o755)
        
        print(f"✅ SVCS command installed to: {svcs_command}")
        print(f"✅ SVCS source directory: {svcs_dir}")
        print()
        print("🎉 Installation complete!")
        print()
        print("You can now use SVCS in any git repository:")
        print("  svcs init      # Initialize SVCS")
        print("  svcs status    # Show status")
        print("  svcs events    # List semantic events")
        print("  svcs compare   # Compare branches")
        print()
        
        # Test the installation
        print("🧪 Testing installation...")
        result = os.system(f"{svcs_command} --help > /dev/null 2>&1")
        if result == 0:
            print("✅ Installation test passed!")
        else:
            print("⚠️ Installation test failed - command may not be in PATH")
            print(f"   You may need to add {python_bin} to your PATH")
        
        return True
        
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return False


def uninstall_svcs():
    """Uninstall SVCS."""
    print("🗑️ Uninstalling SVCS...")
    
    python_bin = Path(sys.executable).parent
    svcs_command = python_bin / 'svcs'
    
    if svcs_command.exists():
        svcs_command.unlink()
        print(f"✅ Removed: {svcs_command}")
    else:
        print("ℹ️ SVCS command not found")
    
    print("✅ Uninstallation complete!")


def main():
    """Main installer entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == 'uninstall':
        uninstall_svcs()
    else:
        install_svcs()


if __name__ == "__main__":
    main()

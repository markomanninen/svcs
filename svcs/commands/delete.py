import shutil
from pathlib import Path
import sys
import subprocess

def cmd_delete_project(args):
    """Unregister project from SVCS registry and delete its directory."""
    project_path = Path(args.path or Path.cwd()).resolve()
    print(f"⚠️  This will unregister and permanently delete the project at: {project_path}")
    confirm = input("Are you sure you want to continue? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Aborted.")
        return

    # Unregister from registry
    print("Unregistering from SVCS registry...")
    result = subprocess.run([
        sys.executable, "svcs_repo_registry_integration.py", "unregister", str(project_path)
    ], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print("Failed to unregister from registry. Aborting delete.")
        return

    # Delete directory
    print(f"Deleting project directory: {project_path}")
    try:
        shutil.rmtree(project_path)
        print("✅ Project directory deleted.")
    except Exception as e:
        print(f"❌ Error deleting directory: {e}")

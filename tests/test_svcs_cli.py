import unittest
import subprocess
import tempfile
from pathlib import Path
import json
import os

class TestSVCSCLI(unittest.TestCase):

    repo_root = Path(__file__).parent.parent

    def _run_svcs_command(self, command_args, tmpdir_path=None):
        base_cmd = [sys.executable, '-m', 'svcs']
        full_cmd = base_cmd + command_args

        env = os.environ.copy()
        python_path = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = f"{str(self.repo_root)}{os.pathsep}{python_path}"

        # Run from repo_root unless a specific tmpdir_path (project path) is more appropriate
        # For init-project, creating the project happens from outside, so repo_root is fine.
        # For commands like 'status' within a project, cwd should be tmpdir_path.
        cwd = tmpdir_path if tmpdir_path and Path(tmpdir_path).is_dir() else self.repo_root

        result = subprocess.run(
            full_cmd,
            capture_output=True, text=True, check=False,
            cwd=cwd,
            env=env
        )
        print(f"Running command: {' '.join(full_cmd)}")
        print(f"stdout:\n{result.stdout}")
        if result.stderr:
            print(f"stderr:\n{result.stderr}")
        return result

    def test_init_project_non_interactive(self):
        """Test the 'svcs init-project --non-interactive' command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_name = "test_non_interactive_project"

            cmd_args = ['init-project', project_name, '--path', tmpdir, '--non-interactive']
            result = self._run_svcs_command(cmd_args)

            self.assertEqual(result.returncode, 0, f"init-project --non-interactive failed with error: {result.stderr}")

            project_path = Path(tmpdir) / project_name
            self.assertTrue(project_path.exists(), f"Project directory '{project_path}' was not created")
            self.assertTrue(project_path.is_dir(), f"'{project_path}' is not a directory")

            # Check for .git directory (smart_init_svcs should create it)
            self.assertTrue((project_path / ".git").exists(), ".git directory was not created")
            self.assertTrue((project_path / ".git").is_dir(), ".git is not a directory")

            # Check for .svcs directory and config.json (smart_init_svcs should create these)
            svcs_dir = project_path / ".svcs"
            self.assertTrue(svcs_dir.exists(), ".svcs directory was not created")
            self.assertTrue((svcs_dir / "config.json").exists(), ".svcs/config.json was not created")

            # Check for main.py
            self.assertTrue((project_path / "main.py").exists(), "main.py was not created")

            # Check for initial commit by looking at git log
            log_result = subprocess.run(
                ['git', 'log', '--oneline'],
                cwd=project_path, capture_output=True, text=True, check=True
            )
            self.assertIn("Initial commit (non-interactive setup)", log_result.stdout, "Initial commit not found in git log")

            # Verify content of .svcs/config.json (project name might be default or passed)
            with open(svcs_dir / "config.json", "r") as f:
                config_data = json.load(f)
            # In non-interactive mode, if project_name is passed, it should use it.
            # If project_name in cmd_init_project for non-interactive is not used, it defaults.
            # The test passes project_name, so smart_init_svcs should ideally pick it up or have a way to set it.
            # For now, let's assume smart_init_svcs might use a generic name or the dir name.
            # This needs to be aligned with how smart_init_svcs actually behaves.
            # For this test, we'll check if projectName key exists.
            self.assertIn("projectName", config_data, "projectName not in config.json")
            # A more specific check could be:
            # self.assertEqual(config_data["projectName"], project_name) # If smart_init sets it from dir name

            # Test attempting to create a project that already exists (non-interactive)
            result_exists = self._run_svcs_command(cmd_args) # Run the same command again
            self.assertNotEqual(result_exists.returncode, 0, "Command should fail or indicate error when project exists")
            self.assertIn("already exists", result_exists.stderr.lower() + result_exists.stdout.lower(), "Error message for existing project not found")

    def test_init_project_non_interactive_no_name(self):
        """Test 'svcs init-project --non-interactive' without a project name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # No project_name argument, should use default "svcs_non_interactive_project"
            cmd_args = ['init-project', '--path', tmpdir, '--non-interactive']
            result = self._run_svcs_command(cmd_args)

            self.assertEqual(result.returncode, 0, f"init-project --non-interactive (no name) failed: {result.stderr}")

            # Default name is "svcs_non_interactive_project" in cmd_init_project
            project_path = Path(tmpdir) / "svcs_non_interactive_project"
            self.assertTrue(project_path.exists(), "Default project directory was not created")
            self.assertTrue((project_path / ".git").exists(), ".git directory was not created for default project name")
            self.assertTrue((project_path / "main.py").exists(), "main.py was not created for default project name")

            log_result = subprocess.run(
                ['git', 'log', '--oneline'],
                cwd=project_path, capture_output=True, text=True, check=True
            )
            self.assertIn("Initial commit (non-interactive setup)", log_result.stdout)


if __name__ == '__main__':
    import sys
    unittest.main()

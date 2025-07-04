#!/usr/bin/env python3
"""
SVCS Init Commands

Commands for initializing SVCS in repositories.
"""

from pathlib import Path
from .base import smart_init_svcs


def cmd_init(args):
    """Initialize SVCS for current repository with smart auto-detection."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    # Smart initialization logic
    result = smart_init_svcs(repo_path)
    print(result)


# Make sure to import Path and other necessary modules at the top of init.py
import os
import subprocess
import shutil
from .base import smart_init_svcs # Assuming smart_init_svcs is here
try:
    from .tour_utils import (
        print_art, print_step_header, print_info, print_command,
        print_success, print_warning, print_error, ask_prompt,
        ask_confirm, print_file_content, WELCOME_BANNER, PROJECT_SETUP_ICON,
        SVCS_INIT_ICON, FILE_ICON, GIT_COMMIT_ICON, MENU_BANNER, FAREWELL_BANNER,
        COMMAND_DOCS, console
    )
except ImportError:
    # Fallback for environments where tour_utils might not be in the same package directly
    # This might happen if commands are structured differently or during certain test setups.
    # A more robust solution might involve adjusting sys.path or ensuring package structure.
    print("Warning: tour_utils not found directly, trying relative import for development.")
    try:
        from tour_utils import (
            print_art, print_step_header, print_info, print_command,
            print_success, print_warning, print_error, ask_prompt,
            ask_confirm, print_file_content, WELCOME_BANNER, PROJECT_SETUP_ICON,
            SVCS_INIT_ICON, FILE_ICON, GIT_COMMIT_ICON, MENU_BANNER, FAREWELL_BANNER,
            COMMAND_DOCS, console
        )
    except ImportError:
        print("Error: tour_utils.py could not be imported. Interactive tour may not function correctly.")
        # Define minimal fallbacks so the script doesn't crash
        def print_art(art_string, style=""): print(art_string)
        def print_step_header(message): print(f"\n--- {message} ---")
        def print_info(message): print(f"INFO: {message}")
        def print_command(command_str): print(f"$ {command_str}")
        def print_success(message): print(f"SUCCESS: {message}")
        def print_warning(message): print(f"WARNING: {message}")
        def print_error(message): print(f"ERROR: {message}")
        def ask_prompt(prompt_message, default=None, choices=None): return input(f"{prompt_message} [{default}]: ") or default
        def ask_confirm(prompt_message, default=True): return input(f"{prompt_message} (Y/n): ").lower() != 'n' if default else input(f"{prompt_message} (y/N): ").lower() == 'y'
        def print_file_content(file_path, header=None):
            try: print(f"\n--- Contents of {file_path.name} ---\n{file_path.read_text()}")
            except Exception as e: print_error(f"Could not read {file_path}: {e}")
        WELCOME_BANNER = SVCS_INIT_ICON = FILE_ICON = GIT_COMMIT_ICON = MENU_BANNER = FAREWELL_BANNER = PROJECT_SETUP_ICON = ""
        COMMAND_DOCS = {}
        console = None # No rich console features

def _run_subprocess(cmd_list, cwd_path, check=True):
    """Helper to run subprocess and print command."""
    print_command(" ".join(cmd_list))
    try:
        process = subprocess.run(cmd_list, cwd=cwd_path, check=check, capture_output=True, text=True)
        if process.stdout:
            print_info(f"Output:\n{process.stdout.strip()}")
        if process.stderr:
            # Treat stderr as warning unless check=True and it fails
            (print_error if check and process.returncode != 0 else print_warning)(f"Stderr:\n{process.stderr.strip()}")
        return process
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {e}")
        if e.stdout: print_error(f"Stdout:\n{e.stdout.strip()}")
        if e.stderr: print_error(f"Stderr:\n{e.stderr.strip()}")
        raise
    except FileNotFoundError:
        print_error(f"Command not found: {cmd_list[0]}. Is it installed and in your PATH?")
        raise


def cmd_init_project(args):
    """Initialize a new SVCS project with an interactive tour."""

    if hasattr(args, 'non_interactive') and args.non_interactive:
        # Simplified non-interactive setup (for tests or power users)
        project_name = args.project_name if hasattr(args, 'project_name') and args.project_name else "svcs_non_interactive_project"
        base_path_str = args.path if hasattr(args, 'path') and args.path else "."
        base_path = Path(base_path_str).resolve()
        project_path = base_path / project_name

        if project_path.exists():
            print_error(f"Project directory '{project_path}' already exists. Aborting non-interactive setup.")
            return

        original_cwd = Path.cwd()
        try:
            project_path.mkdir(parents=True, exist_ok=True)
            os.chdir(project_path)
            print_info(f"Running non-interactive setup in {project_path}")

            smart_init_svcs(Path.cwd()) # This handles git init etc.

            main_py_content = "def hello():\n    print(\"Hello from main.py\")\n\nif __name__ == \"__main__\":\n    hello()"
            with open("main.py", "w") as f:
                f.write(main_py_content)

            _run_subprocess(["git", "add", "main.py"], cwd_path=project_path)
            _run_subprocess(["git", "commit", "-m", "Initial commit (non-interactive setup)"], cwd_path=project_path)
            print_success(f"Non-interactive project '{project_name}' setup complete at {project_path}")

        except Exception as e:
            print_error(f"Error during non-interactive project initialization: {e}")
        finally:
            os.chdir(original_cwd)
        return

    # Interactive Tour Starts
    print_art(WELCOME_BANNER)
    print_info("This tour will guide you through setting up a new SVCS project.")

    # 1. Project Name
    default_project_name = "svcs_demo_project"
    project_name = ask_prompt("Enter a name for your demo project", default=default_project_name)
    if not project_name: project_name = default_project_name

    # 2. Project Path
    default_path_str = "."
    path_str = ask_prompt("Where should we create this project? (Enter path or '.' for current dir)", default=default_path_str)
    if not path_str: path_str = default_path_str

    base_path = Path(path_str).resolve()
    project_path = base_path / project_name

    # 3. Confirmation
    if not ask_confirm(f"We will create '{project_path}'.\nThis will also initialize it as a Git repository and set it up for SVCS. Continue?", default=True):
        print_warning("Tour aborted by user.")
        return

    if project_path.exists():
        print_error(f"Project directory '{project_path}' already exists. Please choose a different name or path.")
        return

    original_cwd = Path.cwd()
    main_py_modified_externally = False
    initial_commit_done = False

    try:
        # 4. Directory Creation
        print_art(PROJECT_SETUP_ICON)
        project_path.mkdir(parents=True)
        os.chdir(project_path)
        print_success(f"Created project directory and changed to: {project_path}")

        # 5. SVCS Initialization
        print_art(SVCS_INIT_ICON)
        print_info("Now, let's initialize SVCS in this project. This will also set up Git if needed.")
        print_command("svcs init (internally calling smart_init_svcs)")
        try:
            smart_init_svcs(Path.cwd()) # Path.cwd() is now project_path
            print_success("`svcs init` complete! This has:\n"
                          "  - Initialized a Git repository (if one wasn't already present).\n"
                          "  - Set up SVCS (hooks, database) in the '.svcs' directory.")
        except Exception as e:
            print_error(f"Failed to initialize SVCS: {e}")
            print_warning("You might need to run 'git init' and 'svcs init' manually in this directory.")
            # Continue the tour if possible, but some features might not work

        svcs_config_path = project_path / ".svcs" / "config.json"
        if svcs_config_path.exists():
            if ask_confirm("The file `.svcs/config.json` was created and configures SVCS for this project. View its contents?", default=False):
                print_file_content(svcs_config_path)
        else:
            print_warning(".svcs/config.json was not found. SVCS might not be properly initialized.")

        # 6. Sample Code Creation
        print_art(FILE_ICON)
        main_py_content = "def hello():\n    print(\"Hello from main.py\")\n\nif __name__ == \"__main__\":\n    hello()"
        main_py_file = project_path / "main.py"
        with open(main_py_file, "w") as f:
            f.write(main_py_content)
        print_success(f"Created sample file: {main_py_file.name}")

        # 7. First Git Commit
        if ask_confirm("Let's make the first commit to get `main.py` into Git and have SVCS analyze it. Commit now?", default=True):
            print_art(GIT_COMMIT_ICON)
            try:
                _run_subprocess(["git", "add", main_py_file.name], cwd_path=project_path)
                commit_msg = "Initial commit: Add main.py (via svcs init-project tour)"
                _run_subprocess(["git", "commit", "-m", commit_msg], cwd_path=project_path)
                print_success("Commit successful! SVCS post-commit hook should have analyzed `main.py`.")
                initial_commit_done = True
            except Exception as e:
                print_error(f"Git operation failed: {e}. You may need to configure git (user.name, user.email) or commit manually.")
        else:
            print_info("First commit skipped. You can commit the file manually later.")

        # 8. Interactive Loop
        print_art(MENU_BANNER)
        print_info(f"Project setup complete. You are in: {project_path}")

        while True:
            console.rule("SVCS Tour Menu")
            menu_options = {
                "1": "View SVCS Status (runs `svcs status`)",
                "2": "See Semantic Events (runs `svcs events`)",
                "3": f"View {main_py_file.name} content",
                "4": f"Instruct on modifying {main_py_file.name}",
                "5": f"Stage and Commit changes to {main_py_file.name}" + (" (enabled after modification)" if not main_py_modified_externally else ""),
                "6": "View .svcs/config.json content",
                "7": "Learn more about an SVCS command",
                "8": "Exit Tour"
            }

            for key, value in menu_options.items():
                if key == "5" and not main_py_modified_externally:
                    console.print(f"{key}. [dim]{value}[/dim]")
                else:
                    console.print(f"{key}. {value}")

            choice = ask_prompt("Choose an option (1-8)", choices=list(menu_options.keys()))

            if choice == "1":
                _run_subprocess(["svcs", "status"], cwd_path=project_path, check=False)
            elif choice == "2":
                if initial_commit_done:
                    _run_subprocess(["svcs", "events"], cwd_path=project_path, check=False)
                else:
                    print_warning("No commits made yet to show events for. Try committing a change first.")
            elif choice == "3":
                print_file_content(main_py_file)
            elif choice == "4":
                print_info(f"Please open `{main_py_file}` in your preferred text editor, make some changes, and save it.")
                print_info("After saving, choose option 5 to commit your changes.")
                if ask_confirm(f"Have you modified and saved {main_py_file.name}?", default=False):
                     main_py_modified_externally = True
                     print_success(f"{main_py_file.name} marked as modified. You can now use option 5.")
                else:
                    print_info("Okay, let me know when you have by selecting this option again.")

            elif choice == "5":
                if main_py_modified_externally:
                    commit_msg_default = "Updated main.py"
                    commit_msg = ask_prompt("Enter commit message", default=commit_msg_default)
                    if not commit_msg: commit_msg = commit_msg_default
                    try:
                        _run_subprocess(["git", "add", main_py_file.name], cwd_path=project_path)
                        _run_subprocess(["git", "commit", "-m", commit_msg], cwd_path=project_path)
                        print_success("Commit successful! SVCS analyzed the changes.")
                        main_py_modified_externally = False
                        initial_commit_done = True
                    except Exception as e:
                        print_error(f"Git commit failed: {e}")
                else:
                    print_warning(f"Please use option 4 to modify `{main_py_file.name}` first, or confirm modification.")
            elif choice == "6":
                if svcs_config_path.exists():
                    print_file_content(svcs_config_path)
                else:
                    print_warning(".svcs/config.json not found.")
            elif choice == "7":
                cmd_learn = ask_prompt("Which SVCS command do you want to learn about (e.g., status, events, config, search, init)?", choices=list(COMMAND_DOCS.keys()))
                if cmd_learn and cmd_learn in COMMAND_DOCS:
                    print_info(f"** {cmd_learn.upper()} **\n{COMMAND_DOCS[cmd_learn]}")
                elif cmd_learn:
                    print_warning(f"Sorry, no quick help available for '{cmd_learn}'.")
            elif choice == "8":
                break
            else:
                print_warning("Invalid choice, please try again.")

            if not ask_confirm("Continue with tour menu?", default=True):
                break

    except KeyboardInterrupt:
        print_warning("\nTour interrupted by user.")
    except Exception as e:
        print_error(f"An unexpected error occurred during the tour: {e}")
        import traceback
        console.print_exception(show_locals=True)
    finally:
        os.chdir(original_cwd) # Ensure we change back to original CWD
        print_art(FAREWELL_BANNER)
        print_info(f"Exited tour. If project was created, it's at: {project_path if 'project_path' in locals() and project_path.exists() else 'N/A'}")
        print_info(f"You are now back in: {Path.cwd()}")

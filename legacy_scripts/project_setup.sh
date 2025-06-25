#!/bin/bash
# ==============================================================================
# Comprehensive Semantic VCS (SVCS) - Project Setup Script
# ==============================================================================
# NOTE: This script was used to initialize a complete Python project structure
# and should not be confuced with the installation of the svcs package.
#
# This script initializes a complete, professional Python project structure and
# integrates the SVCS semantic analysis tool.
#
# What it does:
# 1. Creates a standard project layout: src/, tests/, docs/.
# 2. Creates placeholder source, test, and documentation files.
# 3. Initializes a Git repository if one doesn't exist.
# 4. Creates a comprehensive .gitignore file.
# 5. Sets up the SVCS tool in a hidden .svcs/ directory.
# 6. Modularizes the SVCS code for better maintainability.
# 7. Installs a Git "post-commit" hook to run semantic analysis automatically.
#
# Usage:
# 1. Save this script as `setup_svcs_project.sh` in an empty directory.
# 2. Make it executable: `chmod +x setup_svcs_project.sh`
# 3. Run it: `./setup_svcs_project.sh`
#
# ==============================================================================

# --- Configuration ---
SVCS_DIR=".svcs"
VENV_DIR="$SVCS_DIR/venv"
GIT_HOOK_PATH=".git/hooks/post-commit"

# --- Helper Functions ---
function print_info {
    echo -e "\033[34m[INFO]\033[0m $1"
}

function print_success {
    echo -e "\033[32m[SUCCESS]\033[0m $1"
}

function print_warning {
    echo -e "\033[33m[WARNING]\033[0m $1"
}

function print_error {
    echo -e "\033[31m[ERROR]\033[0m $1"
    exit 1
}

# --- Main Script ---
print_info "Starting Comprehensive SVCS Project Setup..."

# 1. Check Prerequisites
print_info "Checking prerequisites (Git and Python 3)..."
command -v git >/dev/null 2>&1 || { print_error "Git is not installed. Please install Git to continue."; }
command -v python3 >/dev/null 2>&1 || { print_error "Python 3 is not installed. Please install Python 3 to continue."; }
print_success "Prerequisites met."

# 2. Initialize Git Repository
if [ ! -d ".git" ]; then
    print_info "No Git repository found. Initializing a new one..."
    git init
    print_success "New Git repository initialized."
else
    print_info "Existing Git repository found."
fi

# 3. Create Standard Project Directory Structure
print_info "Creating project directory structure (src, tests, docs)..."
mkdir -p src tests docs
print_success "Project directories created."

# 4. Create Placeholder Project Files
print_info "Creating placeholder project files..."

# Source file
cat << 'EOF' > src/main.py
def greet(name="world"):
    """Greets the user."""
    message = f"Hello, {name}!"
    print(message)
    return message

if __name__ == "__main__":
    greet()
EOF

# Test file
cat << 'EOF' > tests/test_main.py
import sys
import os
# Add src to path to allow importing main
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from main import greet

def test_greet_default():
    """Tests the greet function with no arguments."""
    assert greet() == "Hello, world!"

def test_greet_with_name():
    """Tests the greet function with a name."""
    assert greet("Alice") == "Hello, Alice!"
EOF

# Documentation file
cat << 'EOF' > docs/index.md
# Project Documentation

Welcome to your new project!

## Setup

This project was initialized with the SVCS setup script.

## Running the application

To run the application, execute:

`python3 src/main.py`

## Running tests

To run tests, you might use pytest:

`python3 -m pytest`
EOF

print_success "Placeholder files created."


# 5. Create .gitignore
print_info "Creating .gitignore file..."
cat << 'EOF' > .gitignore
# Python
__pycache__/
*.py[cod]
*$py.class

# SVCS Tool Directory
.svcs/

# Virtual Environment
venv/
*.venv
env/
ENV/

# IDE/Editor specific
.vscode/
.idea/
*.swp
*.swo
EOF
print_success ".gitignore created."

# 6. Create Modular SVCS Tool Structure
print_info "Creating modular SVCS tool in '$SVCS_DIR'..."
mkdir -p "$SVCS_DIR"

# Main entry point for the tool
cat << 'EOF' > "$SVCS_DIR/main.py"
#!/usr/bin/env python3
import subprocess
from rich.console import Console
from rich.table import Table
from analyzer import analyze_changes

console = Console()

def get_changed_python_files(commit_hash="HEAD"):
    """Identifies Python files changed in the specified commit."""
    try:
        files_cmd = ["git", "show", "--pretty=format:", "--name-only", commit_hash]
        result = subprocess.run(files_cmd, capture_output=True, text=True, check=True)
        all_files = result.stdout.strip().split('\n')
        py_files = [f for f in all_files if f.endswith(".py")]
        return py_files
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Error getting changed files:[/bold red] {e.stderr}")
        return []

def get_file_content_at_commit(filepath, commit_hash):
    """Retrieves the full content of a file at a specific commit."""
    try:
        cmd = ["git", "show", f"{commit_hash}:{filepath}"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError:
        return "" # File might be new or deleted

def run_analysis():
    console.print("\n[bold cyan]--=[ SVCS Semantic Analysis ]=--[/bold cyan]")
    commit_hash = "HEAD"
    parent_hash = "HEAD~1"
    changed_files = get_changed_python_files(commit_hash)

    if not changed_files:
        console.print("No Python files changed in this commit. Nothing to analyze.")
        return

    all_events = []
    for filepath in changed_files:
        content_after = get_file_content_at_commit(filepath, commit_hash)
        content_before = get_file_content_at_commit(filepath, parent_hash)
        file_events = analyze_changes(filepath, content_before, content_after)
        all_events.extend(file_events)

    if not all_events:
        console.print("No semantic changes detected.")
        return

    table = Table(title=f"Detected Semantic Events for Commit {subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode().strip()}")
    table.add_column("Event Type", style="cyan", no_wrap=True)
    table.add_column("Semantic Node", style="magenta")
    table.add_column("Location", style="green")

    for event in all_events:
        table.add_row(event["event_type"], event["node_id"], event["location"])

    console.print(table)
    # In a real implementation, these events would be stored in the .svcs database.

if __name__ == "__main__":
    run_analysis()
EOF

# Parser module
cat << 'EOF' > "$SVCS_DIR/parser.py"
import ast
from rich.console import Console

console = Console()

def parse_code_to_nodes(source_code):
    """Parses Python source code and extracts a dictionary of semantic nodes."""
    nodes = {}
    if not source_code:
        return nodes
    try:
        tree = ast.parse(source_code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                node_id = f"func:{node.name}"
                nodes[node_id] = ast.unparse(node)
            elif isinstance(node, ast.ClassDef):
                node_id = f"class:{node.name}"
                nodes[node_id] = ast.unparse(node)
    except SyntaxError:
        console.print(f"[bold yellow]Warning:[/bold yellow] Could not parse a file due to a syntax error.")
    return nodes
EOF

# Analyzer module
cat << 'EOF' > "$SVCS_DIR/analyzer.py"
from parser import parse_code_to_nodes

def analyze_changes(filepath, before_content, after_content):
    """Compares two versions of a file and generates semantic events."""
    events = []
    nodes_before = parse_code_to_nodes(before_content)
    nodes_after = parse_code_to_nodes(after_content)
    all_node_ids = set(nodes_before.keys()) | set(nodes_after.keys())

    for node_id in all_node_ids:
        if node_id not in nodes_before:
            event = {"event_type": "node_added", "node_id": node_id, "location": filepath}
            events.append(event)
        elif node_id not in nodes_after:
            event = {"event_type": "node_removed", "node_id": node_id, "location": filepath}
            events.append(event)
        elif nodes_before[node_id] != nodes_after[node_id]:
            event = {"event_type": "node_modified", "node_id": node_id, "location": filepath}
            # Placeholder for deeper diff logic
            events.append(event)
    return events
EOF
print_success "Modular SVCS tool created."

# 7. Set up Python Virtual Environment for the tool
print_info "Setting up Python virtual environment in '$VENV_DIR'..."
python3 -m venv "$VENV_DIR"
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"
pip install --upgrade pip > /dev/null
print_info "Installing Python dependencies (rich)..."
pip install rich > /dev/null
deactivate
print_success "Python environment is ready."


# 8. Install the Git Hook
print_info "Installing the Git post-commit hook..."
if [ -f "$GIT_HOOK_PATH" ]; then
    print_warning "A post-commit hook already exists. Backing it up to '$GIT_HOOK_PATH.bak'."
    mv "$GIT_HOOK_PATH" "$GIT_HOOK_PATH.bak"
fi

cat << EOF > "$GIT_HOOK_PATH"
#!/bin/sh
#
# Semantic VCS (SVCS) - post-commit hook
# This hook runs the semantic processor after a commit is made.

# Activate the virtual environment and run the processor
# We use the absolute path to ensure it works from any context
VENV_PYTHON="\$(pwd)/$VENV_DIR/bin/python3"
PROCESSOR_MAIN="\$(pwd)/$SVCS_DIR/main.py"

# Run the analysis
"\$VENV_PYTHON" "\$PROCESSOR_MAIN"

# If there was a previous hook, run it too.
if [ -f "\$(dirname "\$0")/post-commit.bak" ]; then
  "\$(dirname "\$0")/post-commit.bak"
fi
EOF

chmod +x "$GIT_HOOK_PATH"
print_success "Git post-commit hook installed successfully."


# 9. Initial Commit
print_info "Making initial commit of the project structure..."
git add .
git commit -m "Initial commit: Setup project structure and SVCS" > /dev/null
print_success "Initial commit created."


# --- Final Instructions ---
echo
echo "------------------------------------------------------------------------"
echo "🎉 Comprehensive SVCS Project Setup Complete! 🎉"
echo
echo "Your new project structure is ready:"
echo "  ./src/       - Your application code"
echo "  ./tests/     - Your tests"
echo "  ./docs/      - Your documentation"
echo "  ./.svcs/     - The semantic analysis tool (hidden)"
echo
echo "From now on, after you run \`git commit\`, the SVCS analyzer will"
echo "automatically run and show you a summary of the semantic changes."
echo
echo "Try it out! Modify the 'greet' function in 'src/main.py', commit it,"
echo "and see the output."
echo "------------------------------------------------------------------------"

#!/usr/bin/env python3
"""
Comprehensive audit of all svcs_repo_* files.
Analyzes usage patterns, imports, CLI interfaces, and overall status.
"""

import os
import ast
import sys
import importlib.util
import subprocess
from pathlib import Path
from datetime import datetime

def extract_functions_and_classes(file_path):
    """Extract function and class definitions from a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        functions = []
        classes = []
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        
        return functions, classes, imports
    except Exception as e:
        return [], [], []

def check_cli_interface(file_path):
    """Check if file has CLI interface (if __name__ == '__main__' or argparse)."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        has_main = '__name__ == "__main__"' in content or '__name__=="__main__"' in content
        has_argparse = 'argparse' in content
        has_click = 'click' in content
        
        return has_main, has_argparse, has_click
    except:
        return False, False, False

def check_importability(file_path):
    """Check if the file can be imported without errors."""
    try:
        module_name = Path(file_path).stem
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None:
            return False, "No module spec"
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return True, "Successfully imported"
    except Exception as e:
        return False, str(e)

def find_usage_in_codebase(filename, search_dirs):
    """Find where this file is imported or referenced in the codebase."""
    basename = Path(filename).stem
    usage_files = []
    
    for search_dir in search_dirs:
        for root, dirs, files in os.walk(search_dir):
            # Skip __pycache__ and .git directories
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', '.svcs']]
            
            for file in files:
                if file.endswith('.py') and file != basename + '.py':
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Check for imports
                        if f'import {basename}' in content or f'from {basename}' in content:
                            usage_files.append(file_path)
                        # Check for references
                        elif basename in content:
                            usage_files.append(file_path)
                    except:
                        continue
    
    return usage_files

def get_file_size_and_date(file_path):
    """Get file size and modification date."""
    try:
        stat = os.stat(file_path)
        size = stat.st_size
        mod_date = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
        return size, mod_date
    except:
        return 0, "Unknown"

def main():
    """Main analysis function."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Find all svcs_repo_* files (excluding mcp directory)
    repo_files = []
    for root, dirs, files in os.walk(base_dir):
        # Skip mcp directory for main analysis
        if 'svcs_mcp' in root:
            continue
        for file in files:
            if file.startswith('svcs_repo_') and file.endswith('.py'):
                repo_files.append(os.path.join(root, file))
    
    print("=== SVCS Repository Files Analysis ===\n")
    print(f"Found {len(repo_files)} svcs_repo_* files\n")
    
    # Search directories for usage analysis
    search_dirs = [base_dir]
    
    for file_path in sorted(repo_files):
        filename = os.path.basename(file_path)
        print(f"📁 {filename}")
        print(f"   Path: {file_path}")
        
        # File info
        size, mod_date = get_file_size_and_date(file_path)
        print(f"   Size: {size} bytes, Modified: {mod_date}")
        
        # Extract code structure
        functions, classes, imports = extract_functions_and_classes(file_path)
        print(f"   Functions: {len(functions)} ({', '.join(functions[:5])}{'...' if len(functions) > 5 else ''})")
        print(f"   Classes: {len(classes)} ({', '.join(classes[:3])}{'...' if len(classes) > 3 else ''})")
        
        # Check CLI interface
        has_main, has_argparse, has_click = check_cli_interface(file_path)
        cli_features = []
        if has_main:
            cli_features.append("__main__")
        if has_argparse:
            cli_features.append("argparse")
        if has_click:
            cli_features.append("click")
        
        print(f"   CLI Interface: {', '.join(cli_features) if cli_features else 'None'}")
        
        # Check importability
        importable, import_msg = check_importability(file_path)
        print(f"   Importable: {'✅ Yes' if importable else '❌ No'} ({import_msg})")
        
        # Find usage in codebase
        usage_files = find_usage_in_codebase(filename, search_dirs)
        print(f"   Usage: {len(usage_files)} references")
        if usage_files:
            for usage_file in usage_files[:3]:  # Show first 3
                rel_path = os.path.relpath(usage_file, base_dir)
                print(f"      - {rel_path}")
            if len(usage_files) > 3:
                print(f"      ... and {len(usage_files) - 3} more")
        
        # Check for API imports
        api_imports = [imp for imp in imports if 'api' in imp.lower()]
        if api_imports:
            print(f"   API Imports: {', '.join(api_imports[:3])}")
        
        print()
    
    print("\n=== Summary ===")
    importable_count = 0
    cli_count = 0
    used_count = 0
    
    for file_path in repo_files:
        filename = os.path.basename(file_path)
        
        # Check stats
        importable, _ = check_importability(file_path)
        if importable:
            importable_count += 1
        
        has_main, has_argparse, has_click = check_cli_interface(file_path)
        if has_main or has_argparse or has_click:
            cli_count += 1
        
        usage_files = find_usage_in_codebase(filename, search_dirs)
        if usage_files:
            used_count += 1
    
    print(f"Total files: {len(repo_files)}")
    print(f"Importable: {importable_count}/{len(repo_files)}")
    print(f"With CLI interface: {cli_count}/{len(repo_files)}")
    print(f"Referenced in codebase: {used_count}/{len(repo_files)}")
    
    print("\n=== Recommendations ===")
    for file_path in repo_files:
        filename = os.path.basename(file_path)
        importable, import_msg = check_importability(file_path)
        usage_files = find_usage_in_codebase(filename, search_dirs)
        has_main, has_argparse, has_click = check_cli_interface(file_path)
        
        status = []
        if not importable:
            status.append("❌ Import issues")
        if not usage_files:
            status.append("⚠️ Unused")
        if has_main or has_argparse or has_click:
            status.append("🖥️ Has CLI")
        if importable and usage_files:
            status.append("✅ Active")
        
        print(f"{filename}: {', '.join(status)}")

if __name__ == "__main__":
    main()

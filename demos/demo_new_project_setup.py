#!/usr/bin/env python3
"""
SVCS New Project Setup Guide

This script demonstrates the complete workflow for starting a new git project
with SVCS semantic analysis and MCP support.
"""

import os
import subprocess
import tempfile
from pathlib import Path

def demonstrate_new_project_setup():
    """Show the complete new project setup workflow."""
    print("🚀 SVCS New Project Setup - Complete Workflow")
    print("=" * 60)
    
    print("\n📋 PREREQUISITES:")
    print("1. Install SVCS MCP globally (once per machine)")
    print("2. Setup global SVCS system (once per machine)")
    print("3. Create new git project")
    print("4. Register project with SVCS")
    print("5. Start coding with semantic tracking!")
    
    # Create a temporary directory to demonstrate
    with tempfile.TemporaryDirectory() as temp_dir:
        demo_project = Path(temp_dir) / "my-new-project"
        demo_project.mkdir()
        
        print(f"\n🗂️  Demo Project: {demo_project}")
        
        # Step 1: Global Installation (show commands)
        print("\n" + "="*60)
        print("STEP 1: GLOBAL INSTALLATION (One-time setup)")
        print("="*60)
        
        print("\n💻 Install SVCS MCP globally:")
        print("   pip install svcs-mcp")
        
        print("\n🌐 Setup global SVCS system:")
        print("   svcs init --global")
        print("   # This creates:")
        print("   #   ~/.svcs/global.db (multi-project database)")
        print("   #   ~/.svcs/hooks/svcs-hook (global git hook)")
        print("   #   ~/.svcs/logs/ (server logs)")
        
        print("\n🖥️  Start MCP server for IDE integration:")
        print("   svcs-mcp-server &")
        print("   # This enables VS Code/Cursor integration")
        
        # Step 2: New Project Creation
        print("\n" + "="*60)
        print("STEP 2: CREATE NEW PROJECT")
        print("="*60)
        
        print(f"\n📁 Create project directory:")
        print(f"   mkdir {demo_project.name}")
        print(f"   cd {demo_project.name}")
        
        # Initialize git
        print(f"\n🔧 Initialize git repository:")
        print("   git init")
        print("   git config user.name 'Your Name'")
        print("   git config user.email 'your.email@example.com'")
        
        # Actually create the git repo for demo
        try:
            subprocess.run(['git', 'init'], cwd=demo_project, check=True, capture_output=True)
            subprocess.run(['git', 'config', 'user.name', 'Demo User'], cwd=demo_project, check=True)
            subprocess.run(['git', 'config', 'user.email', 'demo@example.com'], cwd=demo_project, check=True)
            print("   ✅ Git repository initialized")
        except Exception as e:
            print(f"   ⚠️ Git init demo failed: {e}")
        
        # Step 3: SVCS Registration
        print("\n" + "="*60)
        print("STEP 3: REGISTER WITH SVCS")
        print("="*60)
        
        print("\n🎯 Register project with SVCS:")
        print("   svcs init --name 'My New Project'")
        print("   # This will:")
        print("   #   - Register project in global database")
        print("   #   - Install git hooks (symlinks to global hook)")
        print("   #   - Create local .svcs/config.yaml")
        print("   #   - Enable semantic analysis")
        
        # Step 4: Verify Setup
        print("\n📊 Verify SVCS setup:")
        print("   svcs status")
        print("   # Shows registration and hook status")
        
        print("\n📋 List all SVCS projects:")
        print("   svcs list")
        print("   # Shows this project among all registered projects")
        
        # Step 5: IDE Integration
        print("\n" + "="*60)
        print("STEP 4: IDE INTEGRATION")
        print("="*60)
        
        print("\n🔌 Connect VS Code/Cursor to MCP server:")
        print("   1. Install MCP extension in your IDE")
        print("   2. Configure MCP server: svcs-mcp-server")
        print("   3. Start asking semantic questions!")
        
        print("\n💬 Example IDE queries:")
        print("   - 'Register this project for semantic tracking'")
        print("   - 'Show me all my registered projects'")
        print("   - 'What are the recent code evolution patterns?'")
        print("   - 'Analyze the semantic changes in my last commit'")
        
        # Step 6: Development Workflow
        print("\n" + "="*60)
        print("STEP 5: DEVELOPMENT WITH SEMANTIC TRACKING")
        print("="*60)
        
        print("\n📝 Create initial code:")
        print("   echo 'print(\"Hello SVCS!\")' > main.py")
        print("   git add main.py")
        print("   git commit -m 'Initial commit with SVCS'")
        
        # Actually create a demo file
        demo_file = demo_project / "main.py"
        demo_file.write_text('print("Hello SVCS!")\n')
        
        try:
            subprocess.run(['git', 'add', 'main.py'], cwd=demo_project, check=True)
            subprocess.run(['git', 'commit', '-m', 'Initial commit with SVCS'], cwd=demo_project, check=True)
            print("   ✅ Demo commit created")
        except Exception as e:
            print(f"   ⚠️ Demo commit failed: {e}")
        
        print("\n🔍 What happens on commit:")
        print("   1. Git triggers post-commit hook")
        print("   2. ~/.svcs/hooks/svcs-hook executes")
        print("   3. Hook detects project and routes to SVCS")
        print("   4. SVCS analyzes semantic changes")
        print("   5. Results stored in global database")
        print("   6. Available for IDE queries instantly!")
        
        # Step 7: Ongoing Development
        print("\n" + "="*60)
        print("STEP 6: ONGOING DEVELOPMENT")
        print("="*60)
        
        print("\n🔄 Normal development workflow:")
        print("   # Just code normally - SVCS works automatically!")
        print("   vim main.py           # Edit code")
        print("   git add main.py       # Stage changes") 
        print("   git commit -m 'msg'   # Commit (triggers SVCS analysis)")
        
        print("\n📈 Query evolution from IDE:")
        print("   - 'Show performance improvements this week'")
        print("   - 'What functions were refactored recently?'")
        print("   - 'Compare code quality trends across projects'")
        print("   - 'Find similar patterns in other projects'")
        
        print("\n🧹 Project maintenance:")
        print("   svcs stats            # Show project statistics")
        print("   svcs remove           # Unregister (if needed)")
        
        # Summary
        print("\n" + "="*60)
        print("🎉 SETUP COMPLETE!")
        print("="*60)
        
        print("\n✅ Your new project now has:")
        print("   • Automatic semantic analysis on every commit")
        print("   • Global database integration")
        print("   • IDE integration via MCP server")
        print("   • Cross-project evolution insights")
        print("   • Natural language query capabilities")
        
        print("\n🚀 Benefits:")
        print("   • Zero ongoing maintenance")
        print("   • Automatic code evolution tracking")
        print("   • Portfolio-wide insights")
        print("   • IDE-integrated semantic queries")
        print("   • Learning from past coding patterns")


if __name__ == "__main__":
    demonstrate_new_project_setup()

# 🚀 SVCS New Project Setup - Quick Start Guide

## When you start a completely new git project with SVCS and MCP support:

### 🏁 **One-Time Machine Setup** (Do this once per machine)

```bash
# 1. Install SVCS MCP globally
pip install svcs-mcp

# 2. Setup global SVCS system 
svcs init --global
# ✅ Creates ~/.svcs/global.db and ~/.svcs/hooks/svcs-hook

# 3. Start MCP server for IDE integration (optional, for background)
svcs-mcp-server &
# ✅ Enables VS Code/Cursor to connect via MCP
```

---

### 📁 **For Each New Project** (Quick 2-command setup)

```bash
# 1. Create and initialize your git project (normal git workflow)
mkdir my-awesome-project
cd my-awesome-project
git init
git config user.name "Your Name" 
git config user.email "your.email@example.com"

# 2. Register with SVCS (ONE command does everything!)
svcs init --name "My Awesome Project"
# ✅ Registers project in global database
# ✅ Installs git hooks (symlinks to global hook)
# ✅ Creates local .svcs/config.yaml
# ✅ Enables automatic semantic analysis

# 3. Verify everything is working
svcs status
# Should show: ✅ Registered with SVCS, ✅ Git hooks installed
```

---

### 💻 **Start Developing** (Just code normally!)

```bash
# Create your code
echo 'def hello(): print("Hello SVCS!")' > main.py

# Commit normally - SVCS analyzes automatically!
git add main.py
git commit -m "Initial implementation"
# 🔍 SVCS hook automatically analyzes semantic changes

# Continue developing normally
vim main.py           # Edit your code
git add main.py       
git commit -m "Add error handling"  # SVCS tracks evolution
```

---

### 🔍 **Query Your Code Evolution**

#### From Command Line:
```bash
svcs list                    # See all your SVCS projects
svcs stats                   # Get project statistics  
svcs query "performance"     # Natural language queries (coming soon)
```

#### From VS Code/Cursor (with MCP):
- "Show me all my registered projects"
- "What semantic changes happened in my last commit?"
- "Compare evolution patterns across my projects"
- "Find functions that were refactored recently"

---

## 🎯 **What You Get Automatically**

### ✅ **Zero Maintenance Semantic Tracking**
- Every `git commit` automatically triggers semantic analysis
- Code evolution patterns stored in global database
- Cross-project insights and learning
- Natural language query capabilities

### ✅ **IDE Integration**
- VS Code/Cursor can ask semantic questions about your code
- Real-time evolution insights
- Portfolio-wide code analysis
- Pattern recognition across projects

### ✅ **Global Intelligence**
- All projects in one centralized system
- Learn from patterns across your entire codebase
- Track architectural decisions over time
- Identify best practices and anti-patterns

---

## 🛠️ **Troubleshooting**

### Check Project Status:
```bash
svcs status
# Should show:
# 📋 Registration: ✅ Registered with SVCS
# 🔗 Git Hooks:
#   post-commit: ✅ svcs_installed
#   pre-commit: ✅ svcs_installed
```

### List All Projects:
```bash
svcs list
# Shows all projects registered with SVCS
```

### Remove from SVCS (if needed):
```bash
svcs remove
# ✅ Unregisters project
# ✅ Removes git hooks  
# ✅ Restores original hooks (if any)
```

---

## 🎉 **That's It!**

Your new project now has:
- **Automatic semantic analysis** on every commit
- **Global database integration** with all your projects
- **IDE integration** for natural language queries
- **Zero ongoing maintenance** required

Just code normally and let SVCS track your code evolution automatically! 🚀

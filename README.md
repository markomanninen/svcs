# SVCS - Semantic Version Control System

SVCS tracks semantic meaning in code changes beyond traditional line-by-line diffs. It uses a 5-layer analysis system combining Abstract Syntax Tree (AST) analysis with optional AI-powered semantic understanding.

## Table of Contents

- [Key Features](#-key-features)
- [Why SVCS? Value Proposition](#-why-svcs-value-proposition)
- [Use Cases & Creative Applications](#-use-cases--creative-applications)
- [5-Layer Analysis Architecture](#-5-layer-analysis-architecture)
- [Language Support](#-language-support)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Guide](#-usage-guide)
- [Project Management & Cleanup](#-project-management--cleanup)
- [Database Maintenance](#-database-maintenance)
- [Module Documentation](#-module-documentation)
- [MCP Server Interface](#-mcp-server-interface)
- [Development Setup](#-development-setup)
- [System Requirements](#-system-requirements)
- [Limitations](#-limitations)
- [Future Development](#-future-development)

## 🌟 **Key Features**

- **🧠 5-Layer Semantic Analysis** - From AST parsing to optional AI understanding
- **🤖 Model Context Protocol (MCP) Server** - Modern AI integration architecture
- **🌍 Multi-Language Support** - Python (complete), PHP (modern with Tree-sitter), JavaScript/TypeScript (AST-based)
- **� Git-Integrated Team Architecture** - Repository-local semantic data with git notes for collaboration
- **🌿 Branch-Aware Analysis** - Track semantic changes across branches with comparison tools
- **⚡ Real-Time Git Hooks** - Automatic semantic analysis on commit, merge, and branch switch
- **�💬 Conversational Interface** - Natural language queries about code evolution
- **📊 Analytics & Visualization** - Web dashboard and quality insights
- **🔧 CI/CD Integration** - Automated quality gates and PR analysis
- **🗂️ Multi-Repository Management** - Track multiple projects with unified interface

## 🚀 **Why SVCS? Value Proposition**

### **Beyond Traditional Git: The Semantic Gap**

While Git tracks *what* changed (lines, files), SVCS understands *what those changes mean*:

- **Git shows**: `+def calculate_score(items): return sum(x.value * x.weight for x in items)`
- **SVCS reveals**: "Added weighted calculation algorithm, introduced functional programming pattern, improved mathematical abstraction"

### **Complementing AI Code Review Tools**

Modern AI agents (GitHub Copilot, Claude, GPT) excel at immediate code analysis but lack **temporal context**. SVCS provides the missing historical dimension:

| **Traditional AI Agents** | **SVCS + AI Agents** |
|----------------------------|----------------------|
| ✅ Analyze current code | ✅ **+ Track evolution patterns** |
| ✅ Suggest improvements | ✅ **+ Learn from past decisions** |
| ✅ Detect code smells | ✅ **+ Identify improvement trends** |
| ❌ No historical context | ✅ **Rich semantic history** |
| ❌ No team learning | ✅ **Rich semantic insights** |

### **The SVCS Advantage**

1. **Semantic Memory**: Your codebase remembers why changes were made
2. **Pattern Recognition**: Identify successful architectural decisions over time
3. **Personal Code Intelligence**: Learn from your own coding evolution
4. **AI Enhancement**: Provide LLM agents with rich context for better assistance
5. **Educational Tool**: Deep insights into programming evolution and best practices

## 🎯 **Use Cases & Creative Applications**

### **🤖 AI Agent Enhancement**
SVCS + MCP provides rich semantic context to AI assistants, enabling them to understand your project's evolution patterns and provide context-aware suggestions based on historical changes.

### **📚 Code Learning & Investigation**
- **Programming Skill Development**: Track your coding evolution and identify improvement patterns
- **Code Archaeology**: Investigate complex bugs by tracing when complexity was introduced
- **Personal Knowledge Base**: Build semantic understanding of your codebase evolution

### **🔗 Git Integration**
Every semantic event links to its exact git commit, enabling complete traceability. Query specific commits, view diffs, and understand the relationship between semantic changes and actual code changes.

### **🤝 Team Collaboration** (Planned - Git-Integrated)
SVCS will integrate directly with git's team workflow for natural semantic collaboration:

#### **Feature Branch → PR → Merge Workflow**
1. **Developer creates feature branch** → inherits semantic context from main branch
2. **Commits with semantic analysis** → analysis stored as git notes attached to commits  
3. **Pushes feature branch** → git notes automatically included, semantic data available for review
4. **Code review enhanced** → reviewers can query semantic changes: `svcs diff-branches main..feature/auth`
5. **PR merge to main** → semantic data automatically merges, team gets integrated semantic history
6. **Team pulls main** → everyone automatically receives shared semantic intelligence

#### **SVCS-Enhanced Code Review**
```bash
# Reviewer queries semantic impact of PR:
svcs search --branch feature/user-auth --event-type "security_improvement"
svcs semantic-impact feature/user-auth    # Show semantic changes this PR introduces
svcs merge-preview feature/user-auth      # Preview semantic impact of merge

# Compare semantic evolution between branches:
svcs diff-branches main..feature/user-auth
# + Added: class:AuthService (security enhancement)
# + Added: function:validateToken (error handling improvement)  
# ~ Modified: class:UserController (performance optimization)
```

#### **Team Semantic Intelligence**
```bash
# After merge, query collective team intelligence:
svcs team-activity --since "1 week"       # Recent semantic changes across team
svcs cross-developer-evolution class:AuthService  # Track class evolution across developers
svcs search --author "Alice" --event-type "performance_optimization"
```

**Benefits**: Semantic data follows exact same workflow as source code through git's collaboration mechanisms - no separate infrastructure needed, works with any git hosting platform.

### **🏢 Enterprise Applications**
- **Code Review Enhancement**: Find exemplary refactoring examples for training
- **Technical Debt Management**: Track debt accumulation and improvement patterns  
- **CI/CD Integration**: Semantic-aware testing and deployment risk assessment
- **Quality Gates**: Block deployments based on semantic complexity spikes

### **💡 Research & Analytics**
- **Pattern Recognition**: Identify successful architectural decisions over time
- **Code Metrics**: Track "semantic velocity" and architectural coherence
- **Multi-Project Insights**: Compare evolution patterns across your personal projects

## 🧠 5-Layer Analysis Architecture

SVCS employs a multi-layer analysis system:

### **Core Layers (1-4): Structural & Syntactic Analysis**
- **Layer 1-2**: AST parsing and structural changes (functions, classes, imports)
- **Layer 3-4**: Behavioral patterns (control flow, data access, complexity)

### **Layer 5a: Rule-Based Pattern Recognition** 
- Pattern detection using programmatic rules
- Identifies architectural and quality improvements
- Detects error handling patterns and functional programming adoption

### **Layer 5b: LLM-Powered Analysis** 🤖
- **Requires Google Gemini API key** (`GOOGLE_API_KEY` environment variable)
- **Intelligent Filtering**: Only analyzes non-trivial, complex changes
- **Without API key**: SVCS uses layers 1-5a only
- Detects abstract concepts like:
  - Architecture improvements and design pattern adoption
  - Performance optimizations and maintainability enhancements  
  - Code readability improvements and abstraction refinements
  - Error handling strategy changes

## 🌍 Language Support

| Language | Extensions | Support Level | Parser Technology | Features |
|----------|------------|---------------|-------------------|----------|
| **Python** | `.py`, `.pyw`, `.pyi` | **Complete** | Native AST | Full AST analysis, 31+ semantic event types, decorators, async/await, generators, comprehensions, type annotations |
| **PHP** | `.php`, `.phtml`, `.php3`, `.php4`, `.php5`, `.phps` | **Modern** | Tree-sitter (primary) + phply (fallback) | Modern PHP 7.4+/8.x features (enums, attributes, typed properties), legacy PHP 5.x-7.3 support, classes, interfaces, traits, methods, properties, namespaces, inheritance tracking |
| **JavaScript** | `.js` | **AST-based** | esprima AST parser + regex fallback | ES6+ classes, arrow functions, async/await, inheritance changes, method signatures, constructor parameters, import/export tracking |
| **TypeScript** | `.ts` | **AST-based** | esprima AST parser + regex fallback | Same as JavaScript with TypeScript syntax support |

### **Parser Architecture & Robustness**

SVCS uses a **multi-tier fallback system** for maximum reliability:

#### **PHP Analysis**
1. **Primary**: Tree-sitter PHP parser (supports PHP 7.4+ and 8.x)
   - Modern features: enums, attributes, typed properties, union types
   - Accurate AST-based parsing with full semantic understanding
2. **Fallback**: phply parser (PHP 5.x-7.3 legacy support)
   - Maintains compatibility with older codebases
3. **Final Fallback**: Regex parsing for basic structural detection

#### **JavaScript/TypeScript Analysis** 
1. **Primary**: esprima AST parser with tolerance mode
   - Full ES6+ syntax support including classes, arrow functions, async/await
   - Detailed parameter and inheritance tracking
   - Supports both JavaScript (.js) and TypeScript (.ts) syntax
2. **Fallback**: Enhanced regex parsing with modern JS patterns
   - Comprehensive pattern matching for various function declarations

#### **Detected Change Types by Language**

**PHP (Modern Support)**:
- ✅ Classes, interfaces, traits, enums (PHP 8.1+)
- ✅ Method signature changes, property type changes
- ✅ Inheritance tracking (`extends`, `implements`)
- ✅ Modern features: attributes (PHP 8.0+), typed properties
- ✅ Namespace and use statement tracking
- ✅ Visibility modifier changes (`public`, `private`, `protected`)

**JavaScript/TypeScript (AST-based Support)**:
- ✅ Function declarations, expressions, and arrow functions
- ✅ Class inheritance tracking (`extends` relationships)
- ✅ Constructor parameter changes
- ✅ Method additions/removals within classes
- ✅ Variable declarations with function assignments
- ✅ ES6+ syntax support (classes, arrow functions, async/await)
- ✅ TypeScript syntax compatibility
- ✅ Variable scope and declaration changes

**Note**: Python provides the most comprehensive semantic analysis. PHP and JavaScript now offer robust structural and semantic change detection suitable for production use in git hooks.

## 🛠️ **Installation**

**Note**: SVCS uses symbolic links for git hooks and is designed for Unix-based systems (Linux, macOS). Windows support requires WSL.

### **1. Install with Virtual Environment** (Recommended)

```bash
# Clone the repository
git clone https://github.com/markomanninen/svcs.git
cd svcs

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows WSL: venv/bin/activate

# Install MCP server
cd svcs_mcp
pip install -e .

# Install enhanced language parsing dependencies
pip install tree-sitter tree-sitter-php esprima

# Install core SVCS dependencies
pip install -r ../requirements.txt

# Set up Google API key for Layer 5b AI features (optional)
export GOOGLE_API_KEY="your_gemini_api_key_here"

# Verify installation
cd ..
svcs --help
```

### **2. Configure MCP Server in VS Code**

Add to your VS Code `settings.json`:

```json
{
  "mcp": {
    "servers": {
      "svcs": {
        "command": "python3",
        "args": ["/path/to/svcs/svcs_mcp/mcp_server.py"],
        "env": {}
      }
    }
  }
}
```

> **💡 Note**: For enhanced PHP and JavaScript/TypeScript support, ensure you have installed the language parsing dependencies: `tree-sitter`, `tree-sitter-php`, and `esprima`. Without these, SVCS will fall back to basic regex parsing.

## 🚀 **Quick Start**

### **Option A: Repository-Local SVCS** (Recommended for New Projects)

**Git-integrated team collaboration with repository-local storage:**

```bash
# Navigate to your git project
cd your-project

# Initialize repository-local SVCS (includes git hooks)
python3 svcs_local_cli.py init

# Make changes and commit (automatic semantic analysis)
echo "def new_function(): pass" >> code.py
git add code.py
git commit -m "Add new function"
# 🔍 SVCS: Analyzing semantic changes...
# ✅ SVCS: Stored 2 semantic events
# 📝 SVCS: Semantic data saved as git notes

# View semantic evolution
python3 svcs_local_cli.py events --limit 5

# Sync semantic data with team (push/pull git notes)
python3 svcs_local_cli.py notes sync
git push origin main  # Semantic notes automatically included
```

### **Option B: Global SVCS** (Legacy/Existing Projects)

**Traditional global database approach:**

```bash
# Navigate to your git project
cd your-project

# Register with SVCS MCP server
svcs init --name "My Project" .
```

### **2. Make Changes and Commit** (Both Architectures)

```bash
# Create test files in different languages
echo "def hello(): return 'world'" > test.py
echo "<?php function hello() { return 'world'; } ?>" > test.php
echo "function hello() { return 'world'; }" > test.js

git add test.py test.php test.js
git commit -m "Add hello function in multiple languages"

# SVCS automatically detects and analyzes all supported languages
# You'll see semantic analysis output for each file in the terminal
```

### **3. Query Your Code Evolution**

**Repository-Local SVCS:**
```bash
# View semantic events for current branch
python3 svcs_local_cli.py events --limit 10

# View git notes with semantic data
python3 svcs_local_cli.py notes show

# Check repository status
python3 svcs_local_cli.py status
```

**Global SVCS:**
```bash
# Via MCP tools in VS Code/Cursor:
> list svcs projects
> show stats for my project

# Via command line:
svcs search --limit=20
svcs discuss --query "summarize my project"  # Enhanced CLI integration
svcs query "show recent performance changes" # One-shot queries
python3 svcs_discuss.py  # Direct script (legacy)
```

## 📖 **Usage Guide**

### **Core SVCS CLI (`svcs`)**

```bash
# Project management (Global architecture)
svcs init --name "My Project" .              # Register project
svcs list                                    # List projects
svcs stats                                   # Project statistics
svcs recent --days=7                         # Recent activity

# Search semantic history
svcs search --limit=20                       # Basic search
svcs search --author="John Doe"              # Filter by author
svcs search --event-types="node_signature_changed"  # Filter by event type
svcs evolution "func:greet"                  # Track specific function
svcs search --min-confidence=0.8             # High-confidence AI insights

# Database maintenance
svcs cleanup --show-stats                    # Show database status
svcs prune --all-projects                    # Clean orphaned data
```

### **Repository-Local SVCS CLI (`svcs`)**

**New git-integrated team collaboration interface:**

```bash
# Repository initialization and management
svcs init                              # Initialize SVCS for current repository
svcs status                            # Show repository SVCS status
svcs remove                            # Remove SVCS from repository

# Semantic analysis and events
svcs events --limit 10                 # List semantic events for current branch
svcs events --branch feature/auth      # Events for specific branch
svcs analyze --commit abc123           # Manually analyze a commit

# Git notes team collaboration
svcs notes sync                        # Sync semantic notes to remote
svcs notes fetch                       # Fetch semantic notes from remote
svcs notes show --commit abc123        # View semantic note for commit

# Migration from global architecture
svcs migrate list                      # List projects for migration
svcs migrate migrate                   # Migrate current project to local
```

### **Conversational Interface**

Natural language queries about code evolution available through multiple interfaces:

```bash
# CLI Integration (New!)
svcs discuss                            # Start interactive session
svcs discuss --query "summarize recent changes"  # Start with initial query
svcs query "show performance optimizations"      # One-shot query

# Direct script (Legacy)
export GOOGLE_API_KEY="your_key"
python3 svcs_discuss.py

# Example queries:
"What performance optimizations were made last week?"
"Show me all dependency changes by Alice"
"How has the DataProcessor class evolved?"
"Which commits had the most significant semantic changes?"
"Show me only the changes to auth.py in commit abc123"
```

### **Web Dashboard (`svcs_web.py`)**

Generate interactive HTML dashboards:

```bash
python3 svcs_web.py
# Creates: svcs_dashboard.html (open in browser)
```

**Usage**: Open the generated `svcs_dashboard.html` file in your web browser to explore:
- Interactive timeline of semantic changes
- Network graphs of code relationships  
- Quality metrics visualization
- Developer activity heatmaps

### **Interactive Web Dashboard**

Launch a full-featured web interface for exploring SVCS data:

```bash
# Quick start
./start_dashboard.sh

# Manual start
source .svcs/venv/bin/activate
pip install Flask Flask-CORS
python3 svcs_web_server.py
```

**Access**: Open `http://127.0.0.1:8080` in your browser

**Features**:
- 🔍 **Semantic Search**: Advanced filtering and quick pattern searches
- 📝 **Git Integration**: View changed files, diffs, and commit summaries
- 📈 **Evolution Tracking**: Track specific functions/classes over time
- 🎯 **Pattern Analysis**: AI-detected performance, architecture, and quality patterns
- 📋 **System Logs**: Monitor LLM inference and error logs
- 🗂️ **Project Management**: 
  - Multi-project support and statistics
  - Project registration and unregistration
  - **Soft Delete** (unregister): Remove from tracking, keep data for recovery
  - **Hard Delete** (purge): Permanently remove all project data
  - Cleanup utilities with inactive project detection
  - Database statistics and optimization tools
- 📊 **Analytics**: Quality trends and comprehensive reporting
- 🔧 **Database Maintenance**: Clean orphaned data and optimize storage

**Project Management Safety Features**:
- **Confirmation dialogs** for destructive operations
- **Clear distinction** between soft and hard delete options
- **Recovery guidance** for accidentally removed projects
- **Cleanup insights** showing inactive projects and wasted storage

See `docs/INTERACTIVE_DASHBOARD_GUIDE.md` for detailed usage instructions.

### **Analytics & Quality Reports**

```bash
# Generate comprehensive analytics report
python3 svcs_analytics.py

# Quality trend analysis
python3 svcs_quality.py

# CI/CD integration
python3 svcs_ci.py --pr-analysis --target=main
```

## 📊 **Database Maintenance**

SVCS includes database maintenance tools to keep semantic data clean and optimized. When git history is modified (rebasing, squashing, force-pushing), some semantic data may become "orphaned" - linked to commits that no longer exist.

**Available through**:
- Interactive web dashboard (recommended)
- CLI commands (`svcs prune`, `svcs cleanup`)
- MCP server integration

**Best Practices**:
- Always backup before major operations: `cp ~/.svcs/global.db ~/.svcs/global.db.backup`
- Use soft delete by default: `svcs remove /path/to/project` (preserves data)
- Review inactive projects before purging: `svcs cleanup --show-inactive`

For comprehensive maintenance documentation, see [`docs/DATABASE_MAINTENANCE_GUIDE.md`](docs/DATABASE_MAINTENANCE_GUIDE.md).

## �📚 **Module Documentation**

### **Core Analysis Engine**

#### **`svcs` - CLI Interface**
- Command-line interface with rich terminal output
- Project management (init, list, stats, recent)
- Advanced semantic search with filtering capabilities
- Event type and confidence-based queries
- Author and time-based filtering
- Evolution tracking for specific code elements
- Database maintenance operations (prune, cleanup)

#### **`svcs_discuss.py` - Conversational AI Interface**
- Natural language query processing
- Context-aware responses about code evolution
- Integration with all SVCS data layers
- **Requires**: `GOOGLE_API_KEY` environment variable

### **Analytics & Insights**

#### **`svcs_analytics.py` - Data Analytics Engine**
- Temporal analysis of semantic changes
- Developer contribution patterns
- Code quality trend analysis
- Event type distribution statistics

#### **`svcs_quality.py` - Code Quality Insights**
- Error handling pattern improvements
- Code maintainability trends
- Performance optimization detection
- Technical debt accumulation/reduction

#### **`svcs_web.py` - Web Dashboard Generator**
- Interactive HTML dashboards for visualizing semantic evolution
- Timeline visualizations
- Network graphs of code relationships
- Quality metrics charts

### **CI/CD Integration**

#### **`svcs_ci.py` - Continuous Integration Support**
- **PR Analysis**: Semantic impact assessment of pull requests
- **Quality Gates**: Automated quality checks based on semantic patterns
- **Trend Monitoring**: Continuous quality trend analysis
- **Report Generation**: Automated reporting for stakeholders

### **Multi-Language Support**

#### **`svcs_multilang.py` - Advanced Language Extension Framework**
- **Production-ready multi-language semantic analysis** with robust fallback systems
- **Python**: Complete support (.py, .pyx, .pyi) - Functions, classes, async/await, decorators, comprehensions
- **PHP**: Complete modern support (PHP 7.4+/8.x) with Tree-sitter parser + phply legacy fallback
- **JavaScript/TypeScript**: AST-based analysis with esprima parser + intelligent regex fallback
- **Extensible architecture**: Easy addition of new language analyzers with standardized interface

#### **Real-world Git Hook Integration**
- **Tested in production scenarios**: Multi-language analysis in git post-commit hooks
- **Error resilience**: Graceful handling of syntax errors, missing parsers, binary files
- **Performance optimized**: Efficient parsing with minimal git hook overhead

## 🤖 **MCP Server Interface**

Modern AI-integrated interface for multiple projects:

### **Available MCP Tools**

#### **Project Management**
- `list_projects` - List all registered SVCS projects
- `register_project` - Register new project for tracking
- `unregister_project` - Soft delete project (mark inactive, preserve data)
- `get_project_statistics` - Get semantic statistics for project

#### **Semantic Analysis**
- `query_semantic_events` - Query events with filtering
- `get_recent_activity` - Get recent semantic changes
- `search_semantic_patterns` - AI-powered pattern search
- `get_filtered_evolution` - Track specific code element evolution
- `search_events_advanced` - Advanced filtering and search
- `analyze_current_commit` - Analyze most recent commit

#### **Git Integration**
- `get_commit_changed_files` - List files changed in a specific commit
- `get_commit_diff` - Get git diff for a commit (optionally filtered to specific file)
- `get_commit_summary` - Comprehensive commit information including metadata, files, and semantic events

#### **Database Maintenance**
- `prune_orphaned_data` - Remove semantic data for commits no longer in git history
- `debug_query_tools` - Diagnostic information for database debugging

### **Usage in MCP-Compatible IDEs**

In VS Code, Cursor, or other MCP-compatible editors:

```
# Project management
> list svcs projects
> register this project with SVCS
> show stats for /path/to/project

# Semantic queries  
> find performance improvements in my project
> show recent architecture changes
> analyze error handling patterns

# Git integration
> get changed files for commit abc123
> show me the diff for commit abc123
> summarize commit abc123
```

### **MCP Server Integration (AI Chat Interfaces)**

SVCS provides a fully integrated **Model Context Protocol (MCP) server** for AI chat interfaces like Claude and VS Code Chat. The MCP server enables semantic code analysis through natural conversation.

#### **🚀 MCP Server Management**

```bash
# Start MCP server for IDE integration
svcs mcp start                         # Start in foreground (see output)
svcs mcp start --background            # Start in background

# Server management
svcs mcp stop                          # Stop the MCP server
svcs mcp status                        # Check if server is running
svcs mcp restart                       # Restart the server
svcs mcp restart --background          # Restart in background

# Monitoring and debugging
svcs mcp logs                          # View recent server logs
svcs mcp logs --lines 100              # View more log lines
svcs mcp logs --follow                 # Follow logs in real-time
```

#### **🛠️ MCP Server Usage**

**For Development/Testing:**
```bash
svcs mcp start                         # Start in foreground to see output
# Use the tools in Claude/VS Code
svcs mcp stop                          # Stop when done
```

**For Production/IDE Integration:**
```bash
svcs mcp start --background            # Start and detach
svcs mcp status                        # Check if running
svcs mcp logs                          # Check for any issues
```

**After Code Changes:**
```bash
svcs mcp restart --background          # Restart to apply changes
```

#### **🔧 Available MCP Tools (11 Total)**

When the MCP server is running, these tools are available in Claude/VS Code:

**📊 Project Overview & Statistics**
- **list_projects** - List all registered SVCS repositories
- **get_project_statistics** - Get semantic statistics for a project

**🔍 Semantic Event Queries**
- **query_semantic_events** - Query semantic events from database
- **search_events_advanced** - Advanced search with comprehensive filtering
- **get_recent_activity** - Get recent project activity with filtering
- **search_semantic_patterns** - Search for AI-detected semantic patterns

**📈 Code Evolution Tracking**
- **get_filtered_evolution** - Get evolution history for specific functions/classes

**🤖 Conversational Interface**
- **conversational_query** - Natural language interface for semantic analysis

**📝 Commit Analysis**
- **get_commit_summary** - Comprehensive commit analysis including semantic events
- **get_commit_changed_files** - List files changed in specific commits

**🔧 Debug & Diagnostics**
- **debug_query_tools** - Diagnostic information for troubleshooting

#### **💬 Example MCP Queries**

Once the MCP server is running, you can ask natural language questions in Claude or VS Code:

> *"Show me all registered projects"*

> *"What semantic patterns were detected in the last week?"*

> *"Get a summary of commit abc123 including all semantic events"*

> *"How has the authenticate function evolved over time?"*

> *"Show me recent performance optimization patterns with high confidence"*

> *"What files were changed in the last commit and what semantic events occurred?"*

#### **🔗 Integration with Claude/VS Code**

The MCP server automatically integrates with:
- **Claude Desktop** - Add SVCS server to your MCP configuration
- **VS Code with MCP Extension** - Connect to local SVCS server
- **Any MCP-compatible AI interface** - Standard Model Context Protocol support

**Log Location:** `~/Library/Logs/Claude/mcp-server-svcs.log` (macOS)

## 🧑‍💻 **Development Setup**

```bash
# Clone and setup development environment
git clone https://github.com/markomanninen/svcs.git
cd svcs

# Create development environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .
pip install -e svcs_mcp/

# Run tests
python3 -m pytest tests/
python3 tests/test_svcs_complete_5layer.py

# Install development dependencies
pip install black pytest pre-commit
```

## 🖥️ **System Requirements**

### **Core Requirements**
- Python 3.8+ (recommended: Python 3.11+)
- Git 2.0+ 
- Unix-based system (Linux, macOS) or Windows WSL
- 4GB+ RAM (for AI analysis)
- 1GB+ disk space (for databases and logs)

### **Dependencies**
```bash
# Essential packages (auto-installed)
rich>=10.0.0              # Terminal UI and formatting
click>=8.0.0               # CLI framework
sqlite3                    # Database (built-in)

# Optional but recommended for Layer 5b
google-generativeai>=0.3.0 # Gemini AI integration

# MCP Server dependencies
mcp>=0.1.0                 # Model Context Protocol
```

### **API Requirements**
- **Google API Key** - Required for Layer 5b AI analysis and conversational interface
  - Get one at [Google AI Studio](https://makersuite.google.com/app/apikey)
  - Free tier: 1000 requests/day
  - Without API key: SVCS uses layers 1-5a only

### **Performance Characteristics**
- **Layer 1-4 analysis**: ~100-200ms per commit (fast, always runs)
- **Layer 5a analysis**: ~200-500ms per commit (rule-based patterns)
- **Layer 5b analysis**: ~2-10s per commit (only for complex changes, requires API key)
- **MCP server startup**: ~500ms (global database initialization)
- **Database queries**: ~10-50ms (optimized with indices)

**TODO**: Real benchmarks needed for production workloads.

### **Resource Usage**
**TODO**: Comprehensive testing needed for:
- Memory usage patterns across different project sizes
- Disk space requirements for long-term history
- Network usage for API calls
- CPU utilization profiles

## ⚠️ **Limitations**

### **Current Limitations**
- **Large Context Analysis**: SVCS analyzes individual commits/files, not whole application stack impacts
- **Cross-Project Dependencies**: Limited visibility into changes affecting multiple projects
- **Real-time Analysis**: Git hook-based, requires commits to trigger analysis
- **Windows Support**: Requires WSL due to symbolic link usage for git hooks
- **API Dependency**: Layer 5b features require external Google API

### **Language Support Status**
- **Python**: Comprehensive semantic analysis with 31+ event types
- **PHP**: Modern language support with Tree-sitter parsing (PHP 7.4+/8.x) and phply fallback
- **JavaScript/TypeScript**: AST-based analysis using esprima parser with comprehensive syntax support
- **Cross-language projects**: Multi-language repository support for mixed codebases

### **Scalability Considerations**
- SQLite database may not scale to very large repositories
- LLM API costs can accumulate with frequent complex changes
- Git hook approach may impact commit performance on large files

## 🔮 **Future Development**

### **Time Crystal VCS Origin**
This project originated from the "Time Crystal VCS" concept - a science fiction-like invention by ChatGPT O3 (see `docs/TimeCrystalVCS.pdf`), from which the practical implementation was determined and developed as an AI-assisted coding project initiated by Marko T. Manninen, 06/2025, in roughly one day using:
- Gemini 2.5 Pro (initial planning and setup script)
- VS Code Claude 4 Preview agent (main coding)
- A code contribution from OpenAI O3 (debug persistent click cli --event-types parsing problem)

## 🔮 **Future Development**

### **Current Limitations**

SVCS is currently designed as a **single-user system**:
- Local database (`~/.svcs/global.db`) stores data only on your machine
- No built-in sharing or synchronization capabilities
- Projects are managed locally per user
- No team collaboration features yet implemented

### **Current Limitations**

SVCS is currently in transition between architectures:
- **Global Architecture** (current): Local database (`~/.svcs/global.db`) for single-user operation
- **Repository-Local Architecture** (new): Git-integrated team collaboration with repository-local storage

The new repository-local architecture has been implemented and is ready for testing:
- Repository-local semantic database (`.svcs/semantic.db`)
- Git notes integration for team sharing
- Branch-aware semantic analysis
- Repository-specific git hooks

### **Migration to Git-Integrated Team Features**

✅ **Implemented**: Repository-local architecture with git notes integration
- Repository-local database storage in `.svcs/semantic.db`
- Semantic data stored as git notes attached to commits
- Branch-aware semantic analysis and tracking
- Repository-specific git hooks for automatic analysis
- Team collaboration through git push/pull workflow
- Migration tools from global to repository-local storage

🚧 **In Progress**: Integration with existing SVCS components
- Connecting to existing semantic analyzer modules
- Updating MCP server for repository-local mode
- Web dashboard integration for local repositories

### **Planned Git-Integrated Team Features**

We're designing **git-native team collaboration** that integrates with existing git workflows:

#### **Git-Integrated Team Collaboration** (Planned)
- **Git Notes Integration**: Semantic analysis stored as git notes attached to commits
- **Automatic Sync**: Semantic data travels with commits via push/pull operations  
- **Branch-Aware Analysis**: Semantic evolution tracked per git branch
- **Merge Integration**: Semantic data automatically merges when branches merge
- **Natural Team Workflow**: No separate servers needed - works with any git hosting

#### **Technical Roadmap** (In Progress)

✅ **Phase 1 - Core Architecture** (Completed):
```bash
# Implemented repository-local CLI commands
svcs init                         # Initialize SVCS for repository
svcs status                       # Show repository status and branch info
svcs events --branch main --limit 10  # Branch-specific semantic events
svcs notes sync                   # Sync semantic data via git notes
svcs notes fetch                  # Fetch team's semantic data
svcs migrate list                 # List projects for migration from global DB
```

🚧 **Phase 2 - Integration** (In Progress):
```bash
# Planned integration with existing SVCS components
svcs search --event-type "security_improvement"  # Advanced semantic search
svcs diff-branches main..feature    # Compare semantic evolution between branches
svcs team-activity --since "1 week" # Team's semantic changes across branches
svcs merge-preview feature/auth     # Preview semantic impact of branch merge
```

📋 **Phase 3 - Team Features** (Planned):
- Full MCP server integration with repository-local mode
- Web dashboard for repository-local semantic data
- Advanced branch comparison and merge preview
- Team activity analytics and collaboration insights

#### **Git-Native Team Workflow** (Planned)
1. **Developer commits** → semantic analysis stored as git notes
2. **Push branch** → git notes automatically included  
3. **Teammates pull** → get commits + semantic analysis automatically
4. **Branch merges** → semantic events transfer to target branch
5. **Team collaboration** → everyone sees shared semantic evolution

#### **Architecture Goals**
- **Git-Native**: Leverages git's existing collaboration mechanisms
- **Zero Infrastructure**: No separate servers needed, works with GitHub/GitLab/etc.
- **Automatic Sync**: Semantic data follows same workflow as source code
- **Branch Aware**: Understands git branches and merge relationships

### **Technical Improvements**
- **Enhanced Language Support**: Full semantic analysis for more languages (Go, Rust, Java, C++, etc.)
- **Cross-Language Analysis**: Detection of architectural changes spanning multiple languages  
- **Real-time Analysis**: File-watching based analysis for immediate feedback
- **Advanced AI Integration**: Support for multiple LLM providers and local models
- **Visual Interfaces**: Rich IDE extensions and web-based exploration tools

### **Development Credits**

This project has been developed with substantial AI assistance:
- VS Code Claude 4 Preview agent (main coding)
- A code contribution from OpenAI O3 (debug persistent click cli --event-types parsing problem)

### **Research Areas**
- Semantic change impact prediction across application layers
- Code evolution pattern recognition and recommendation systems
- Automated refactoring suggestions based on semantic analysis
- Git-integrated semantic data synchronization and branch-aware analysis

## 🆘 Troubleshooting

*This section is intentionally left empty as we don't have extensive real-world usage experience yet. Issues and solutions will be documented as they are discovered through actual usage.*

## 📸 Screenshots & Demos

*TODO: Add screenshots and short videos/GIFs demonstrating:*
- *SVCS analysis output in terminal*
- *MCP integration in VS Code*
- *Web dashboard interface*
- *Conversational interface examples*

## 📄 License

[MIT License](LICENCE)

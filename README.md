# SVCS - Semantic Versi## 🌟 Key Features

- **🧠 5-Layer Semantic Analysis** - From AST parsing to AI-powered pattern recognition
- **📁 Repository-Local Architecture** - Each repository maintains its own semantic database  
- **🤝 Git-Integrated Team Collaboration** - Semantic data shared automatically via git notes
- **🌍 Multi-Language Support** - Python (complete), PHP (modern), JavaScript/TypeScript (AST-based)
- **🌐 Interactive Web Dashboard** - Modern browser-based interface for exploring semantic data
- **🤖 Model Context Protocol (MCP) Server** - AI assistant integration for VS Code, Claude, etc.
- **⚡ Real-Time Git Hooks** - Automatic semantic analysis on every commit
- **💬 Conversational AI Interface** - Natural language queries about code evolution
- **🛠️ Complete CLI Toolkit** - Rich command-line interface for all features
- **🔧 Project Management** - Multi-project support with centralized registrySystem

SVCS is a **repository-local semantic analysis system** that tracks the meaning of code changes beyond traditional line-by-line diffs. It uses a 5-layer analysis system combining Abstract Syntax Tree (AST) analysis with optional AI-powered semantic understanding.

🚀 **Production Ready** - Complete system with CLI, web dashboard, MCP server, and team collaboration features.

## Table of Contents

- [Key Features](#-key-features)
- [Why SVCS? Value Proposition](#-why-svcs-value-proposition)
- [5-Layer Analysis Architecture](#-5-layer-analysis-architecture)
- [Language Support](#-language-support)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Complete CLI Reference](#-complete-cli-reference)
- [Web Dashboard](#-web-dashboard)
- [MCP Server Interface](#-mcp-server-interface)
- [Advanced Features](#-advanced-features)
- [Development Setup](#-development-setup)
- [System Requirements](#-system-requirements)
- [Limitations](#-limitations)
- [Contributing](#-contributing)

## 🌟 Key Features

- **🧠 5-Layer Semantic Analysis** - From AST parsing to optional AI understanding
- **📁 Repository-Local Architecture** - Each repository maintains its own semantic database
- **🤝 Git-Integrated Team Collaboration** - Semantic data shared via git notes
- **🌍 Multi-Language Support** - Python (complete), PHP (modern), JavaScript/TypeScript (AST-based)
- **🤖 Model Context Protocol (MCP) Server** - AI assistant integration for VS Code, Claude, etc.
- **⚡ Real-Time Git Hooks** - Automatic semantic analysis on commit
- **💬 Conversational AI Interface** - Natural language queries about code evolution
- **📊 Interactive Web Dashboard** - Visualize semantic patterns and evolution
- **� Complete CLI Toolkit** - Rich command-line interface for all features

## 🚀 Why SVCS? Value Proposition

### Beyond Traditional Git: The Semantic Gap

While Git tracks *what* changed (lines, files), SVCS understands *what those changes mean*:

- **Git shows**: `+def calculate_score(items): return sum(x.value * x.weight for x in items)`
- **SVCS reveals**: "Added weighted calculation algorithm, introduced functional programming pattern, improved mathematical abstraction"

### Perfect for AI-Enhanced Development

Modern AI assistants (GitHub Copilot, Claude, GPT) excel at immediate code analysis but lack **temporal context**. SVCS provides the missing historical dimension:

| **Traditional AI Tools** | **SVCS + AI Tools** |
|---------------------------|----------------------|
| ✅ Analyze current code | ✅ **+ Track evolution patterns** |
| ✅ Suggest improvements | ✅ **+ Learn from past decisions** |
| ✅ Detect code smells | ✅ **+ Identify improvement trends** |
| ❌ No historical context | ✅ **Rich semantic history** |
| ❌ No team learning | ✅ **Team semantic intelligence** |

### Use Cases

- **🎯 Code Learning & Investigation** - Track your coding evolution and identify improvement patterns
- **🔗 Complete Git Integration** - Every semantic event links to its exact git commit for full traceability
- **🤝 Team Collaboration** - Git-integrated workflow for natural semantic data sharing
- **🏢 Enterprise Applications** - Code review enhancement, technical debt management, CI/CD integration
## 🧠 5-Layer Analysis Architecture

SVCS employs a multi-layer analysis system that provides increasingly sophisticated semantic understanding:

### Layers 1-4: Structural & Syntactic Analysis
- **Layer 1-2**: AST parsing and structural changes (functions, classes, imports)
- **Layer 3-4**: Behavioral patterns (control flow, data access, complexity)

### Layer 5a: Rule-Based Pattern Recognition
- Pattern detection using programmatic rules
- Identifies architectural and quality improvements
- Detects error handling patterns and functional programming adoption

### Layer 5b: LLM-Powered Analysis 🤖
- **Requires Google Gemini API key** (`GOOGLE_API_KEY` environment variable)
- **Intelligent Filtering**: Only analyzes non-trivial, complex changes
- **Without API key**: SVCS uses layers 1-5a (still very powerful!)
- Detects abstract concepts like:
  - Architecture improvements and design pattern adoption
  - Performance optimizations and maintainability enhancements
  - Code readability improvements and abstraction refinements
  - Error handling strategy changes

## 🌍 Language Support

| Language | Extensions | Support Level | Parser Technology | Features |
|----------|------------|---------------|-------------------|----------|
| **Python** | `.py`, `.pyw`, `.pyi` | **Complete** | Native AST | Full AST analysis, 31+ semantic event types, decorators, async/await, generators, comprehensions, type annotations |
| **PHP** | `.php`, `.phtml`, `.php3`, `.php4`, `.php5`, `.phps` | **Modern** | Tree-sitter (primary) + phply (fallback) | Modern PHP 7.4+/8.x features (enums, attributes, typed properties), PHP 5.x-7.3 support, classes, interfaces, traits, methods, properties, namespaces, inheritance tracking |
| **JavaScript** | `.js` | **AST-based** | esprima AST parser + regex fallback | ES6+ classes, arrow functions, async/await, inheritance changes, method signatures, constructor parameters, import/export tracking |
| **TypeScript** | `.ts` | **AST-based** | esprima AST parser + regex fallback | Same as JavaScript with TypeScript syntax support |

### Parser Architecture & Robustness

SVCS uses a **multi-tier fallback system** for maximum reliability:

#### PHP Analysis
1. **Primary**: Tree-sitter PHP parser (supports PHP 7.4+ and 8.x)
   - Modern features: enums, attributes, typed properties, union types
   - Accurate AST-based parsing with full semantic understanding
2. **Fallback**: phply parser (PHP 5.x-7.3 support)
   - Maintains compatibility with older codebases
3. **Final Fallback**: Regex parsing for basic structural detection

#### JavaScript/TypeScript Analysis
1. **Primary**: esprima AST parser with tolerance mode
   - Full ES6+ syntax support including classes, arrow functions, async/await
   - Detailed parameter and inheritance tracking
   - Supports both JavaScript (.js) and TypeScript (.ts) syntax
2. **Fallback**: Enhanced regex parsing with modern JS patterns
   - Comprehensive pattern matching for various function declarations

#### Detected Change Types by Language

**Python (Complete Support)**:
- ✅ Functions, classes, methods, properties, decorators
- ✅ Async/await patterns, generators, comprehensions
- ✅ Type annotations, inheritance tracking
- ✅ Import statements, exception handling
- ✅ 31+ distinct semantic event types

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

> **Note**: Python provides the most comprehensive semantic analysis. PHP and JavaScript offer robust structural and semantic change detection suitable for production use in git hooks.
## 🛠️ Installation

**Requirements**: Python 3.8+, Git, Unix-based system (Linux, macOS, or Windows WSL)

### 1. Install SVCS

```bash
# Clone the repository
git clone https://github.com/markomanninen/svcs.git
cd svcs

# Install SVCS globally (creates 'svcs' command)
pip install -e .

# Install enhanced language parsing (optional but recommended)
pip install tree-sitter tree-sitter-php esprima

# Verify installation
svcs --help
```

### 2. Optional: AI Analysis Setup

For Layer 5b AI analysis, set up Google Gemini API:

```bash
# Get your API key from: https://makersuite.google.com/app/apikey
export GOOGLE_API_KEY="your-api-key"

# Or add to your shell profile (.bashrc, .zshrc, etc.)
echo 'export GOOGLE_API_KEY="your-api-key"' >> ~/.bashrc
```

**Note**: Without the API key, SVCS still provides powerful semantic analysis through layers 1-5a.

## 🚀 Quick Start

### 1. Initialize SVCS in Your Repository

```bash
# Navigate to your git project
cd your-project

# Initialize SVCS (installs git hooks automatically)
svcs init

# For new projects, SVCS can initialize git too
svcs init --git-init
```

### 2. Use Your Normal Git Workflow

```bash
# Make changes to your code
echo "def new_function(): pass" >> code.py

# Commit as usual - SVCS analyzes automatically
git add code.py
git commit -m "Add new function"
# 🔍 SVCS: Analyzing semantic changes...
# ✅ SVCS: Detected semantic events stored locally and in git notes
```

### 3. Explore Your Code Evolution

```bash
# View recent semantic changes
svcs events --limit 10

# Search for specific patterns
svcs search "authentication"

# Track function evolution
svcs evolution "func:new_function"

# Check repository status
svcs status
```

### 4. Explore Advanced Interfaces

```bash
# Interactive web dashboard
svcs web start
# Open http://127.0.0.1:8080 in your browser

# Start MCP server for AI integration
svcs mcp start --background

# Conversational interface
svcs discuss --query "summarize recent changes"
```

## 📋 Complete CLI Reference

### Quick Reference Table

| Command | Description | Example |
|---------|-------------|---------|
| **Core Repository Management** |
| `svcs init` | Initialize SVCS in current repository | `svcs init` |
| `svcs init-project [name]` | Interactive project setup with tour | `svcs init-project MyApp` |
| `svcs status` | Show repository status and semantic stats | `svcs status` |
| `svcs cleanup` | Repository maintenance and optimization | `svcs cleanup --show-stats` |
| **Semantic Data Exploration** |
| `svcs events` | List recent semantic events | `svcs events --limit 50` |
| `svcs search` | Advanced semantic search | `svcs search "authentication"` |
| `svcs evolution` | Track function/class evolution | `svcs evolution "func:authenticate"` |
| `svcs compare` | Compare semantic patterns between branches | `svcs compare main develop` |
| **Analytics and Quality** |
| `svcs analytics` | Generate comprehensive analytics report | `svcs analytics --output report.json` |
| `svcs quality` | Code quality analysis | `svcs quality --verbose` |
| **Web Dashboard** |
| `svcs web start` | Start interactive web dashboard | `svcs web start --port 9000` |
| `svcs dashboard` | Generate static HTML dashboard | `svcs dashboard --output dash.html` |
| **AI Integration** |
| `svcs discuss` | Start conversational interface | `svcs discuss --query "recent changes"` |
| `svcs query` | One-shot natural language query | `svcs query "show performance issues"` |
| `svcs mcp start` | Start MCP server for AI assistants | `svcs mcp start --background` |
| **Enhanced Git Operations** |
| `svcs pull` | Enhanced git pull with semantic sync | `svcs pull` |
| `svcs push` | Enhanced git push with semantic notes | `svcs push origin main` |
| `svcs merge` | Enhanced git merge with event transfer | `svcs merge feature-branch` |
| `svcs sync` | Sync semantic data with remote | `svcs sync` |
| `svcs sync-all` | Complete sync after complex operations | `svcs sync-all` |
| **Configuration & CI** |
| `svcs config` | Configure SVCS settings | `svcs config set auto-sync true` |
| `svcs ci` | CI/CD integration commands | `svcs ci pr-analysis` |
| **Utilities** |
| `svcs notes` | Git notes management | `svcs notes sync` |
| `svcs workflow` | Show workflow guide | `svcs workflow --type team` |
| `svcs help` | Quick help and examples | `svcs help` |

### Core Repository Management

```bash
svcs init                    # Initialize SVCS in current repository
svcs init --git-init         # Initialize git repository + SVCS
svcs status                  # Show repository status and semantic stats
svcs cleanup                 # Repository maintenance and optimization
```

### Semantic Data Exploration

```bash
# View semantic events
svcs events                  # Recent semantic events (default: 20)
svcs events --limit 50       # Show more events
svcs events --branch main    # Events for specific branch
svcs events --type "function_added"  # Filter by event type

# Advanced search
svcs search "authentication"               # Search semantic events
svcs search --author "john@example.com"    # Filter by author
svcs search --since "1 week ago"           # Time-based filtering
svcs search --pattern-type performance     # Search for patterns

# Track evolution
svcs evolution "func:authenticate"   # Track specific function
svcs evolution "class:UserManager"   # Track class evolution
```

### Analytics and Insights

```bash
svcs analytics               # Generate analytics report
svcs quality                 # Code quality analysis
svcs compare main develop    # Compare branches
```

### Web and AI Interfaces

```bash
# Web dashboard
svcs web start               # Start interactive web dashboard
svcs web start --port 9000   # Custom port
svcs dashboard               # Generate static HTML dashboard

# AI-powered interfaces
svcs discuss                 # Start interactive conversation
svcs discuss --query "what changed recently?"  # Start with query
svcs query "show performance improvements"     # One-shot query

# MCP server for AI assistants
svcs mcp start               # Start MCP server (foreground)
svcs mcp start --background  # Background mode
svcs mcp status              # Check server status
svcs mcp stop                # Stop server
```

### Git Integration

```bash
svcs notes sync              # Sync semantic notes with remote
svcs notes fetch             # Fetch team semantic data
svcs notes show --commit abc123  # View semantic note for commit
```

### Project Tours and Help

```bash
svcs init-project            # Interactive project setup tour
svcs init-project MyProject --non-interactive  # Automated setup
svcs workflow               # Show workflow guide
svcs help                   # Quick help and examples
```

### Advanced Git Integration & Sync Commands

```bash
# Enhanced git operations with automatic semantic sync
svcs pull                    # Enhanced git pull with semantic notes sync
svcs push [remote] [branch]  # Enhanced git push with semantic notes sync  
svcs merge <branch>          # Enhanced git merge with semantic event transfer
svcs sync                    # Sync semantic data with remote repository
svcs sync-all                # Complete sync after complex git operations
svcs merge-resolve           # Resolve post-merge semantic event issues
svcs auto-fix                # Auto-detect and fix common SVCS issues

# Configuration management
svcs config set auto-sync true     # Configure automatic sync behavior
svcs config get auto-sync          # View current configuration
svcs config list                   # List all configuration settings

# CI/CD integration
svcs ci pr-analysis          # Analyze pull request semantic impact
svcs ci quality-gate         # Run quality gate checks
svcs ci report               # Generate CI reports

# Project management
svcs init-project            # Interactive project creation with guided tour
svcs delete-project          # Remove project from SVCS tracking

# Internal/Hook commands (typically used by git hooks)
svcs process-hook post-commit       # Process git post-commit hook
```

## 🌐 Web Dashboard

SVCS provides a comprehensive web-based interface for exploring semantic data, project management, and analytics.

### Quick Start

```bash
# Start the interactive web dashboard  
svcs web start

# Custom port
svcs web start --port 9000

# Open in browser
# http://127.0.0.1:8080
```

### Dashboard Features

**🔍 Semantic Search & Analysis**
- Advanced filtering by author, date range, confidence level, and analysis layer
- Quick action buttons for common searches (performance, architecture, error handling)
- Real-time results with formatted display and confidence scores

**📝 Git Integration**
- View changed files for any commit with syntax highlighting
- Display raw git diffs with comprehensive commit analysis
- Browse recent commits with semantic context and evolution tracking

**📈 Code Evolution & Analytics**
- Track specific functions/classes over time with detailed evolution history
- AI-detected pattern analysis (performance, architecture, error handling)
- Confidence-based filtering and temporal pattern analysis

**🗂️ Project Management**
- Multi-project support with centralized repository discovery and management
- Project statistics, health monitoring, and comprehensive analytics
- Database maintenance tools with cleanup and optimization features

**📊 Interactive Visualizations**
- Timeline visualizations of semantic evolution
- Event type distribution charts and analytics dashboards
- Network diagrams showing code structure and dependencies

### Static Dashboard Generation

```bash
# Generate standalone HTML dashboard
svcs dashboard --output my_report.html

# Open the generated file in any browser
# No server required - fully self-contained
```

## 🤖 MCP Server Interface

SVCS provides a **Model Context Protocol (MCP) server** that integrates with AI assistants like Claude, VS Code Copilot, and other MCP-compatible tools.

### Quick Start

```bash
# Start MCP server
svcs mcp start --background

# Check status
svcs mcp status

# View logs
svcs mcp logs

# Stop server
svcs mcp stop
```

### Available MCP Tools

**Project Management**
- `list_projects` - List all SVCS repositories
- `get_project_statistics` - Get semantic statistics for project

**Semantic Analysis**
- `search_events_advanced` - Advanced search with comprehensive filtering
- `get_recent_activity` - Get recent semantic changes
- `search_semantic_patterns` - AI-powered pattern search
- `get_filtered_evolution` - Track specific code element evolution

**Git Integration**
- `get_commit_changed_files` - List files changed in commits
- `get_commit_summary` - Comprehensive commit analysis with semantic events

### Usage in AI Assistants

Once the MCP server is running, you can ask natural language questions in compatible AI interfaces:

**VS Code/Cursor with Copilot Chat:**
```
@copilot Show me all registered SVCS projects
@copilot What semantic patterns were detected in the last week?
@copilot Get a summary of commit abc123 including all semantic events
@copilot How has the authenticate function evolved over time?
@copilot Find all performance optimizations in my code
@copilot Show recent architecture improvements with high confidence
```

**Claude Desktop:**
> *"Show me all registered projects"*  
> *"What semantic patterns were detected in the last week?"*  
> *"Get a summary of commit abc123 including all semantic events"*  
> *"How has the authenticate function evolved over time?"*

### IDE Integration

The MCP server integrates seamlessly with modern development environments:

- **Claude Desktop** - Add SVCS server to your MCP configuration for natural language semantic queries
- **VS Code with Copilot Chat** - Use `@copilot` commands to access SVCS semantic insights directly in your editor
- **Cursor IDE** - Native MCP support for AI-powered semantic code analysis
- **Any MCP-compatible AI interface** - Standard Model Context Protocol support ensures broad compatibility

## 🔬 Advanced Features

### Team Collaboration

SVCS provides git-integrated team collaboration through semantic notes:

```bash
# Share semantic insights with team
svcs notes sync                  # Push semantic data to remote
git push origin main             # Semantic notes included automatically

# Receive team insights
git pull origin main             # Semantic notes synced automatically
svcs notes fetch                 # Explicit fetch if needed

# View team semantic data
svcs notes show --commit abc123  # See semantic note for specific commit
```

### Branch Comparison

```bash
# Compare semantic evolution between branches
svcs compare main develop        # See semantic differences
svcs compare --limit 20          # Show more comparison data
```

### Pattern Analysis

```bash
# Search for specific semantic patterns
svcs search --pattern-type performance     # Performance improvements
svcs search --pattern-type architecture    # Architectural changes
svcs search --pattern-type error_handling  # Error handling patterns
```

### CI/CD Integration

```bash
# Analyze pull request semantic impact
svcs ci pr-analysis --target main

# Run quality gate checks
svcs ci quality-gate --strict

# Generate CI reports
svcs ci report --format json
```

### Configuration Management

```bash
# View current configuration
svcs config list

# Configure automatic sync with remotes
svcs config set auto-sync true

# Set AI analysis confidence threshold
svcs config set ai-threshold 0.8

# Configure web dashboard settings
svcs config set web-port 9000
svcs config set web-host 0.0.0.0
```

### Project Management

```bash
# Interactive project creation and setup
svcs init-project MyNewProject

# Non-interactive project creation
svcs init-project MyProject --path /path/to/project --non-interactive

# Remove project from SVCS tracking
svcs delete-project --path /path/to/project

# List all registered projects
svcs list

# Project cleanup and maintenance
svcs cleanup --git-unreachable
svcs cleanup --show-stats
```

## 🧑‍💻 Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/markomanninen/svcs.git
cd svcs

# Install in development mode with all dependencies
pip install -e .

# Install enhanced language parsing (recommended)
pip install tree-sitter tree-sitter-php esprima

# Install development dependencies
pip install pytest black pre-commit

# Install git hooks for development
pre-commit install

# Verify installation
svcs --help
```

### Running Tests

```bash
# Core functionality tests
python -m pytest tests/

# Comprehensive integration tests
python tests/test_complete_functionality.py

# GitHub collaboration workflow tests
python tests/test_github_collaboration.py

# MCP server functionality tests
python tests/test_mcp_tools.py

# Web dashboard tests
python tests/test_comprehensive_dashboard.py
```

## 🖥️ System Requirements

### Core Requirements
- **Python**: 3.8+ (recommended: 3.11+)
- **Git**: 2.0+
- **OS**: Unix-based system (Linux, macOS, or Windows WSL)
- **Memory**: 2GB+ RAM
- **Storage**: 100MB+ for databases and logs

### Dependencies
SVCS automatically installs required dependencies:

```bash
# Essential (auto-installed)
rich>=12.0.0                    # Terminal UI and formatting
click>=8.0.0                    # CLI framework  
sqlite3                         # Database (built-in)
google-generativeai>=0.3.0      # Gemini AI integration
tenacity>=8.0.0                 # Retry logic for API calls

# Language parsing (auto-installed)
tree-sitter>=0.20.0             # Modern parsing engine
tree-sitter-php>=0.20.0         # PHP AST support
esprima>=4.0.1                  # JavaScript/TypeScript support
phply>=1.2.6                    # PHP fallback parser

# Web dashboard (optional)
Flask>=2.0.0                    # Web server
Flask-CORS>=3.0.0               # Cross-origin requests

# MCP server (optional)
mcp                             # Model Context Protocol
```

### API Requirements
- **Google Gemini API** (optional) - Required for Layer 5b AI analysis
  - Get free key at: https://makersuite.google.com/app/apikey
  - Free tier: 1000 requests/day
  - Without API key: SVCS uses layers 1-5a (still very powerful!)

### Performance Characteristics
- **Layer 1-4 analysis**: ~100-200ms per commit (fast AST-based analysis)
- **Layer 5a analysis**: ~200-500ms per commit (rule-based pattern detection)
- **Layer 5b analysis**: ~2-10s per commit (AI analysis, only for complex changes, requires API key)
- **Database queries**: ~10-50ms (optimized with indices)
- **Web dashboard startup**: ~1-3s (includes project discovery)
- **MCP server response**: ~100-500ms per query (depending on complexity)

## ⚠️ Limitations

### Current Limitations
- **Windows Support**: Requires WSL due to symbolic link usage for git hooks and shell script dependencies
- **Database Scale**: SQLite-based storage may require optimization for very large repositories (>100k commits)
- **API Dependencies**: Layer 5b AI analysis requires external Google Gemini API access and consumes API tokens
- **Real-time Analysis**: Git hook-based approach requires commits to trigger analysis (no live code analysis)
- **Memory Usage**: Large repositories may require 2-4GB RAM for comprehensive analysis

### Language Support Status
- **Python**: Comprehensive semantic analysis with 31+ event types, full AST support
- **PHP**: Modern language support (PHP 7.4+/8.x) with Tree-sitter parser + phply fallback
- **JavaScript/TypeScript**: AST-based analysis with comprehensive ES6+ syntax support
- **Other Languages**: Planned support for Go, Rust, Java, C++, and other popular languages

### Scalability Considerations
- **Repository Size**: Optimized for typical project sizes (1k-10k commits)
- **Team Size**: Repository-local architecture scales naturally with distributed teams
- **Performance Impact**: Git hook approach adds ~200ms-2s to commit time depending on analysis layers
- **Storage Requirements**: ~10-50MB additional storage per 1000 commits for semantic data
- **Network Usage**: Git notes synchronization adds minimal overhead to git operations

## 🆘 Getting Help

### Built-in Help Commands

```bash
# Quick help and examples
svcs help

# Show SVCS workflow guide  
svcs workflow

# Show team collaboration workflow
svcs workflow --type team

# Show troubleshooting guide
svcs workflow --type troubleshooting

# Get help for specific commands
svcs init --help
svcs search --help
svcs web --help
```

### Common Issues & Solutions

**Installation Issues**
```bash
# Verify installation
pip install -e .
svcs --version

# Install with optional dependencies
pip install -e ".[ai,web,mcp]"
```

**Setup Issues**
```bash
# Initialize SVCS in existing repository
svcs init

# Check repository status
svcs status

# Run diagnostics
svcs auto-fix
```

**Performance Issues**
```bash
# Clean up database
svcs cleanup --show-stats

# Optimize repository
svcs cleanup --git-unreachable
```

### Documentation & Resources

- **Quick Start**: Follow the examples in the "🚀 Quick Start" section above
- **Complete CLI Reference**: See the command table and detailed sections above
- **Web Dashboard**: Interactive interface with built-in help tooltips
- **MCP Integration**: Built-in AI assistant tools for natural language queries
- **Project Examples**: Use `svcs init-project` for guided setup with real examples

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Workflow

```bash
# Fork and clone
git clone https://github.com/yourusername/svcs.git
cd svcs

# Set up development environment
pip install -e .
pip install pytest black pre-commit

# Install pre-commit hooks
pre-commit install

# Make changes and test
python -m pytest tests/
python tests/test_complete_functionality.py

# Submit pull request
```

### Areas for Contribution
- **Language Support**: Add parsers for new programming languages (Go, Rust, Java, C++)
- **AI Integration**: Improve semantic pattern detection algorithms and confidence scoring
- **Performance Optimization**: Enhance analysis speed, memory usage, and database efficiency
- **Web Dashboard**: Add new visualizations, analytics features, and user interface improvements
- **Documentation**: Improve user guides, API documentation, and example projects
- **Testing**: Expand test coverage for edge cases, multi-language projects, and large repositories
- **Platform Support**: Native Windows support without WSL dependency

### Code Style
- Follow PEP 8 for Python code
- Use type hints where possible
- Add docstrings for public functions
- Run `black` for code formatting
- Test your changes thoroughly

### Reporting Issues
- **Bug Reports**: Use GitHub Issues with minimal reproduction examples and system information
- **Feature Requests**: Describe use cases and expected behavior clearly
- **Performance Issues**: Include repository size, commit frequency, and analysis timing data
- **Documentation Issues**: Suggest specific improvements or clarifications needed
- **System Requirements**: Always include SVCS version, Python version, and operating system details

## 📄 License

[MIT License](LICENSE) - See the LICENSE file for details.

---

**SVCS** - Bringing semantic understanding to version control through repository-local analysis, team collaboration, and AI integration. Built with ❤️ for developers who care about understanding code evolution beyond traditional diffs.

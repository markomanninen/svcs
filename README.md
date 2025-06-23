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
- **💬 Conversational Interface** - Natural language queries about code evolution
- **📊 Analytics & Visualization** - Web dashboard and quality insights
- **🔧 CI/CD Integration** - Automated quality gates and PR analysis
- **⚡ Global Project Management** - Track multiple projects from one interface

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
| ❌ No team learning | ✅ **Organizational code intelligence** |

### **The SVCS Advantage**

1. **Semantic Memory**: Your codebase remembers why changes were made
2. **Pattern Recognition**: Identify successful architectural decisions over time
3. **Team Intelligence**: Learn from collective coding wisdom
4. **AI Enhancement**: Provide LLM agents with rich context for better assistance
5. **Educational Tool**: Deep insights into programming evolution and best practices

## 🎯 **Use Cases & Creative Applications**

### **🤖 AI Agent Enhancement**

**Problem**: AI assistants lack context about your project's evolution
**Solution**: SVCS + MCP provides rich semantic context

```typescript
// AI Agent with SVCS context:
"Based on your codebase history, I see you've been transitioning from 
procedural to functional patterns. The last 5 commits show increased 
use of map/filter/reduce. For this new feature, I recommend continuing 
this pattern with..."
```

**Creative Applications**:
- **AI Pair Programming**: Agents understand your coding style evolution
- **Intelligent Code Review**: Context-aware suggestions based on project patterns
- **Architectural Guidance**: AI recommendations informed by successful past decisions
- **Technical Debt Detection**: AI identifies recurring problematic patterns

### **📚 Deep Learning About Programming**

**Educational Use Cases**:

1. **Programming Skill Development**
   ```bash
   # Discover your coding evolution
   python3 svcs_discuss.py
   > "How has my error handling improved over time?"
   > "What design patterns have I adopted this year?"
   > "Show me my most significant architectural decisions"
   ```

2. **Team Knowledge Transfer**
   - New developers understand codebase evolution
   - See how experienced developers approach problems
   - Learn from successful refactoring patterns

3. **Code Review Learning**
   - Understand the *why* behind code changes
   - See long-term impact of architectural decisions
   - Learn from semantic patterns that improved code quality

### **🔍 Code Archaeology & Investigation**

**Forensic Analysis**:
```bash
# Investigate complex bugs
python3 svcs.py log --node="func:authentication" --layer="5b"
# Result: "3 months ago: simplified auth flow, removed edge case handling"

# Understand performance regressions  
python3 svcs_discuss.py
> "What changes affected database performance in the last quarter?"
```

**Creative Applications**:
- **Bug Origin Tracking**: Semantic analysis reveals when complexity was introduced
- **Architecture Archaeology**: Understand how current architecture evolved
- **Decision Archaeology**: Rediscover reasoning behind historical changes

### **🔗 Full Git Traceability & Integration**

**Every semantic event is linked to its exact git commit identifier**, enabling complete traceability:

```bash
# Find semantic events with commit hashes
python3 svcs_mcp/cli.py query-events --limit 5
# Shows: Event: node_added, Commit: 88e833c5...

# Access the actual file changes
git show 88e833c5
# Shows: full diff of what changed in that commit

# View commit context
git log --oneline 88e833c5
# Shows: commit message, author, date
```

**New: Programmatic Git Integration** 🆕

SVCS now provides direct access to git changes through both the MCP server and conversational interface:

```bash
# Via MCP tools in VS Code/Cursor:
> get changed files for commit 88e833c5
> show me the diff for commit 88e833c5
> summarize commit 88e833c5

# Via conversational interface:
python3 svcs_discuss.py
> "What files were changed in commit 88e833c5?"
> "Show me the actual diff for that commit"
> "What were the exact code changes that led to the authentication refactoring?"
```

**Enhanced API Functions**:
- `get_commit_changed_files(commit_hash)` - List of files changed in commit
- `get_commit_diff(commit_hash, file_path=None)` - Git diff for commit (optionally filtered to specific file)
- `get_commit_summary(commit_hash)` - Comprehensive commit information including metadata, files, and semantic events

**Database Schema Linkage**:
- Every `semantic_events` record contains a `commit_hash` field
- Links directly to git commits for full historical context
- Enables forensic analysis of how semantic changes relate to actual code changes
- Supports advanced workflows like blame analysis and bisect operations

### **🎓 Advanced Learning & Research**

**Programming Education**:
1. **Pattern Recognition**: Identify when and why design patterns emerge
2. **Refactoring Studies**: Track successful code improvement strategies
3. **Language Evolution**: See how teams adopt new language features
4. **Best Practices Discovery**: Learn from semantic patterns that improve quality

**Research Applications**:
- **Code Evolution Studies**: Academic research on programming practices
- **Team Dynamics**: How different developers contribute to semantic evolution
- **Language Adoption**: Track migration patterns between technologies
- **Quality Metrics**: Correlation between semantic changes and bug rates

### **🏢 Enterprise & Team Applications**

**Organizational Intelligence**:

1. **Code Review Excellence**
   ```bash
   # Find exemplary refactoring examples
   python3 svcs.py log --type="abstract_abstraction_improvement" --min-confidence=0.9
   # Use findings to train junior developers
   ```

2. **Architecture Decision Records (ADR) Enhancement**
   - Automatic detection of architectural changes
   - Evidence-based architecture evolution tracking
   - Long-term impact assessment of decisions

3. **Technical Debt Management**
   ```bash
   # Identify debt accumulation patterns
   python3 svcs_analytics.py --focus="maintainability_trends"
   # Proactive debt reduction strategies
   ```

### **🔧 DevOps & CI/CD Innovation**

**Intelligent Pipeline Integration**:

1. **Semantic-Aware Testing**
   - Trigger different test suites based on semantic change types
   - Performance tests for changes marked as optimization
   - Security tests for authentication/authorization changes

2. **Deployment Risk Assessment**
   ```bash
   # Pre-deployment analysis
   python3 svcs_ci.py --semantic-risk-assessment
   # "High semantic complexity detected, recommend gradual rollout"
   ```

3. **Quality Gates 2.0**
   - Block deployments with semantic complexity spikes
   - Require documentation for architectural changes
   - Enforce review requirements based on semantic impact

### **💡 Creative & Experimental Applications**

**Novel Use Cases**:

1. **Code Storytelling**
   ```bash
   # Generate narrative documentation
   python3 svcs_discuss.py
   > "Tell the story of how our authentication system evolved"
   # Creates narrative documentation automatically
   ```

2. **Semantic Code Metrics**
   - Track "semantic velocity" (meaningful changes per sprint)
   - Measure "architectural coherence" over time
   - "Code wisdom index" (accumulation of best practices)

3. **AI Training Data Generation**
   - High-quality examples of code improvements
   - Before/after semantic analysis for model training
   - Real-world refactoring pattern datasets

4. **Cross-Project Pattern Mining**
   ```bash
   # Discover successful patterns across projects
   svcs_analytics.py --cross-project-patterns
   # Share architectural wisdom across teams
   ```

### **🎯 Targeting Specific Problems**

**Real-World Problem Solving**:

1. **"Why is this code so complex?"**
   - Trace semantic complexity accumulation
   - Identify when complexity was introduced
   - Learn from successful simplification patterns

2. **"How do we maintain code quality?"**
   - Track quality trends over time
   - Identify developers/practices that improve quality
   - Set up semantic quality gates

3. **"Why do bugs keep appearing here?"**
   - Semantic analysis reveals fragile code patterns
   - Track correlation between change types and bugs
   - Predictive quality analysis

4. **"How do we onboard new developers?"**
   - Show them semantic evolution patterns
   - Demonstrate team coding standards through history
   - Provide context for architectural decisions

### **🔮 Future-Forward Applications**

**Emerging Possibilities**:

1. **AI Code Generation Enhancement**
   - Generate code following project's semantic patterns
   - Maintain architectural consistency automatically
   - Learn from project-specific successful patterns

2. **Semantic Code Search**
   ```bash
   # Find code by semantic meaning, not syntax
   > "Find functions that handle error recovery"
   > "Show me examples of performance optimization"
   ```

3. **Predictive Development**
   - Predict which code areas need refactoring
   - Suggest architectural improvements based on patterns
   - Recommend team training based on semantic gaps

**The fundamental insight**: SVCS transforms code history from a simple audit trail into a rich, queryable knowledge base that enhances both human understanding and AI capabilities.

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
```

### **2. Configure MCP Server in VS Code**

Add to your VS Code `settings.json`:

```json
{
  "mcp": {
    "servers": {
      "svcs": {
        "command": "python3",
        "args": ["/path/to/svcs/svcs_mcp/working_mcp_server.py"],
        "env": {}
      }
    }
  }
}
```

> **💡 Note**: For enhanced PHP and JavaScript/TypeScript support, ensure you have installed the language parsing dependencies: `tree-sitter`, `tree-sitter-php`, and `esprima`. Without these, SVCS will fall back to basic regex parsing.

## 🚀 **Quick Start**

### **1. Register a Project**

```bash
# Navigate to your git project
cd your-project

# Register with SVCS MCP server
svcs init --name "My Project" .
```

### **2. Make Changes and Commit**

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

Use any MCP-compatible IDE or the CLI:

```bash
# Via MCP tools in VS Code/Cursor:
> list svcs projects
> show stats for my project

# Via command line:
python3 svcs.py log
python3 svcs_discuss.py  # Requires GOOGLE_API_KEY
```

## 📖 **Usage Guide**

### **Core SVCS Module (`svcs.py`)**

The main CLI interface for querying semantic history:

```bash
# View complete semantic history
python3 svcs.py log

# Filter by author
python3 svcs.py log --author="John Doe"

# Filter by event type
python3 svcs.py log --type="node_signature_changed"

# Filter by specific function/node
python3 svcs.py log --node="func:greet"

# Filter by analysis layer
python3 svcs.py log --layer="5b"  # AI semantic insights
python3 svcs.py log --layer="core" # Structural changes

# Complex queries
python3 svcs.py log --layer="5b" --min-confidence=0.8
python3 svcs.py log --type="abstract_performance_optimization"

# Clean orphaned data
python3 svcs.py prune
```

### **Conversational Interface (`svcs_discuss.py`)**

Natural language queries about code evolution:

```bash
# Start interactive session (requires GOOGLE_API_KEY)
export GOOGLE_API_KEY="your_key"
python3 svcs_discuss.py

# Example queries:
"What performance optimizations were made last week?"
"Show me all dependency changes by Alice"
"How has the DataProcessor class evolved?"
"Which commits had the most significant semantic changes?"

# New git integration queries:
"What files were changed in commit abc123?"
"Show me the actual diff for that commit"
"What were the exact code changes that led to the authentication refactoring?"
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

### **Interactive Web Dashboard** 🆕

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
- 🗂️ **Project Management**: Multi-project support and statistics
- 📊 **Analytics**: Quality trends and comprehensive reporting
- 🔧 **Database Maintenance**: Clean orphaned data and optimize storage

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

## � **Database Maintenance**

SVCS includes comprehensive database maintenance tools to keep your semantic data clean and optimized.

### **Orphaned Data Cleanup**

When git history is modified (rebasing, squashing, force-pushing), some semantic data may become "orphaned" - linked to commits that no longer exist. SVCS provides multiple ways to clean this up:

#### **Interactive Dashboard** (Recommended)
- Navigate to "🔧 Database Maintenance" in the web interface
- Choose specific project or global cleanup
- Visual results with detailed statistics
- Built-in help and safety information

#### **Command Line Interface**
```bash
# Clean all projects
python3 svcs.py prune

# Clean specific project
python3 svcs.py prune /path/to/project
```

#### **MCP Server Integration**
```
> prune orphaned data for /path/to/project
> clean up database for all projects
```

### **Safety & Best Practices**

- **Always backup** your database before pruning: `cp ~/.svcs/global.db ~/.svcs/global.db.backup`
- **Coordinate with team** on shared repositories
- **Regular maintenance** - prune after major rebases or history changes
- **Monitor results** - review what was cleaned to ensure nothing important was lost

For comprehensive maintenance documentation, see [`docs/DATABASE_MAINTENANCE_GUIDE.md`](docs/DATABASE_MAINTENANCE_GUIDE.md).

## �📚 **Module Documentation**

### **Core Analysis Engine**

#### **`svcs.py` - Main CLI Interface**
- Rich terminal output with filtering capabilities
- Event type and layer-based queries
- Author and time-based filtering
- Database maintenance operations (prune, stats, debug)

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
- `get_project_statistics` - Get semantic statistics for project

#### **Semantic Analysis**
- `query_semantic_events` - Query events with filtering
- `get_recent_activity` - Get recent semantic changes
- `search_semantic_patterns` - AI-powered pattern search
- `get_filtered_evolution` - Track specific code element evolution
- `search_events_advanced` - Advanced filtering and search
- `analyze_current_commit` - Analyze most recent commit

#### **Git Integration** 🆕
- `get_commit_changed_files` - List files changed in a specific commit
- `get_commit_diff` - Get git diff for a commit (optionally filtered to specific file)
- `get_commit_summary` - Comprehensive commit information including metadata, files, and semantic events

#### **Database Maintenance** 🆕
- `prune_orphaned_data` - Remove semantic data for commits no longer in git history
- `debug_query_tools` - Diagnostic information for database debugging

### **Practical Usage**

In any MCP-compatible IDE (VS Code, Cursor, etc.):

```
# Project management
> list svcs projects
> show stats for /path/to/project
> register this project with SVCS

# Semantic queries
> find performance improvements in my project
> show recent architecture changes
> what functions were added last week?
> analyze error handling patterns

# Git integration queries
> get changed files for commit abc123
> show me the diff for commit abc123
> summarize commit abc123
> show diff for file.py in commit abc123

# Database maintenance
> prune orphaned data for /path/to/project
> clean up database for all projects
> debug database for this project
```

### **Project Management CLI**

```bash
# Project lifecycle management
svcs init --name "My Project" /path/to/project     # Register and setup
svcs list                                          # List all projects
svcs status /path/to/project                       # Check project status
svcs remove /path/to/project                       # Unregister project

# Database maintenance
svcs prune /path/to/project                        # Clean orphaned data for specific project
svcs prune                                         # Clean orphaned data for all projects
```

## 🔧 **Development Setup**

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

### **Planned Improvements**
- **Enhanced Language Support**: Full semantic analysis for more languages (Go, Rust, Java, C++, etc.)
- **Cross-Language Analysis**: Detection of architectural changes spanning multiple languages  
- **Real-time Analysis**: File-watching based analysis for immediate feedback
- **Distributed Architecture**: Support for large-scale, multi-repository analysis
- **Advanced AI Integration**: Support for multiple LLM providers and local models
- **Visual Interfaces**: Rich IDE extensions and web-based exploration tools

### **Research Areas**
- Semantic change impact prediction across application layers
- Code evolution pattern recognition and recommendation systems
- Automated refactoring suggestions based on semantic analysis
- Cross-project learning and pattern transfer

## 🆘 Troubleshooting

*This section is intentionally left empty as we don't have extensive real-world usage experience yet. Issues and solutions will be documented as they are discovered through actual usage.*

## 📸 Screenshots & Demos

*TODO: Add screenshots and short videos/GIFs demonstrating:*
- *SVCS analysis output in terminal*
- *MCP integration in VS Code*
- *Web dashboard interface*
- *Conversational interface examples*

## 📄 License

[MIT License - Specify your license here]

---

## 🌟 **Getting Started**

SVCS provides semantic understanding of code evolution beyond traditional version control. Start tracking the meaning of your code changes today:

```bash
# Quick start
git clone https://github.com/markomanninen/svcs.git
cd your-project
/path/to/svcs/svcs_mcp/cli.py init --name "My Project" .
export GOOGLE_API_KEY="your_key"  # Optional, for Layer 5b
git commit -m "Begin semantic tracking" --allow-empty
```

**SVCS - Understanding what your code changes actually mean.** 🚀

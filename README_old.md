# SVCS - Semantic Version Control System

SVCS tracks semantic meaning in code changes beyond traditional line-by-line diffs. It uses a 5-layer analysis system combining Abstract Syntax Tree (AST) analysis with optional AI-powered semantic understanding.

## Table of Contents

- [Key Features](#-key-features)
- [5-Layer Analysis Architecture](#-5-layer-analysis-architecture)
- [Language Support](#-language-support)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Guide](#-usage-guide)
- [Module Documentation](#-module-documentation)
- [MCP Server Interface](#-mcp-server-interface)
- [Development Setup](#-development-setup)
- [System Requirements](#-system-requirements)
- [Limitations](#-limitations)
- [Future Development](#-future-development)

## 🌟 **Key Features**

- **🧠 5-Layer Semantic Analysis** - From AST parsing to optional AI understanding
- **🤖 Model Context Protocol (MCP) Server** - Modern AI integration architecture
- **🌍 Multi-Language Support** - Python (complete), JavaScript/TypeScript/Go/PHP (basic)
- **💬 Conversational Interface** - Natural language queries about code evolution
- **📊 Analytics & Visualization** - Web dashboard and quality insights
- **🔧 CI/CD Integration** - Automated quality gates and PR analysis
- **⚡ Global Project Management** - Track multiple projects from one interface

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

| Language | Extensions | Support Level | Features |
|----------|------------|---------------|----------|
| **Python** | `.py`, `.pyw`, `.pyi` | **Complete** | Full AST analysis, 31+ semantic event types, decorators, async/await, generators, comprehensions, type annotations |
| **JavaScript** | `.js`, `.jsx`, `.mjs` | **Basic** | Functions, classes, imports/requires, ES6+ features |
| **TypeScript** | `.ts`, `.tsx` | **Basic** | Functions, classes, imports, type definitions |
| **Go** | `.go` | **Basic** | Functions, structs, packages, imports, method receivers |
| **PHP** | `.php`, `.phtml`, `.php3-5`, `.phps` | **Basic** | Classes, interfaces, traits, methods, properties, namespaces |

**Note**: Only Python has comprehensive semantic analysis. Other languages provide basic structural change detection.

## 🚀 What Makes SVCS Different

Traditional version control systems like Git track textual changes. SVCS goes deeper by analyzing:

- **Function signature changes** - When parameters are added, removed, or modified
- **Dependency modifications** - New imports, removed dependencies
- **Control flow changes** - New loops, conditionals, exception handling
- **Logic transformations** - How the actual behavior of functions evolves
- **Internal call patterns** - Changes in how functions interact
- **Async/await patterns** - Conversion between sync/async code
- **Generator patterns** - Functions becoming generators or vice versa
- **Decorator usage** - Addition and removal of decorators
- **Class inheritance** - Changes in base classes and method signatures
- **Operator usage** - Patterns in arithmetic, logical, and comparison operations
- **Data access patterns** - How objects and data structures are accessed
- **Scope management** - Global and nonlocal variable usage
- **Comprehension patterns** - List, dict, set, and generator comprehensions
- **Exception handling** - Try/catch block modifications
- **Code quality patterns** - Assert statements and testing patterns

### 🔬 Deep Semantic Analysis

SVCS performs AST (Abstract Syntax Tree) analysis to understand:

- **Structural Changes**: Function and class definitions, method additions/removals
- **Behavioral Changes**: Control flow modifications, exception handling patterns
- **Architectural Changes**: Inheritance hierarchies, decorator applications
- **Performance Patterns**: Comprehensions vs loops, generator usage
- **Async Patterns**: Async/await adoption, coroutine conversions
- **Data Patterns**: How data is accessed, manipulated, and transformed
- **Quality Patterns**: Assertion usage, error handling improvements

## 📋 Features

### Core Capabilities
- **🧠 5-Layer Analysis System** - From basic AST to AI-powered semantic understanding
- **🤖 Intelligent LLM Filtering** - AI analysis only for complex, non-trivial changes  
- **⚡ Automatic Git Integration** - Runs complete analysis on every commit via post-commit hooks
- **🌍 Multi-Language Support** - Python, JavaScript/TypeScript, Go, and PHP
- **💬 Conversational Queries** - Natural language interface for exploring code history
- **📊 Database Storage** - SQLite with full semantic event metadata including AI insights
- **🎯 Resource Management** - Prevents expensive LLM calls for trivial changes

### 🚀 What Makes SVCS Different

Traditional VCS tracks textual changes. SVCS tracks **semantic meaning**:

#### **Structural Changes** (Layers 1-2)
- Function signature changes, new classes, dependency modifications
- Control flow changes, exception handling patterns

#### **Behavioral Analysis** (Layers 3-4)  
- Logic transformations, async/await patterns, generator usage
- Data access patterns, comprehension adoption

#### **AI-Powered Insights** (Layer 5a)
- Error handling pattern improvements
- Code quality enhancements, functional programming adoption

#### **True Semantic Understanding** (Layer 5b) 🤖
- **Architecture improvements** - Design pattern adoption, structural enhancements
- **Performance optimizations** - Caching, algorithmic improvements  
- **Maintainability gains** - Code organization, readability improvements
- **Abstract concept detection** - Intent and design philosophy changes

### LLM Filtering

SVCS determines when to use expensive AI analysis:

#### **LLM Analysis Triggered For:**
- ✅ Complex algorithms with multiple classes/functions
- ✅ Meaningful optimizations (caching, performance improvements)
- ✅ Architecture changes affecting code structure  
- ✅ Files with high complexity scores (imports, decorators, control flow)

#### **LLM Analysis Skipped For:**
- ⚡ Very small files (≤5 lines)
- ⚡ Trivial changes (comments, whitespace, simple literals)
- ⚡ Low complexity changes (basic variable assignments)
- ⚡ String literal or constant-only modifications

### 🎯 Event Types Tracked

SVCS detects and categorizes semantic events across all 5 layers:

#### **Core Events (Layers 1-4)**
- `node_added` - New functions, classes, or methods created
- `node_removed` - Functions, classes, or methods deleted
- `node_signature_changed` - Function/method signatures modified
- `node_logic_changed` - Internal implementation changes (fallback)

#### **Dependency & Import Changes**
- `dependency_added` - New imports or dependencies
- `dependency_removed` - Removed imports or dependencies

#### **Function Call & Interaction Changes**
- `internal_call_added` - New function calls within methods
- `internal_call_removed` - Removed function calls

#### **Exception & Error Handling**
- `exception_handling_added` - New exception handlers added

#### **Control Flow & Structure**
- `control_flow_changed` - Changes in loops, conditionals, context managers

#### **Async/Await Patterns**
- `function_made_async` - Function converted to async
- `function_made_sync` - Async function converted to sync
- `await_usage_changed` - Changes in await call patterns

#### **Generator & Return Patterns**
- `function_made_generator` - Function converted to generator (added yield)
- `generator_made_function` - Generator converted to regular function
- `return_pattern_changed` - Changes in return statement usage
- `yield_pattern_changed` - Changes in yield statement patterns

#### **Decorator Changes**
- `decorator_added` - New decorators applied
- `decorator_removed` - Decorators removed

#### **Comprehension & Functional Programming**
- `comprehension_usage_changed` - Changes in list/dict/set comprehensions
- `lambda_usage_changed` - Changes in lambda function usage

#### **Scope & Variable Management**
- `global_scope_changed` - Changes in global variable declarations
- `nonlocal_scope_changed` - Changes in nonlocal variable declarations
- `assignment_pattern_changed` - Changes in variable assignment patterns
- `augmented_assignment_changed` - Changes in augmented assignments (+=, -=, etc.)

#### **Operator Usage Patterns**
- `binary_operator_usage_changed` - Changes in arithmetic/binary operators
- `unary_operator_usage_changed` - Changes in unary operators (-, +, not)
- `comparison_operator_usage_changed` - Changes in comparison operators
- `logical_operator_usage_changed` - Changes in logical operators (and, or)

#### **Data Access Patterns**
- `attribute_access_changed` - Changes in object attribute access
- `subscript_access_changed` - Changes in list/dict subscript access

#### **Class-Specific Changes**
- `inheritance_changed` - Changes in base classes
- `class_methods_changed` - Methods added or removed from classes
- `class_attributes_changed` - Class attributes modified

#### **Code Quality & Testing**
- `assertion_usage_changed` - Changes in assert statement usage

#### **File-Level Changes**
- `file_content_changed` - Non-code or top-level script changes

#### **Exception & Error Handling (Extended)**
- `exception_handling_removed` - Exception handlers removed
- `error_handling_introduced` - Error handling added to previously unguarded code
- `error_handling_removed` - All error handling removed from function

#### **Literal & Constant Patterns**
- `string_literal_usage_changed` - Changes in string literal patterns
- `numeric_literal_usage_changed` - Changes in numeric literal usage
- `boolean_literal_usage_changed` - Changes in boolean literal patterns
- `none_literal_usage_changed` - Changes in None literal usage

#### **Language Features**
- `starred_expression_usage_changed` - Changes in *args/**kwargs usage
- `slice_usage_changed` - Changes in slice expression patterns
- `nested_class_usage_changed` - Changes in nested class definitions
- `default_parameters_added` - Default parameter values introduced
- `default_parameters_removed` - Default parameter values removed

#### **Code Complexity & Architecture**
- `function_complexity_changed` - Overall function complexity changes
- `type_annotations_introduced` - Type annotation support added
- `type_annotations_removed` - Type annotation support removed
- `functional_programming_adopted` - Introduction of functional programming patterns
- `functional_programming_removed` - Removal of functional programming patterns

#### **Layer 5a Events (AI Pattern Recognition)**
- `error_handling_pattern_improved` - Enhanced exception handling strategies
- `functional_programming_adopted` - Introduction of functional programming patterns
- `code_quality_pattern_improved` - Overall code quality enhancements
- `performance_pattern_optimized` - Performance-related pattern improvements

#### **Layer 5b Events (True AI Analysis)** 🤖
- `abstract_architecture_change` - High-level architectural improvements
- `abstract_performance_optimization` - AI-detected performance enhancements
- `abstract_maintainability_improvement` - Code maintainability and organization gains
- `abstract_readability_improvement` - Enhanced code clarity and documentation
- `abstract_abstraction_improvement` - Better abstraction and separation of concerns
- `abstract_error_strategy_change` - Error handling strategy evolution

## 🌍 Multi-Language Support

SVCS supports semantic analysis across multiple programming languages:

### 🐍 **Python** (Complete Support)
- **File Extensions**: `.py`, `.pyw`, `.pyi`
- **Features**: Full AST analysis with 31+ semantic event types
- **Supported Constructs**: Functions, classes, decorators, async/await, generators, comprehensions, type annotations, exception handling

### 🌐 **JavaScript/TypeScript** 
- **File Extensions**: `.js`, `.jsx`, `.ts`, `.tsx`, `.mjs`
- **Supported Constructs**: Functions, classes, imports/requires, ES6+ features
- **Detection**: Arrow functions, class definitions, module imports

### 🐹 **Go**
- **File Extensions**: `.go`
- **Supported Constructs**: Functions, structs, packages, imports
- **Detection**: Method receivers, struct definitions, package imports

### 🐘 **PHP** (New!)
- **File Extensions**: `.php`, `.phtml`, `.php3`, `.php4`, `.php5`, `.phps`
- **Supported Constructs**: Classes, interfaces, traits, methods, properties, constants
- **Features**: 
  - Namespace declarations
  - Interface implementations
  - Trait usage
  - Property and constant definitions
  - Exception handling
  - Use statements and includes

### 🔧 **Multi-Language Analytics**
```bash
# Test multi-language support
python3 svcs_multilang.py

# View language-specific statistics
python3 demo_php_support.py   # For PHP-specific insights
```

Each language analyzer automatically detects semantic patterns specific to that language while maintaining consistent event types across the system.

## 🛠️ **Installation**

**Note**: SVCS uses symbolic links for git hooks and is designed for Unix-based systems (Linux, macOS). Windows support requires WSL.

### **1. Install with Virtual Environment** (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/svcs.git
cd svcs

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows WSL: venv/bin/activate

# Install MCP server
cd svcs_mcp
pip install -e .

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

## � **Quick Start**

### **1. Register a Project**

```bash
# Navigate to your git project
cd your-project

# Register with SVCS MCP server
svcs init --name "My Project" .
```

### **2. Make Changes and Commit**

```bash
# Create a test file
echo "def hello(): return 'world'" > test.py
git add test.py
git commit -m "Add hello function"

# SVCS automatically analyzes the commit
# You'll see semantic analysis output in the terminal
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

### **MCP Server Interface**

Modern AI-integrated interface for multiple projects:

```bash
# List all registered projects
# (Via MCP tools in your AI assistant)
> list svcs projects

# Get project statistics
> show stats for /path/to/project

# Search semantic patterns
> find performance improvements in my project
> show recent architecture changes
```

### **Conversational Interface (`svcs_discuss.py`)**

Natural language queries about code evolution:

```bash
# Start interactive session
export GOOGLE_API_KEY="your_key"
python3 svcs_discuss.py

# Example queries:
"What performance optimizations were made last week?"
"Show me all dependency changes by Alice"
"How has the DataProcessor class evolved?"
"Which commits had the most significant semantic changes?"
```

### **Analytics & Quality (`svcs_analytics.py`, `svcs_quality.py`)**

Generate insights about code quality evolution:

```bash
# Generate comprehensive analytics report
python3 svcs_analytics.py

# Quality trend analysis
python3 svcs_quality.py

# Web dashboard generation
python3 svcs_web.py
```

### **CI/CD Integration (`svcs_ci.py`)**

Integrate semantic analysis into your development workflow:

```bash
# Run PR analysis
python3 svcs_ci.py --pr-analysis --target=main

# Quality gate checking
python3 svcs_ci.py --quality-gate

# Generate PR report
python3 svcs_ci.py --generate-report
```

### **Multi-Language Support (`svcs_multilang.py`)**

Analyze semantic changes across different programming languages:

```bash
# Test multi-language support
python3 svcs_multilang.py

# PHP-specific analysis
python3 tests/demo_php_support.py

# JavaScript/TypeScript analysis  
# (automatically detected based on file extensions)
```

## 📚 **Detailed Module Documentation**

### **Core Analysis Engine**

#### **`svcs.py` - Main CLI Interface**
The primary command-line interface for interacting with SVCS semantic history.

**Key Features:**
- Rich terminal output with filtering capabilities
- Event type and layer-based queries
- Author and time-based filtering
- Database maintenance operations

**Usage Examples:**
```bash
# Basic queries
python3 svcs.py log                           # All events
python3 svcs.py log --limit 20                # Recent 20 events
python3 svcs.py log --author "John Doe"       # By author

# Advanced filtering
python3 svcs.py log --type "node_added"       # Specific event types
python3 svcs.py log --layer "5b"              # AI-detected events only
python3 svcs.py log --min-confidence 0.8      # High-confidence events

# Maintenance
python3 svcs.py prune                         # Clean orphaned data
```

#### **`svcs_discuss.py` - Conversational AI Interface**
Natural language interface for exploring semantic code evolution using Google Gemini.

**Key Features:**
- Natural language query processing
- Context-aware responses about code evolution
- Integration with all SVCS data layers
- Rich markdown output formatting

**Prerequisites:**
```bash
export GOOGLE_API_KEY="your_gemini_api_key"
```

**Example Conversations:**
```
User: "What performance optimizations happened last month?"
AI: "I found 3 performance optimizations in the last month:
     - Caching implementation in DataProcessor (90% confidence)
     - Algorithm optimization in sort_function (85% confidence)
     - Database query batching in UserService (80% confidence)"

User: "Show me all architecture changes by Alice"
AI: "Alice made 5 architecture changes:
     - Introduced Repository pattern in user management
     - Refactored authentication to use strategy pattern
     - Extracted service layer from controllers"
```

### **Analytics & Insights**

#### **`svcs_analytics.py` - Data Analytics Engine**
Comprehensive analytics and reporting system for code evolution patterns.

**Features:**
- Temporal analysis of semantic changes
- Developer contribution patterns
- Code quality trend analysis
- Event type distribution statistics

**Generated Reports:**
```bash
python3 svcs_analytics.py

# Generates:
# - reports/svcs_analytics_report.json
# - Time-series data for visualization
# - Developer activity summaries
# - Quality metric trends
```

**Report Contents:**
- Total events by layer and type
- Most active developers and time periods
- Quality improvement patterns
- Architecture evolution timelines

#### **`svcs_quality.py` - Code Quality Insights**
Focused analysis of code quality evolution using AI-detected patterns.

**Key Metrics:**
- Error handling pattern improvements
- Code maintainability trends
- Performance optimization detection
- Technical debt accumulation/reduction

**Usage:**
```bash
python3 svcs_quality.py

# Outputs:
# - Quality trend analysis
# - Hotspot identification (files needing attention)
# - Recommendation engine for improvements
# - Quality gate status for CI/CD
```

#### **`svcs_web.py` - Web Dashboard Generator**
Creates interactive HTML dashboards for visualizing semantic evolution.

**Features:**
- Interactive timeline of semantic changes
- Network graphs of code relationships
- Quality metrics visualization
- Developer activity heatmaps

**Generated Output:**
```bash
python3 svcs_web.py

# Creates:
# - svcs_dashboard.html (interactive dashboard)
# - Embedded JavaScript for interactivity
# - CSS styling for professional presentation
```

### **CI/CD Integration**

#### **`svcs_ci.py` - Continuous Integration Support**
Integration module for incorporating semantic analysis into development workflows.

**Core Functions:**
- **PR Analysis**: Semantic impact assessment of pull requests
- **Quality Gates**: Automated quality checks based on semantic patterns
- **Trend Monitoring**: Continuous quality trend analysis
- **Report Generation**: Automated reporting for stakeholders

**Usage in CI Pipeline:**
```yaml
# Example GitHub Actions workflow
- name: SVCS Semantic Analysis
  run: |
    python3 svcs_ci.py --pr-analysis --target=main
    python3 svcs_ci.py --quality-gate --fail-on-regression
```

**Quality Gate Checks:**
- Complexity increase detection
- Error handling coverage requirements
- Performance regression detection
- Architecture consistency validation

### **Multi-Language Support**

#### **`svcs_multilang.py` - Language Extension Framework**
Extensible framework for analyzing semantic changes across programming languages.

**Supported Languages:**
- **Python** (.py, .pyw, .pyi) - Full support with 31+ semantic event types
- **JavaScript/TypeScript** (.js, .jsx, .ts, .tsx, .mjs) - Function and class analysis
- **Go** (.go) - Function, struct, and package analysis
- **PHP** (.php, .phtml) - Class, interface, trait, and method analysis

**Architecture:**
```python
class LanguageAnalyzer(ABC):
    @abstractmethod
    def parse_code(self, content: str) -> Dict[str, Any]:
        """Parse source code into semantic components"""
    
    @abstractmethod  
    def detect_changes(self, before: Dict, after: Dict) -> List[Dict]:
        """Detect semantic changes between versions"""
```

**Adding New Languages:**
1. Implement `LanguageAnalyzer` interface
2. Add file extension mapping
3. Define language-specific semantic patterns
4. Test with comprehensive examples

### **MCP Server Architecture**

#### **`svcs_mcp/` - Model Context Protocol Server**
Modern AI-integrated architecture for managing multiple SVCS projects.

**Key Components:**

##### **`working_mcp_server.py` - Production MCP Server**
- Fully functional MCP server implementation
- Global database management across projects
- AI tool integration for semantic queries
- Real-time project registration and analysis

**Available MCP Tools:**
```
- list_projects              # List all registered SVCS projects
- register_project           # Register new project for tracking
- get_project_statistics     # Get semantic statistics for project
- query_semantic_events      # Query events with filtering
- get_recent_activity        # Get recent semantic changes
- search_semantic_patterns   # AI-powered pattern search
- get_filtered_evolution     # Track specific code element evolution
- search_events_advanced     # Advanced filtering and search
- analyze_current_commit     # Analyze most recent commit
```

##### **`cli.py` - Command Line Interface**
Project management CLI for the MCP server:

```bash
# Project lifecycle management
svcs init --name "My Project" /path/to/project     # Register and setup
svcs list                                          # List all projects
svcs status /path/to/project                       # Check project status
svcs remove /path/to/project                       # Unregister project

# Global operations
svcs --version                                     # Show version info
svcs --help                                        # Show help
```

##### **`git_hooks.py` - Global Hook Management**
Manages git hooks across multiple projects:

- **Global Hook Script**: Single script in `~/.svcs/hooks/`
- **Project Symlinks**: Links from project `.git/hooks/` to global script
- **Automatic Routing**: Routes analysis requests to MCP server
- **Clean Installation/Removal**: Safe hook management

##### **`semantic_analyzer.py` - Analysis Engine**
Integration layer between MCP server and existing SVCS analysis:

- **Legacy Integration**: Works with existing `.svcs/` project structure
- **Data Migration**: Migrates existing semantic data to global database
- **Real-time Analysis**: Processes commits through MCP architecture
- **Multi-project Support**: Handles analysis for multiple projects simultaneously

### **Testing & Demonstration**

#### **`tests/` Directory - Comprehensive Test Suite**

##### **Integration Tests:**
- `test_svcs_complete_5layer.py` - Full system integration test
- `test_all_layers.py` - Individual layer verification
- `test_mcp_*.py` - MCP server functionality tests

##### **AI Analysis Tests:**
- `test_svcs_layer5_true_ai.py` - Google Gemini integration tests
- `test_layer5_manual.py` - Manual AI analysis verification
- `test_llm_*.py` - LLM interaction and response tests

##### **Language Support Tests:**
- `test_svcs_multilang.py` - Multi-language analysis tests
- `demo_php_support.py` - PHP-specific semantic analysis
- Various language-specific test files

##### **Feature Demonstrations:**
- `demo_*.py` - Individual feature demonstrations
- `comprehensive_test.py` - Showcase of all semantic patterns
- `time_crystal_demo.py` - Complete system demonstration

#### **`time_crystal_demo.py` - Complete System Showcase**
Demonstrates the full "Time Crystal VCS" vision with all 5 layers working together:

```bash
python3 time_crystal_demo.py

# Shows:
# - Layer 1-2: Structural analysis (AST changes)
# - Layer 3-4: Behavioral analysis (logic patterns)  
# - Layer 5a: AI pattern recognition
# - Layer 5b: True semantic understanding
# - Multi-language support demonstration
```

### **Advanced Features**

#### **Database Schema & Storage**
SVCS uses SQLite with a sophisticated schema optimized for semantic analysis:

**Core Tables:**
- `projects` - Registered project metadata
- `commits` - Git commit information with semantic context  
- `semantic_events` - Detailed semantic change events
- `files` - File-level tracking and metadata

**Advanced Fields:**
- `layer` - Analysis layer (core, 5a, 5b)
- `confidence` - AI confidence score (0.0-1.0)
- `reasoning` - LLM reasoning for detected changes
- `impact` - Change impact description
- `semantic_node` - Specific code element affected

#### **Logging & Debugging**
Comprehensive logging system for monitoring and debugging:

**Log Files:**
- `layer5b_semantic_analysis_YYYY-MM-DD.jsonl` - AI interaction logs
- `layer5b_parse_results_YYYY-MM-DD.jsonl` - AI response parsing logs
- `mcp_server.log` - MCP server operational logs
- `git_hooks.log` - Git hook execution logs

**Debug Information:**
- Full LLM prompts and responses
- Timing information for each analysis layer
- Error tracking and recovery
- Performance metrics

#### **Performance Optimization**
SVCS includes several performance optimizations:

**Intelligent Filtering:**
- Skip LLM analysis for trivial changes (saves API costs)
- Complexity scoring to determine analysis depth
- File size and change magnitude thresholds

**Caching:**
- Database-backed semantic event caching
- LLM response caching for similar code patterns
- Git metadata caching for faster queries

**Parallel Processing:**
- Multi-file change analysis in parallel
- Background processing for large repositories
- Asynchronous MCP server operations

## � **Requirements & Dependencies**

### **System Requirements**
- Python 3.8+ (recommended: Python 3.11+)
- Git 2.0+ 
- 4GB+ RAM (for AI analysis)
- 1GB+ disk space (for databases and logs)

### **Core Dependencies**
```bash
# Essential packages (auto-installed)
rich>=10.0.0              # Terminal UI and formatting
google-generativeai>=0.3.0 # Gemini AI integration
click>=8.0.0               # CLI framework
sqlite3                    # Database (built-in)

# MCP Server dependencies
mcp>=0.1.0                 # Model Context Protocol
asyncio                    # Async support (built-in)
pathlib                    # Path handling (built-in)

# Optional but recommended
pytest>=6.0.0              # Testing framework
black>=22.0.0              # Code formatting
```

### **API Requirements**
- **Google API Key** - Required for Layer 5b AI analysis and conversational interface
  - Get one at [Google AI Studio](https://makersuite.google.com/app/apikey)
  - Free tier: 1000 requests/day (sufficient for most projects)
  - Paid tier: Higher limits for enterprise use

### **Performance Characteristics**
- **Layer 1-4 analysis**: ~100-200ms per commit (fast, always runs)
- **Layer 5a analysis**: ~200-500ms per commit (pattern-based AI)
- **Layer 5b analysis**: ~2-10s per commit (only for complex changes)
- **MCP server startup**: ~500ms (global database initialization)
- **Database queries**: ~10-50ms (optimized with indices)

### **Resource Usage**
- **Memory**: 50-200MB per project (depending on history size)
- **Disk**: 10-100MB per project (SQLite database + logs)
- **Network**: Minimal (only for AI API calls on complex changes)
- **CPU**: Low (efficient AST parsing and caching)

## 🤝 **Contributing**

SVCS is designed to be extensible across multiple dimensions:

### **Contribution Areas**

1. **Layer 5b AI Enhancements** 🤖
   - Improve LLM prompts for better semantic understanding
   - Add support for additional LLM providers (OpenAI, Anthropic, local models)
   - Fine-tune filtering logic for different project types

2. **Language Support Expansion** 🌍  
   - Extend beyond current languages to Rust, C++, Java, etc.
   - Language-specific semantic pattern detection
   - Cross-language architectural change detection

3. **Analytics & Visualization** 📊
   - Visual representations of semantic evolution over time
   - Code quality trend analysis using AI insights
   - Architecture drift detection and alerting

4. **Integration & Tooling** 🔧
   - IDE extensions (VS Code, IntelliJ, etc.)
   - CI/CD pipeline integration for semantic change gates
   - Code review tools that surface semantic insights
   - GitHub/GitLab webhook integration

5. **Performance & Optimization** ⚡
   - Incremental analysis for large codebases
   - Parallel processing for multi-file changes
   - Caching of LLM results

### **Research Areas**

- **Semantic Change Impact Prediction** - Use AI to predict the impact of proposed changes
- **Code Evolution Patterns** - Identify common semantic evolution patterns across projects
- **Automated Refactoring Suggestions** - AI-powered suggestions based on semantic analysis
- **Cross-Project Learning** - Transfer learning from semantic patterns across repositories

### **Development Setup**

```bash
# Clone and setup development environment
git clone https://github.com/your-org/svcs.git
cd svcs

# Install in development mode
pip install -e .
pip install -e svcs_mcp/

# Run tests
python3 -m pytest tests/
python3 tests/test_svcs_complete_5layer.py

# Set up pre-commit hooks
pip install pre-commit
pre-commit install
```

## �📄 License

[MIT License - Specify your license here]

## 🆘 Troubleshooting

### Common Issues

**"SVCS database not found"**
```bash
# Re-run setup to initialize database
./setup.sh
```

**"No such column: e.author"**
```bash
# Database schema issue - reinitialize
rm .svcs/history.db
python3 .svcs/main.py
```

**Permission denied on Git hooks**
```bash
chmod +x .git/hooks/post-commit
```

### Getting Help

1. **Check the complete 5-layer analysis**: `python3 tests/test_svcs_complete_5layer.py`
2. **Verify AI integration**: Ensure `GOOGLE_API_KEY` is set and valid
3. **Check Git hook installation**: Verify `.git/hooks/post-commit` exists and is executable
4. **Review logs**: Check `.svcs/logs/` for LLM interaction logs
5. **Database inspection**: Use SQLite browser to examine `.svcs/history.db`

### Debugging LLM Issues

```bash
# Test LLM integration directly
python3 tests/test_svcs_layer5_true_ai.py

# Check if filtering is working correctly  
git commit --allow-empty -m "Test commit to trigger analysis"

# Review LLM logs
cat .svcs/logs/layer5b_semantic_analysis_$(date +%Y-%m-%d).jsonl | tail -1 | jq .
```

---

## 🌟 **Conclusion**

SVCS represents a paradigm shift in version control, moving beyond traditional line-based diffs to **semantic understanding** of code evolution. By combining AST analysis with AI-powered insights, SVCS provides unprecedented visibility into how your codebase evolves over time.

### **Key Benefits:**

- **🧠 Semantic Awareness**: Understand *what* changed, not just *where*
- **🤖 AI Integration**: Leverage modern LLM capabilities for code analysis  
- **📊 Quality Insights**: Track code quality evolution with concrete metrics
- **🔧 Developer Productivity**: Make informed decisions based on semantic patterns
- **🌍 Multi-Language**: Consistent analysis across different programming languages

### **Getting Started:**

1. **Install**: Run the setup script in your project
2. **Configure**: Set your Google API key for AI features
3. **Commit**: Make code changes and watch SVCS analyze them
4. **Explore**: Use the conversational interface to ask questions about your code
5. **Scale**: Register multiple projects with the MCP server

### **Future Vision:**

SVCS is the foundation for the **"Time Crystal VCS"** concept - a version control system that understands the temporal and semantic dimensions of code evolution. As AI capabilities advance, SVCS will continue to provide deeper insights into software development patterns and help teams build better software through semantic understanding.

**Start your semantic version control journey today!**

```bash
# Quick start
git clone https://github.com/your-org/svcs.git
cd your-project
/path/to/svcs/setup.sh
export GOOGLE_API_KEY="your_key"
git commit -m "Begin semantic tracking" --allow-empty
```

---

**SVCS - Where every commit tells a semantic story.** 🚀


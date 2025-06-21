# SVCS - Semantic Version Control System

A version control system that tracks the **semantic meaning** of code changes, not just line-by-line diffs. SVCS uses a **5-Layer Analysis System** combining Abstract Syntax Tree (AST) analysis with AI-powered semantic understanding to capture what your code changes actually *mean*.

## 🧠 5-Layer Analysis Architecture

SVCS employs a multi-layer analysis system:

### **Core Layers (1-4): Structural & Syntactic Analysis**
- **Layer 1-2**: AST parsing and structural changes (functions, classes, imports)
- **Layer 3-4**: Behavioral patterns (control flow, data access, complexity)

### **Layer 5a: AI Pattern Recognition** 
- Pattern detection using rule-based AI
- Identifies architectural and quality improvements
- Detects error handling patterns and functional programming adoption

### **Layer 5b: True AI Abstract Analysis** 🤖
- **LLM-Powered Semantic Understanding** using Google Gemini
- **Intelligent Filtering**: Only analyzes non-trivial, complex changes
- Detects abstract concepts like:
  - Architecture improvements and design pattern adoption
  - Performance optimizations and maintainability enhancements  
  - Code readability improvements and abstraction refinements
  - Error handling strategy changes

### **Multi-Language Support**
- Python, JavaScript/TypeScript, Go, PHP support
- Language-agnostic semantic event detection

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

## 🛠️ Installation & Setup

### Quick Start
```bash
# Clone or navigate to your project directory
cd your-project

# Run the setup script
chmod +x setup.sh
./setup.sh

# Set up Google API key for AI features (optional but recommended)
export GOOGLE_API_KEY="your_gemini_api_key_here"
```

The setup script will:
1. Create proper project structure (`src/`, `tests/`, `docs/`)
2. Initialize Git repository (if needed)
3. Set up the complete 5-layer SVCS analysis engine in `.svcs/` directory
4. Install Git post-commit hook for automatic analysis
5. Create isolated Python environment with all dependencies (`rich`, `google-generativeai`)
6. Initialize SQLite database with enhanced schema for AI analysis
7. Configure intelligent LLM filtering system

### Verification
After setup, test with a commit:
```bash
# Make any change to a Python file
echo "def test(): return 'hello'" > test_file.py
git add test_file.py
git commit -m "Test SVCS 5-layer analysis"

# You should see analysis output:
# 🚀 SVCS COMPLETE 5-LAYER SEMANTIC ANALYSIS 🚀
# ✅ Complete 5-Layer Analyzer Available
# 📊 Layer Status:
#    ✅ Core (1-4): Structural & Syntactic  
#    ✅ Layer 5a: AI Pattern Recognition
#    ✅ Layer 5b: True AI Abstract Analysis
#    ✅ Multi-lang: Multi-language Support
# ⚡ Skipping LLM analysis for trivial change (intelligent filtering)
# 💾 Stored X semantic events in database
```

### Manual Setup
If you prefer manual setup:

```bash
# Initialize SVCS directory structure
mkdir -p .svcs
cd .svcs

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install rich google-generativeai

# Copy SVCS core files to .svcs/
# (main.py, analyzer.py, parser.py, storage.py, api.py)

# Install Git hook
cp .svcs/post-commit .git/hooks/
chmod +x .git/hooks/post-commit
```

## 📖 Usage

### Automatic Analysis (Default Behavior)

SVCS automatically runs complete 5-layer analysis on every Git commit:

```bash
# Any normal Git workflow triggers analysis
git add your_file.py
git commit -m "Your commit message"

# SVCS automatically analyzes the changes and shows:
# - Core structural/syntactic changes (Layers 1-4)
# - AI pattern recognition results (Layer 5a) 
# - LLM semantic insights for complex changes (Layer 5b)
# - Intelligent filtering decisions (LLM called vs skipped)
```

### Manual Analysis

Run analysis on-demand:

```bash
# Complete 5-layer analysis
python3 tests/test_svcs_complete_5layer.py

# Test specific layers
python3 tests/test_svcs_layer5_true_ai.py  # Layer 5b AI analysis
python3 tests/test_svcs_layer5_ai.py       # Layer 5a pattern recognition
```

### CLI Interface for Querying Results

#### View Complete Semantic History
```bash
python3 svcs.py log
```

#### Filter by Author
```bash
python3 svcs.py log --author="John Doe"
```

#### Filter by Event Type
```bash
python3 svcs.py log --type="node_signature_changed"
```

#### Filter by Function/Node
```bash
python3 svcs.py log --node="func:greet"
```

#### Filter by Layer
```bash
python3 svcs.py log --layer="5b"  # Show only AI semantic insights
python3 svcs.py log --layer="5a"  # Show only AI pattern recognition
python3 svcs.py log --layer="core" # Show only structural changes
```

#### Complex Queries
```bash
# Recent AI insights with high confidence
python3 svcs.py log --layer="5b" --min-confidence=0.8

# Performance optimizations detected by AI
python3 svcs.py log --type="abstract_performance_optimization"

# Show LLM reasoning for specific changes
python3 svcs.py log --layer="5b" --show-reasoning
```

### Conversational Interface 🤖
```bash
# Natural language queries about your code evolution
python3 svcs_discuss.py

# Example queries:
# "What performance optimizations were made last week?"
# "Show me all architecture changes in the DataProcessor class"
# "Which commits had the most significant semantic changes?"
```

#### Combine Filters
```bash
python3 svcs.py log --author="John Doe" --type="dependency_added"
```

#### Clean Orphaned Data
```bash
python3 svcs.py prune
```

### Conversational Interface

For natural language queries about your code evolution:

```bash
# Set up Google AI API key
export GOOGLE_API_KEY="your_api_key_here"

# Start conversational interface
python3 svcs_discuss.py
```

Example conversations:
- "What functions have changed in the last week?"
- "Show me all dependency changes by Alice"
- "How has the main.py file evolved?"
- "What are the most common types of changes?"

## 🗂️ Project Structure

```
your-project/
├── src/                    # Main application code
│   └── main.py
├── tests/                  # Unit tests
│   ├── test_main.py
│   └── test_discuss.py
├── docs/                   # Documentation
│   └── index.md
├── .svcs/                  # SVCS analysis engine
│   ├── main.py            # Post-commit hook entry point
│   ├── analyzer.py        # AST semantic analysis
│   ├── parser.py          # Python AST parsing
│   ├── storage.py         # Database operations
│   ├── api.py             # Query interface
│   ├── history.db         # SQLite semantic events database
│   └── venv/              # Isolated Python environment
├── svcs.py                # Main CLI interface
├── svcs_discuss.py        # Conversational interface
├── setup.sh               # Setup script
└── README.md              # This file
```

## 📊 Example Output

### Complete 5-Layer Analysis
When you commit changes, SVCS runs analysis:

```
🚀 SVCS COMPLETE 5-LAYER SEMANTIC ANALYSIS 🚀
✅ Complete 5-Layer Analyzer Available
📊 Layer Status:
   ✅ Core (1-4): Structural & Syntactic
   ✅ Layer 5a: AI Pattern Recognition  
   ✅ Layer 5b: True AI Abstract Analysis
   ✅ Multi-lang: Multi-language Support
🔍 Analyzing commit: 6923478 (Parent: ff40c44)
📁 Processing file: complex_algorithm.py
✅ Google Generative AI configured successfully

💾 Stored 9 semantic events in database

📊 ANALYSIS SUMMARY
   5B: 2 events
   CORE: 7 events
```

### Detailed Event Analysis
```
                               Semantic Events for Commit 6923478                               
┏━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ Layer ┃ Event Type                           ┃ Node             ┃ Location         ┃ Details         ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ core  │ function_complexity_changed          │ func:_apply_mat… │ complex_algorit… │ Function        │
│       │                                      │                  │                  │ complexity      │
│       │                                      │                  │                  │ increased       │
│ 5b    │ abstract_performance_optimization    │ abstract:comple… │ complex_algorit… │ Introduction of │
│       │                                      │                  │                  │ caching to      │
│       │                                      │                  │                  │ improve         │
│       │                                      │                  │                  │ performance     │
│       │                                      │                  │                  │ (confidence:    │
│       │                                      │                  │                  │ 90.0%)          │
│ 5b    │ abstract_maintainability_improvement │ abstract:comple… │ complex_algorit… │ Improved code   │
│       │                                      │                  │                  │ maintainability │
│       │                                      │                  │                  │ through caching │
│       │                                      │                  │                  │ (confidence:    │
│       │                                      │                  │                  │ 80.0%)          │
└───────┴──────────────────────────────────────┴──────────────────┴──────────────────┴─────────────────┘
```

### Intelligent Filtering in Action
```
# For trivial changes:
⚡ Skipping LLM analysis for trivial change in simple_function.py

# For complex changes:  
🤖 Layer 5b: True AI Analysis detecting abstract semantic patterns...
💭 LLM Analysis: Architecture improvement with caching optimization
```

## 🔧 Configuration

### Environment Variables
- `GOOGLE_API_KEY` - **Required** for Layer 5b AI analysis and conversational interface
- `SVCS_DEBUG` - Enable debug output (optional)

### AI Analysis Configuration
SVCS intelligently manages LLM usage:

```python
# Automatic filtering prevents LLM calls for:
- Very small files (≤5 lines)
- Trivial changes (comments, whitespace, simple literals)  
- Low complexity changes (basic assignments, single line changes)
- Files with complexity score < 3

# LLM analysis triggered for:
- Complex algorithms with multiple classes/functions
- Architecture changes with significant structural impact
- Performance optimizations and caching implementations
- Files with high complexity scores (imports, decorators, control flow)
```

### Database Schema
SVCS uses SQLite with enhanced schema for AI analysis:
- `semantic_events` - Core semantic event data **with AI fields**:
  - `layer` - Analysis layer (core, 5a, 5b)
  - `confidence` - AI confidence score (0.0-1.0)
  - `reasoning` - LLM reasoning for the detected change  
  - `impact` - Description of the change's impact
  - `layer_description` - Human-readable layer description
- `commits` - Git commit metadata (author, timestamp, hash)

### Logging
- **LLM interactions** logged to `.svcs/logs/layer5b_semantic_analysis_YYYY-MM-DD.jsonl`
- **Parse results** logged to `.svcs/logs/layer5b_parse_results_YYYY-MM-DD.jsonl`
- Full prompt/response/metadata tracking for debugging and analysis

## 🚦 Requirements

- Python 3.8+
- Git repository
- **Google API Key** (for Layer 5b AI analysis) - Get one at [Google AI Studio](https://makersuite.google.com/app/apikey)
- Dependencies (auto-installed by setup script):
  - `rich` - Terminal output and tables
  - `google-generativeai` - Gemini LLM integration for semantic analysis

### Performance Notes
- **Layer 1-4 analysis**: Fast, runs on every commit (~100ms)
- **Layer 5a analysis**: Medium speed, pattern-based AI (~200ms)  
- **Layer 5b analysis**: Slower, only for complex changes (~2-5s when triggered)
- **Intelligent filtering**: Prevents unnecessary LLM calls, saving time and API costs

## 🤝 Contributing

SVCS is designed to be extensible across multiple dimensions:

### **Contribution Areas**

1. **Layer 5b AI Enhancements** 🤖
   - Improve LLM prompts for better semantic understanding
   - Add support for additional LLM providers (OpenAI, Anthropic, local models)
   - Fine-tune filtering logic for different project types

2. **Language Support Expansion** 🌍  
   - Extend beyond Python to Rust, C++, Java, etc.
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

## 📄 License

[Specify your license here]

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

**SVCS provides semantic understanding of code evolution by combining traditional version control with AI-powered analysis.**

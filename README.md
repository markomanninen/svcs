# SVCS - Semantic Version Control System

A revolutionary approach to version control that tracks the **semantic meaning** of code changes, not just line-by-line diffs. SVCS uses Abstract Syntax Tree (AST) analysis to understand what your code changes actually *mean*.

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

SVCS performs comprehensive AST (Abstract Syntax Tree) analysis to understand:

- **Structural Changes**: Function and class definitions, method additions/removals
- **Behavioral Changes**: Control flow modifications, exception handling patterns
- **Architectural Changes**: Inheritance hierarchies, decorator applications
- **Performance Patterns**: Comprehensions vs loops, generator usage
- **Async Patterns**: Async/await adoption, coroutine conversions
- **Data Patterns**: How data is accessed, manipulated, and transformed
- **Quality Patterns**: Assertion usage, error handling improvements

## 📋 Features

### ✨ Core Capabilities
- **Automatic Semantic Analysis** - Runs on every Git commit via post-commit hooks
- **Rich Query Interface** - Filter by author, event type, function name, or file location
- **Conversational Queries** - Natural language interface for exploring code history
- **Git Integration** - Seamlessly works with your existing Git workflows
- **Persistent History** - SQLite database stores semantic events with full metadata

### 🎯 Event Types Tracked

#### **Core Structural Changes**
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

## 🛠️ Installation & Setup

### Quick Start
```bash
# Clone or navigate to your project directory
cd your-project

# Run the comprehensive setup script
chmod +x setup.sh
./setup.sh
```

The setup script will:
1. Create proper project structure (`src/`, `tests/`, `docs/`)
2. Initialize Git repository (if needed)
3. Set up the SVCS analysis engine in `.svcs/` directory
4. Install Git post-commit hook for automatic analysis
5. Create isolated Python environment with dependencies

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

### CLI Interface

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

#### Filter by File Location
```bash
python3 svcs.py log --location="src/main.py"
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
├── setup.sh               # Comprehensive setup script
└── README.md              # This file
```

## 📊 Example Output

When you commit changes, SVCS automatically analyzes them:

```
--=[ SVCS Semantic Analysis ]=--
Stored 1 semantic events in the database.
                        Detected Semantic Events for Commit 4efaa18                        
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Event Type         ┃ Semantic Node ┃ Location    ┃ Details                                      ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ node_logic_changed │ func:greet    │ src/main.py │ The implementation of this node has changed. │
└────────────────────┴───────────────┴─────────────┴──────────────────────────────────────────────┘
```

Query results show rich, filterable history:

```
                               Filtered Semantic History                               
┏━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Commit  ┃ Author        ┃ Date            ┃ Event Type         ┃ Semantic Node ┃ Location    ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ 4efaa18 │ Marko Manninen│ 2025-06-18 20:25│ node_logic_changed │ func:greet    │ src/main.py │
└─────────┴───────────────┴─────────────────┴────────────────────┴───────────────┴─────────────┘
```

## 🔧 Configuration

### Environment Variables
- `GOOGLE_API_KEY` - Required for conversational interface
- `SVCS_DEBUG` - Enable debug output (optional)

### Database
SVCS uses SQLite for storage with these tables:
- `semantic_events` - Core semantic event data
- `commits` - Git commit metadata (author, timestamp, hash)

## 🚦 Requirements

- Python 3.8+
- Git
- Dependencies (auto-installed by setup script):
  - `rich` - Beautiful terminal output
  - `google-generativeai` - Conversational interface

## 🤝 Contributing

SVCS is designed to be extensible. Key areas for contribution:

1. **New Event Types** - Add detection for additional semantic patterns
2. **Language Support** - Extend beyond Python to other languages
3. **Visualization** - Create visual representations of semantic evolution
4. **Integration** - Connect with IDEs, CI/CD pipelines, code review tools

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

1. Check the setup script output for errors
2. Verify Git repository is properly initialized
3. Ensure Python virtual environment is activated
4. Check file permissions on `.svcs/` directory

---

**SVCS transforms how you understand your code's evolution. Start tracking the semantic story of your project today!**

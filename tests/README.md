# SVCS Tests

This directory contains various test scripts for the SVCS (Semantic Version Control System) project. Below are the most important and runnable test files:

## Main Test Scripts

### 🔗 `test_bare_hooks.py` - Bare Repository Hooks Test
**RECOMMENDED FOR VALIDATION**

This is the primary test script for validating SVCS bare repository hooks functionality.

```bash
cd tests
python test_bare_hooks.py
```

**What it tests:**
- Creation and initialization of bare repositories with SVCS
- Hook installation (post-receive, update) in bare repos
- Semantic analysis triggering during push operations
- Semantic event generation and storage
- Automatic semantic notes retrieval in fresh clones
- Database persistence and content verification

**Expected output:** Should detect 20+ semantic events and pass all critical tests.

### 🧪 `test_complete_functionality.py` - Comprehensive Feature Test
Tests the complete SVCS feature set including all layers of semantic analysis.

```bash
cd tests
python test_complete_functionality.py
```

### 🔄 `test_git_integration.py` - Git Integration Test
Tests SVCS integration with standard Git workflows.

```bash
cd tests
python test_git_integration.py
```

### 🎯 `test_cli_integration.py` - CLI Integration Test
Tests the SVCS command-line interface functionality.

```bash
cd tests
python test_cli_integration.py
```

## Specialized Test Scripts

### MCP (Model Context Protocol) Tests
- `test_mcp_debug.py` - Debug MCP server functionality
- `test_mcp_initialization.py` - Test MCP server initialization
- `test_mcp_query_tools.py` - Test MCP query capabilities

### API and Web Interface Tests
- `test_api_comprehensive.py` - Comprehensive API testing
- `test_web_api_comprehensive.py` - Web API endpoint testing
- `test_dashboard_js_fix.py` - Dashboard JavaScript functionality

### Semantic Analysis Tests
- `test_semantic.py` - Core semantic analysis testing
- `test_semantic_patterns_fix.py` - Semantic pattern detection
- `test_layer5_true_ai.py` - AI-powered semantic analysis

### Git Hook Tests
- `test_enhanced_semantic_hooks.py` - Enhanced hook functionality
- `test_hooks_basic.py` - Basic hook installation and execution

## Running Tests

### Prerequisites
Make sure you have the required dependencies installed:

```bash
# From the project root
pip install -r requirements.txt
```

### Running Individual Tests
Navigate to the tests directory and run any test script:

```bash
cd /path/to/svcs/tests
python test_name.py
```

### Running with Timeout (Recommended)
For tests that might hang, use timeout:

```bash
cd tests
gtimeout 60s python test_bare_hooks.py  # 60-second timeout
```

## Test Environment

### Configuration
Some tests may require environment configuration:
- `.env` file in the project root for AI/LLM settings
- Git configuration for commit author information
- Python virtual environment with dependencies

### Temporary Files
Most tests create temporary directories and clean up automatically. If a test is interrupted, you may need to manually clean up `/tmp` or similar temporary locations.

### Expected Behavior
- Tests should complete within reasonable time limits (30-60 seconds typically)
- Successful tests will show ✅ success indicators
- Failed tests will show ❌ error indicators with explanations

## Troubleshooting

### Common Issues
1. **Import Errors**: Make sure you're running from the tests directory
2. **Git Errors**: Ensure Git is properly configured with user.name and user.email
3. **Permission Errors**: Some tests may require write permissions to temporary directories
4. **Timeout Issues**: Use `gtimeout` command for tests that might hang

### Debug Mode
Many tests support verbose output. Check the test file for debug flags or verbose options.

## Contributing

When adding new tests:
1. Place them in this `tests/` directory
2. Use descriptive names starting with `test_`
3. Include proper error handling and cleanup
4. Update this README with test descriptions
5. Ensure tests are self-contained and don't require manual setup

## Test Categories

| Category | Purpose | Key Files |
|----------|---------|-----------|
| **Bare Repo** | Validate bare repository functionality | `test_bare_hooks.py` |
| **Git Integration** | Test Git workflow integration | `test_git_integration.py`, `test_complete_git_integration.py` |
| **CLI** | Command-line interface testing | `test_cli.py`, `test_cli_integration.py` |
| **API** | Web API and endpoint testing | `test_api_comprehensive.py`, `test_web_api_comprehensive.py` |
| **Semantic** | Semantic analysis and AI features | `test_semantic.py`, `test_layer5_true_ai.py` |
| **MCP** | Model Context Protocol testing | `test_mcp_*.py` |
| **Hooks** | Git hook functionality | `test_hooks_basic.py`, `test_enhanced_semantic_hooks.py` |

For more detailed information about SVCS, see the main [README.md](../README.md) in the project root.

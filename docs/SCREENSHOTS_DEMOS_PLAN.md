# SVCS Screenshots & Demos Production Plan

This document provides detailed task-level instructions for creating screenshots and demo videos for the SVCS project. Each section is designed to be followed step-by-step during screen recording sessions, with Copilot providing real-time guidance.

## 📋 Table of Contents

1. [Setup & Preparation](#setup--preparation)
2. [Core Feature Demonstrations](#core-feature-demonstrations)
3. [MCP Server Integration](#mcp-server-integration)
4. [Web Dashboard & Analytics](#web-dashboard--analytics)
5. [Project Management & Cleanup](#project-management--cleanup)
6. [Multi-Language Support Demos](#multi-language-support-demos)
7. [AI-Powered Features](#ai-powered-features)
8. [CLI Interface Demonstrations](#cli-interface-demonstrations)
9. [Real-World Use Cases](#real-world-use-cases)
10. [Production Quality Checks](#production-quality-checks)

---

## 🔧 Setup & Preparation

### Pre-Recording Checklist
- [ ] Clean terminal with readable font size (16-18pt)
- [ ] VS Code with SVCS MCP server configured
- [ ] Fresh clone of SVCS repository from GitHub
- [ ] Virtual environment created and activated
- [ ] All dependencies installed from requirements.txt AND requirements_web.txt
- [ ] Google API key set for Layer 5b features (optional)
- [ ] Clean browser for web dashboard demos
- [ ] Screen recording software configured (1080p minimum)
- [ ] Test project directory ready for demo

### Environment Setup Commands
```bash
# Clone the SVCS repository
git clone https://github.com/markomanninen/svcs.git
cd svcs

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install MCP server (provides 'svcs' command)
cd svcs_mcp
pip install -e .
cd ..

# Install ALL dependencies (includes language parsers)
pip install -r requirements.txt

# Install web dashboard dependencies
pip install -r requirements_web.txt

# Set API key (optional, for Layer 5b AI features)
export GOOGLE_API_KEY="your_key_here"

# Verify installation
svcs --help
python3 svcs.py --help

# Note: svcs (MCP CLI) has full features, svcs.py has basic log/prune only
# Use 'svcs' for all modern features, 'svcs.py' only for legacy log viewing

# Verify web dashboard
./start_dashboard.sh &
curl http://127.0.0.1:8080/health
```

---

## 🚀 Core Feature Demonstrations

### Demo 1: Initial Project Setup and First Analysis
**Duration**: 3-4 minutes
**Objective**: Show complete installation and first-time project setup

#### Recording Script:
1. **Create and setup demo project**
   ```bash
   mkdir demo_project && cd demo_project
   git init
   ```

2. **Register project with SVCS**
   ```bash
   svcs init --name "Demo Project" .
   ```
   - **Narration**: "SVCS registers the project and sets up git hooks automatically"

3. **Create initial code files**
   ```python
   # Create test.py
   def greet(name):
       return f"Hello, {name}!"
   
   class Calculator:
       def add(self, a, b):
           return a + b
   ```

4. **Make first commit and show analysis**
   ```bash
   git add test.py
   git commit -m "Initial implementation"
   ```
   - **Narration**: "Watch SVCS automatically analyze the semantic changes"

5. **Query the semantic history**
   ```bash
   svcs search --project . --limit 10
   ```
   - **Screenshot point**: Terminal output showing semantic events

#### Expected Outputs to Highlight:
- Git hook execution messages
- Semantic events detected (node_added, class_added, etc.)
- Rich terminal formatting with colors and structure

---

### Demo 2: 5-Layer Analysis in Action
**Duration**: 4-5 minutes
**Objective**: Demonstrate the progression through analysis layers

#### Recording Script:
1. **Show simple structural change (Layers 1-2)**
   ```python
   # Modify test.py - add parameter
   def greet(name, greeting="Hello"):
       return f"{greeting}, {name}!"
   ```
   ```bash
   git commit -am "Add greeting parameter"
   svcs search --project . --limit 5
   ```

2. **Show behavioral change (Layers 3-4)**
   ```python
   # Add error handling
   def greet(name, greeting="Hello"):
       if not name:
           raise ValueError("Name cannot be empty")
       return f"{greeting}, {name}!"
   ```
   ```bash
   git commit -am "Add input validation"
   svcs search --project . --limit 5
   ```

3. **Show pattern recognition (Layer 5a)**
   ```python
   # Refactor to functional style
   def validate_input(name):
       if not name:
           raise ValueError("Name cannot be empty")
       return name
   
   def format_greeting(name, greeting="Hello"):
       return f"{greeting}, {name}!"
   
   def greet(name, greeting="Hello"):
       validated_name = validate_input(name)
       return format_greeting(validated_name, greeting)
   ```
   ```bash
   git commit -am "Refactor to functional composition"
   svcs search --project . --limit 5
   ```

4. **Show AI analysis (Layer 5b) - if API key available**
   ```bash
   svcs search --project . --min-confidence 0.7 --limit 5
   ```

#### Screenshot Points:
- Layer progression in terminal output
- Different semantic event types by layer
- Confidence scores for AI analysis

---

## 🤖 MCP Server Integration

### Demo 3: VS Code MCP Integration
**Duration**: 4-5 minutes
**Objective**: Show SVCS working with AI assistants in VS Code

#### Recording Script:
1. **Show MCP configuration in VS Code**
   - Open VS Code settings.json
   - Show SVCS MCP server configuration

2. **Demonstrate MCP tools in chat**
   ```
   @copilot list svcs projects
   @copilot show recent activity for this project
   @copilot find performance improvements in my code
   @copilot analyze the current commit
   ```

3. **Show project management commands**
   ```
   @copilot register this project with SVCS
   @copilot get project statistics
   ```

4. **Demonstrate semantic queries**
   ```
   @copilot search for error handling patterns
   @copilot show functions that were added last week
   @copilot find architecture improvements with high confidence
   ```

5. **Show git integration queries**
   ```
   @copilot get changed files for commit abc123
   @copilot show me the diff for commit abc123
   @copilot summarize commit abc123
   ```

#### Screenshot Points:
- MCP server configuration
- Chat interface with SVCS responses
- Rich semantic data in AI responses
- Git integration features

---

## 📊 Web Dashboard & Analytics

### Demo 4: Interactive Web Dashboard
**Duration**: 6-7 minutes
**Objective**: Show the full web interface for SVCS data exploration

#### Recording Script:
1. **Launch dashboard**
   ```bash
   ./start_dashboard.sh
   ```
   - Open browser to http://127.0.0.1:8080

2. **Show main features**
   - Project selection dropdown
   - Timeline visualization
   - Event type filters
   - Author filters

3. **Demonstrate semantic search**
   - Use pattern search for "performance"
   - Filter by confidence scores
   - Show event details

4. **Show git integration**
   - Click on commit hash
   - View changed files
   - Show diff viewer
   - Demonstrate commit summary

5. **Show analytics section**
   - Quality trends over time
   - Developer activity patterns
   - Event type distribution

6. **Demonstrate evolution tracking**
   - Search for specific function
   - Show evolution timeline
   - Track method signature changes

#### Screenshot Points:
- Main dashboard overview
- Semantic search results
- Git integration features
- Analytics visualizations
- Evolution tracking interface

---

### Demo 5: Static Dashboard Generation
**Duration**: 2-3 minutes
**Objective**: Show HTML dashboard generation for sharing/reports

#### Recording Script:
1. **Generate static dashboard**
   ```bash
   python3 svcs_web.py
   ```

2. **Open generated HTML file**
   - Show browser opening svcs_dashboard.html
   - Navigate through interactive elements

3. **Highlight static features**
   - Standalone HTML (no server needed)
   - Interactive charts and graphs
   - Timeline visualization
   - Network diagrams

---

## 🗂️ Project Management & Cleanup

### Demo 6: Project Lifecycle Management
**Duration**: 5-6 minutes
**Objective**: Demonstrate complete project management features

#### Recording Script:
1. **Show project registration**
   ```bash
   # Register multiple projects
   svcs init --name "Project A" /path/to/project-a
   svcs init --name "Project B" /path/to/project-b
   
   # List all projects
   svcs list
   ```

2. **Show project statistics**
   ```bash
   svcs stats --project /path/to/project-a
   svcs recent --project /path/to/project-a --days 7
   ```

3. **Demonstrate soft delete (recoverable)**
   ```bash
   # Soft delete - preserves data
   svcs remove /path/to/project-b
   
   # Show it's marked inactive
   svcs list
   
   # Reactivate project
   svcs init --name "Project B Reactivated" /path/to/project-b
   ```

4. **Show cleanup utility**
   ```bash
   # Preview cleanup
   python3 svcs_cleanup.py --temp-dirs --dry-run
   
   # Show different filtering options
   python3 svcs_cleanup.py --inactive --dry-run
   python3 svcs_cleanup.py --pattern "*test*" --dry-run
   ```

5. **Demonstrate hard delete (permanent)**
   ```bash
   # Hard delete with confirmation
   python3 svcs_cleanup.py --pattern "demo_*"
   ```

#### Screenshot Points:
- Project listing before/after operations
- Soft delete vs hard delete differences
- Cleanup utility filtering options
- Safety features (dry-run, confirmations)

---

## 🌍 Multi-Language Support Demos

### Demo 7: Multi-Language Project Analysis
**Duration**: 5-6 minutes
**Objective**: Show SVCS analyzing Python, PHP, and JavaScript in one project

#### Recording Script:
1. **Create multi-language files**
   ```python
   # auth.py
   class AuthService:
       def authenticate(self, username, password):
           return self._verify_credentials(username, password)
   ```
   
   ```php
   <?php
   // auth.php
   class AuthService {
       public function authenticate($username, $password) {
           return $this->verifyCredentials($username, $password);
       }
   }
   ?>
   ```
   
   ```javascript
   // auth.js
   class AuthService {
       authenticate(username, password) {
           return this.verifyCredentials(username, password);
       }
   }
   ```

2. **Commit and show analysis**
   ```bash
   git add auth.py auth.php auth.js
   git commit -m "Add authentication service in multiple languages"
   ```

3. **Show language-specific analysis**
   ```bash
   svcs search --project . --location "auth.py" --limit 5
   svcs search --project . --location "auth.php" --limit 5
   svcs search --project . --location "auth.js" --limit 5
   ```

4. **Modify methods in all languages and show evolution**
   - Add parameters to methods
   - Change visibility (PHP)
   - Add async/await (JavaScript)

#### Expected Highlights:
- Parser technology differences (AST vs Tree-sitter vs esprima)
- Language-specific semantic events
- Consistent analysis across languages

---

## 🧠 AI-Powered Features

### Demo 8: Conversational Interface
**Duration**: 5-6 minutes
**Objective**: Show natural language queries about code evolution

#### Recording Script:
1. **Start conversational interface**
   ```bash
   export GOOGLE_API_KEY="your_key_here"
   python3 svcs_discuss.py
   ```

2. **Demonstrate various query types**
   ```
   "What performance optimizations were made last week?"
   "Show me all dependency changes by Alice"
   "How has the DataProcessor class evolved?"
   "Which commits had the most significant semantic changes?"
   "What functions handle error recovery?"
   "Show me examples of code simplification"
   ```

3. **Show git integration queries**
   ```
   "What files were changed in commit abc123?"
   "Show me the actual diff for that commit"
   "What were the exact code changes in the authentication refactoring?"
   "Show me only the changes to auth.py in commit abc123"
   ```

4. **Demonstrate context awareness**
   - Ask follow-up questions
   - Reference previous queries
   - Show detailed semantic explanations

#### Expected Highlights:
- Natural language processing
- Rich, contextual responses
- Integration with git data
- AI explanations of semantic patterns

---

### Demo 9: Layer 5b AI Analysis in Detail
**Duration**: 3-4 minutes
**Objective**: Show AI semantic pattern detection

#### Recording Script:
1. **Create complex refactoring scenario**
   ```python
   # Before: procedural code
   def process_data(data):
       results = []
       for item in data:
           if item['valid']:
               processed = item['value'] * 2
               results.append(processed)
       return results
   
   # After: functional style
   def process_data(data):
       return [
           item['value'] * 2 
           for item in data 
           if item['valid']
       ]
   ```

2. **Commit and show AI analysis**
   ```bash
   git commit -am "Refactor to functional style"
   svcs search --project . --min-confidence 0.7 --limit 5
   ```

3. **Show pattern recognition**
   - Abstract pattern detection
   - Confidence scores
   - Detailed explanations

#### Expected AI Patterns:
- `abstract_functional_programming_adoption`
- `abstract_code_simplification`
- `abstract_readability_improvement`

---

## 🎯 Real-World Use Cases

### Demo 10: Code Review Enhancement
**Duration**: 5-6 minutes
**Objective**: Show SVCS enhancing code review process

#### Recording Script:
1. **Simulate PR scenario**
   - Create branch with multiple commits
   - Include various types of changes
   
2. **Pre-review analysis**
   ```bash
   python3 svcs_ci.py --pr-analysis --target=main
   ```

3. **Show semantic impact assessment**
   ```bash
   svcs search --project . --since "1 week ago" --min-confidence 0.7 --limit 10
   ```

4. **Demonstrate pattern detection**
   - Find architectural changes
   - Identify complexity increases
   - Show quality improvements

5. **Use conversational interface for review**
   ```
   "What are the main architectural changes in this PR?"
   "Are there any concerning complexity increases?"
   "What quality improvements were made?"
   ```

---

### Demo 11: Technical Debt Management
**Duration**: 4-5 minutes
**Objective**: Show SVCS tracking code quality over time

#### Recording Script:
1. **Show quality analytics**
   ```bash
   svcs stats --project .
   svcs patterns maintainability --project . --since "6 months ago"
   ```

2. **Identify debt patterns**
   ```bash
   svcs search --project . --event-types "complexity_increase" --min-confidence 0.8 --limit 10
   svcs patterns architecture --project . --since "3 months ago"
   ```

3. **Track improvements**
   ```bash
   svcs search --project . --event-types "abstract_code_simplification" --limit 10
   svcs patterns performance --project . --since "1 month ago"
   ```

4. **Use dashboard for trend visualization**
   - Open web dashboard
   - Show quality metrics over time
   - Highlight improvement/degradation patterns

---

## 💻 CLI Interface Demonstrations

### Demo 12: Complete CLI Feature Tour
**Duration**: 6-7 minutes
**Objective**: Comprehensive CLI interface demonstration

#### Recording Script:
1. **Basic query commands**
   ```bash
   # View all semantic history
   svcs search --limit 20
   
   # Filter by author
   svcs search --author "John Doe" --limit 10
   
   # Filter by time period
   svcs search --since "1 week ago" --limit 10
   ```

2. **Advanced filtering**
   ```bash
   # Specific event types
   svcs search --event-types "node_signature_changed" --limit 10
   
   # High confidence changes
   svcs search --min-confidence 0.8 --limit 10
   
   # Node-specific tracking
   svcs evolution "func:authenticate"
   ```

3. **Project management**
   ```bash
   # List projects
   svcs list
   
   # Project statistics
   svcs stats
   
   # Recent activity
   svcs recent --days 7
   ```

4. **Analytics commands**
   ```bash
   svcs stats
   svcs patterns performance
   svcs recent --days 30
   ```

#### Screenshot Points:
- Rich terminal formatting
- Filtering capabilities
- Color-coded output
- Progress indicators

---

## ✅ Production Quality Checks

### Final Demo: Integration Verification
**Duration**: 3-4 minutes
**Objective**: Verify all components work together

#### Recording Script:
1. **Verify git hooks**
   ```bash
   ls -la .git/hooks/
   cat .git/hooks/post-commit
   ```

2. **Test multi-layer analysis**
   - Make commit with complex changes
   - Verify all layers execute
   - Check database entries

3. **Verify MCP server**
   ```bash
   svcs --help
   ```

4. **Check web dashboard**
   ```bash
   curl http://127.0.0.1:8080/health
   curl http://127.0.0.1:8080/api/projects
   ```

5. **Verify error handling**
   - Test with syntax errors
   - Test with missing dependencies
   - Show graceful degradation

6. **Demo database cleanup (prune)**
   ```bash
   # Show current semantic events
   svcs search --project . --limit 5
   
   # Create a commit then reset it (simulate orphaned data)
   echo "# temp" > temp.py
   git add temp.py
   git commit -m "Temp commit"
   git reset --hard HEAD~1
   
   # Show orphaned data cleanup (currently only available in legacy script)
   # TODO: Should be: svcs prune --project .
   python3 svcs.py prune
   ```
   - **Screenshot point**: Before/after prune showing cleanup
   - **Note**: This demonstrates a feature that should be added to the main `svcs` command

---

## 📝 Post-Production Checklist

### For Each Demo:
- [ ] Clean, readable terminal output
- [ ] Clear narration/captions
- [ ] Highlight key features visually
- [ ] Show expected vs actual results
- [ ] Include error scenarios where relevant
- [ ] Verify audio quality
- [ ] Check screen resolution (1080p minimum)
- [ ] Add timestamps for key moments

### For Screenshots:
- [ ] High resolution (2x scaling for retina)
- [ ] Clean terminal/interface
- [ ] Readable font sizes
- [ ] Highlight important elements
- [ ] Include relevant context
- [ ] Multiple angles/views where helpful

### Content Organization:
- [ ] Create animated GIFs for key workflows
- [ ] Short video clips (30-60 seconds) for features
- [ ] Longer demos (3-7 minutes) for complete workflows
- [ ] Static screenshots for documentation
- [ ] Thumbnails for video content

---

## 🎬 Technical Recording Settings

### Recommended Setup:
- **Resolution**: 1920x1080 minimum, 2560x1440 preferred
- **Frame Rate**: 30 FPS for demos, 60 FPS for smooth animations
- **Audio**: Clear narration with noise reduction
- **Terminal**: Dark theme, 16-18pt font
- **Browser**: Clean interface, no personal bookmarks/data
- **VS Code**: Clean workspace, relevant extensions only

### File Organization:
```
screenshots/
├── setup/
├── core-features/
├── multi-language/
├── mcp-integration/
├── web-dashboard/
├── ai-features/
├── git-integration/
├── use-cases/
└── cli-interface/

videos/
├── quick-demos/     # 30-60 seconds
├── feature-tours/   # 3-7 minutes
├── complete-flows/  # 7+ minutes
└── gifs/           # Animated highlights
```

This plan provides comprehensive, step-by-step guidance for creating professional screenshots and demos of all SVCS features. Each section can be followed independently during screen recording sessions, with Copilot providing real-time assistance and verification.

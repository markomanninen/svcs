# SVCS Screenshots & Demos Production Plan
**Updated for Current SVCS Architecture - January 2025**

This document provides detailed task-level instructions for creating screenshots and demo videos for the SVCS project. Each section is designed to be followed step-by-step during screen recording sessions.

## 📋 Table of Contents

1. [Setup & Preparation](#setup--preparation)
2. [Core Feature Demonstrations](#core-feature-demonstrations)
3. [MCP Server Integration](#mcp-server-integration)
4. [Web Dashboard & Analytics](#web-dashboard--analytics)
5. [Enhanced Git Integration](#enhanced-git-integration)
6. [Multi-Language Support Demos](#multi-language-support-demos)
7. [AI-Powered Features](#ai-powered-features)
8. [Project Management & Tours](#project-management--tours)
9. [Real-World Use Cases](#real-world-use-cases)
10. [Production Quality Checks](#production-quality-checks)

---

## 🔧 Setup & Preparation

### Pre-Recording Checklist
- [ ] Clean terminal with readable font size (16-18pt, recommend JetBrains Mono or Fira Code)
- [ ] VS Code/Cursor with SVCS MCP server configured
- [ ] Fresh clone of SVCS repository from GitHub
- [ ] Virtual environment created and activated
- [ ] SVCS installed globally with `pip install -e .`
- [ ] Google API key set for Layer 5b features (optional but recommended)
- [ ] Clean browser for web dashboard demos (Chrome/Safari recommended)
- [ ] Screen recording software configured (1080p minimum, 4K preferred)
- [ ] Demo project directories prepared

### Environment Setup Commands (Updated 2025)
```bash
# Clone the SVCS repository
git clone https://github.com/markomanninen/svcs.git
cd svcs

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install SVCS globally (creates 'svcs' command)
pip install -e .

# Install enhanced language parsing (recommended)
pip install tree-sitter tree-sitter-php esprima

# Install enhanced language parsing (recommended)
pip install tree-sitter tree-sitter-php esprima

# Set API key (optional, for Layer 5b AI features)
export GOOGLE_API_KEY="your_key_here"

# Verify installation
svcs --help
svcs --version

# Verify web dashboard capability
svcs web start --port 8080 &
curl http://127.0.0.1:8080/health
svcs web stop
```

### ⚠️ Important Updates from Previous Documentation

**What Changed:**
- ✅ **Single Installation**: Just `pip install -e .` provides complete functionality
- ✅ **Unified CLI**: All commands now use `svcs` (no more separate `svcs.py`)
- ✅ **Centralized Architecture**: No file copying, git hooks call centralized installation
- ✅ **Enhanced Project Management**: `svcs init-project` provides interactive tours
- ✅ **Improved Web Dashboard**: Standalone server with advanced features
- ✅ **Enhanced Git Integration**: `svcs pull`, `svcs push`, `svcs merge` with semantic sync

**Removed/Deprecated:**
- ❌ `svcs.py` separate CLI (now unified under `svcs`)
- ❌ `./start_dashboard.sh` script (now `svcs web start`)
- ❌ Manual file copying during setup
- ❌ Separate MCP installation (integrated into main package)

---

## 🚀 Core Feature Demonstrations

### Demo 1: Modern Project Setup and First Analysis
**Duration**: 4-5 minutes
**Objective**: Show streamlined installation and interactive project creation

#### Recording Script:
1. **Show SVCS installation verification**
   ```bash
   svcs --help
   svcs --version
   ```
   - **Narration**: "SVCS provides a unified CLI with all features integrated"

2. **Create new project with interactive tour**
   ```bash
   svcs init-project DemoApp
   ```
   - **Narration**: "SVCS includes an interactive tour for new users"
   - Follow the interactive prompts
   - Show the guided creation of sample code
   - Demonstrate the commit and analysis process

3. **Explore initial analysis results**
   ```bash
   svcs status
   svcs events --limit 10
   ```
   - **Screenshot point**: Rich terminal output with semantic events

4. **Show SVCS configuration**
   ```bash
   svcs config list
   cat .svcs/config.json
   ```

#### Expected Outputs to Highlight:
- Interactive tour interface with rich formatting
- Automatic git repository initialization
- Git hook installation messages
- Semantic events detected (node_added, class_added, etc.)
- SVCS configuration and database setup

---

### Demo 2: Enhanced Git Integration Workflow
**Duration**: 5-6 minutes
**Objective**: Demonstrate git-integrated semantic workflow

#### Recording Script:
1. **Initialize existing repository**
   ```bash
   cd existing-project
   svcs init
   ```
   - **Narration**: "SVCS integrates seamlessly with existing git repositories"

2. **Make code changes and show enhanced commits**
   ```python
   # Modify existing function
   def calculate_score(items, weights=None):
       if not items:
           raise ValueError("Items cannot be empty")
       
       if weights:
           return sum(item * weight for item, weight in zip(items, weights))
       return sum(items)
   ```

3. **Demonstrate enhanced git operations**
   ```bash
   git add calculate.py
   git commit -m "Add error handling and weighted calculation"
   
   # Show semantic sync
   svcs sync
   
   # Enhanced git operations
   svcs pull  # Enhanced pull with semantic notes
   svcs push  # Enhanced push with semantic notes
   ```

4. **Show semantic evolution tracking**
   ```bash
   svcs evolution "func:calculate_score"
   svcs search --pattern-type error_handling
   ```

#### Screenshot Points:
- Git hook execution during commit
- Enhanced git operations output
- Semantic evolution timeline
- Pattern recognition results

---
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

### Demo 3: VS Code/Cursor MCP Integration  
**Duration**: 6-7 minutes
**Objective**: Show SVCS working with AI assistants in modern IDEs

#### Recording Script:
1. **Start SVCS MCP server**
   ```bash
   svcs mcp start --background
   svcs mcp status
   ```

2. **Show MCP configuration**
   - Display VS Code/Cursor settings for SVCS MCP server
   - Show connection status in IDE

3. **Demonstrate semantic queries in IDE chat**
   ```
   @copilot Show me all registered SVCS projects
   @copilot What semantic patterns were detected in the last week?
   @copilot Get a summary of commit abc123 including all semantic events
   @copilot How has the authenticate function evolved over time?
   @copilot Find all performance optimizations in my code
   @copilot Show recent architecture improvements with high confidence
   ```

4. **Show project management through AI**
   ```
   @copilot List all projects in SVCS registry
   @copilot Get project statistics for current repository
   @copilot Search for error handling patterns in this project
   ```

5. **Demonstrate git integration queries**
   ```
   @copilot Get changed files for commit abc123
   @copilot Show me the complete diff for that commit
   @copilot What were the semantic events in the latest merge?
   ```

#### Screenshot Points:
- MCP server status and logs
- IDE chat interface with SVCS responses
- Rich semantic data visualization in AI responses
- Project management through natural language

---

## 📊 Web Dashboard & Analytics

### Demo 4: Interactive Web Dashboard
**Duration**: 8-10 minutes
**Objective**: Show the comprehensive web interface for SVCS data exploration

#### Recording Script:
1. **Launch modern web dashboard**
   ```bash
   svcs web start --port 8080
   ```
   - Open browser to http://127.0.0.1:8080
   - **Narration**: "The web dashboard provides a rich interface for semantic data exploration"

2. **Show main dashboard features**
   - Project selection and multi-project support
   - Real-time analytics dashboard
   - Interactive timeline visualizations
   - Event type and confidence filtering

3. **Demonstrate advanced search capabilities**
   - Pattern search with confidence thresholds
   - Author and time-based filtering
   - Location-based filtering (files/directories)
   - Quick action buttons for common patterns

4. **Show git integration features**
   - Click on commit hashes to view details
   - Interactive file change viewer with syntax highlighting
   - Side-by-side diff viewer
   - Commit summary with semantic context

5. **Demonstrate analytics and evolution tracking**
   - Quality trends over time
   - Developer activity patterns
   - Function/class evolution timelines
   - Network diagrams of code dependencies

6. **Show project management interface**
   - Multi-project dashboard
   - Project health monitoring
   - Database statistics and maintenance tools

#### Screenshot Points:
- Main dashboard overview with analytics
- Advanced search interface with filters
- Git integration with syntax-highlighted diffs
- Evolution tracking visualizations
- Project management interface

---

### Demo 5: Static Dashboard Generation
**Duration**: 3-4 minutes
**Objective**: Show standalone dashboard creation for sharing/reports

#### Recording Script:
1. **Generate static dashboard**
   ```bash
   svcs dashboard --output comprehensive_report.html --theme light
   ```

2. **Open and demonstrate static features**
   - Show browser opening the standalone HTML file
   - Navigate through interactive elements (no server needed)
   - Demonstrate offline functionality

3. **Show customization options**
   ```bash
   svcs dashboard --output dark_theme_report.html --theme dark
   ```

#### Expected Features:
- Fully self-contained HTML with embedded CSS/JS
- Interactive charts and graphs
- Timeline visualizations
- Network diagrams

---

## 🔄 Enhanced Git Integration

### Demo 6: Advanced Git Workflow with Semantic Sync
**Duration**: 6-7 minutes  
**Objective**: Demonstrate enhanced git operations with automatic semantic synchronization

#### Recording Script:
1. **Setup collaborative scenario**
   ```bash
   # Setup remote repository simulation
   git remote add origin <remote-url>
   svcs config set auto-sync true
   ```

2. **Demonstrate enhanced git operations**
   ```bash
   # Enhanced pull with semantic notes sync
   svcs pull
   
   # Make changes and enhanced push
   echo "# New feature" >> feature.py
   git add feature.py
   git commit -m "Add new feature module"
   svcs push origin main
   ```

3. **Show advanced merge operations**
   ```bash
   # Create and switch to feature branch
   git checkout -b feature-auth
   
   # Make changes and commit
   echo "class Auth: pass" >> auth.py
   git add auth.py
   git commit -m "Add authentication module"
   
   # Enhanced merge with semantic event transfer
   git checkout main
   svcs merge feature-auth
   ```

4. **Demonstrate semantic sync utilities**
   ```bash
   svcs sync-all  # Complete synchronization
   svcs auto-fix  # Auto-detect and fix issues
   svcs merge-resolve  # Resolve post-merge semantic issues
   ```

5. **Show configuration management**
   ```bash
   svcs config list
   svcs config set auto-sync false
   svcs config get auto-sync
   ```

#### Screenshot Points:
- Enhanced git operation outputs
- Semantic event transfer during merge
- Configuration management interface
- Sync status and resolution tools

---

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
   python3 svcs_repo_ci.py --pr-analysis --target=main
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

This updated plan provides comprehensive, step-by-step guidance for creating professional screenshots and demos of all current SVCS features (January 2025). Each section reflects the modern unified CLI architecture, centralized installation, enhanced git integration, and production-ready functionality.

**Key Updates in This Revision:**
- ✅ Updated for unified `svcs` CLI command
- ✅ Reflects centralized installation architecture  
- ✅ Includes enhanced git integration features
- ✅ Documents modern web dashboard capabilities
- ✅ Shows current MCP server integration
- ✅ Demonstrates interactive project tours
- ✅ Includes AI-powered features and conversational interface
- ✅ Updated command syntax and examples
- ✅ Realistic timing estimates for current feature set

Each demo section can be followed independently during screen recording sessions to create high-quality promotional and educational content that accurately represents SVCS's production capabilities.

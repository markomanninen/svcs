# 📹 SVCS Core Demo Sessions - Streamlined Plan

This is a condensed, action-focused plan for recording the essential SVCS demonstrations. Each session is designed to be recorded independently and showcases core functionality without overlap.

## 🎯 Quick Reference

| Demo | Duration | Focus | Key Commands |
|------|----------|-------|--------------|
| **Setup & First Analysis** | 3-4 min | Project initialization | `svcs init`, first commit |
| **5-Layer Analysis** | 4-5 min | Semantic layer progression | Multiple commits showing layer evolution |
| **MCP Integration** | 4-5 min | VS Code AI assistant | `@copilot` commands |
| **Web Dashboard** | 6-7 min | Interactive analytics | `./start_dashboard.sh` |
| **Project Management** | 5-6 min | Lifecycle & cleanup | `svcs list`, `svcs_cleanup.py` |
| **Multi-Language** | 5-6 min | Python, PHP, JavaScript | Cross-language analysis |
| **AI Features** | 5-6 min | Conversational interface | `svcs_discuss.py` |
| **CLI Tour** | 6-7 min | Complete CLI features | All `svcs` commands |

---

## 🚀 Session 1: Setup & First Analysis
**Duration**: 3-4 minutes | **Objective**: Complete project setup and first semantic analysis

### Recording Flow:
```bash
# 1. Create demo project
mkdir demo_project && cd demo_project
git init

# 2. Register with SVCS
svcs init --name "Demo Project" .

# 3. Create initial code
cat > test.py << EOF
def greet(name):
    return f"Hello, {name}!"

class Calculator:
    def add(self, a, b):
        return a + b
EOF

# 4. First commit & analysis
git add test.py
git commit -m "Initial implementation"

# 5. View semantic history
svcs search --project . --limit 10
```

### 📸 Key Screenshots:
- Git hook execution in terminal
- Semantic events output (node_added, class_added)
- Rich terminal formatting

---

## 🔍 Session 2: 5-Layer Analysis Progression
**Duration**: 4-5 minutes | **Objective**: Show all semantic analysis layers

### Recording Flow:
```bash
# Layer 1-2: Structural change
cat > test.py << EOF
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

class Calculator:
    def add(self, a, b):
        return a + b
EOF
git commit -am "Add greeting parameter"
svcs search --project . --limit 3

# Layer 3-4: Behavioral change
cat > test.py << EOF
def greet(name, greeting="Hello"):
    if not name:
        raise ValueError("Name cannot be empty")
    return f"{greeting}, {name}!"

class Calculator:
    def add(self, a, b):
        return a + b
EOF
git commit -am "Add input validation"
svcs search --project . --limit 3

# Layer 5a: Pattern recognition
cat > test.py << EOF
def validate_input(name):
    if not name:
        raise ValueError("Name cannot be empty")
    return name

def format_greeting(name, greeting="Hello"):
    return f"{greeting}, {name}!"

def greet(name, greeting="Hello"):
    validated_name = validate_input(name)
    return format_greeting(validated_name, greeting)

class Calculator:
    def add(self, a, b):
        return a + b
EOF
git commit -am "Refactor to functional composition"
svcs search --project . --limit 3

# Layer 5b: AI analysis (if API key available)
svcs search --project . --min-confidence 0.7 --limit 5
```

### 📸 Key Screenshots:
- Layer progression in output
- Different semantic event types
- Confidence scores for AI analysis

---

## 🤖 Session 3: MCP Integration in VS Code
**Duration**: 4-5 minutes | **Objective**: AI assistant integration

### Recording Flow:
1. **Show MCP configuration**
   - Open VS Code settings.json
   - Display SVCS MCP server config

2. **Demonstrate core MCP commands**
   ```
   @copilot list svcs projects
   @copilot show recent activity for this project
   @copilot analyze the current commit
   @copilot search for error handling patterns
   @copilot get changed files for commit abc123
   ```

### 📸 Key Screenshots:
- MCP configuration in VS Code
- Chat responses with semantic data
- Git integration features

---

## 📊 Session 4: Web Dashboard Tour
**Duration**: 6-7 minutes | **Objective**: Full web interface demonstration

### Recording Flow:
```bash
# 1. Launch dashboard
./start_dashboard.sh
# Open browser to http://127.0.0.1:8080
```

### Dashboard Navigation:
1. **Main features overview**
   - Project dropdown
   - Timeline visualization
   - Filter controls

2. **Semantic search demo**
   - Search for "performance"
   - Apply confidence filters
   - Show event details

3. **Git integration**
   - Click commit hash
   - View changed files
   - Show diff viewer

4. **Analytics section**
   - Quality trends
   - Developer activity
   - Event distribution

### 📸 Key Screenshots:
- Dashboard overview
- Search results interface
- Analytics visualizations
- Git integration features

---

## 🗂️ Session 5: Project Management & Cleanup
**Duration**: 5-6 minutes | **Objective**: Complete lifecycle management

### Recording Flow:
```bash
# 1. Register multiple projects
svcs init --name "Project A" /path/to/project-a
svcs init --name "Project B" /path/to/project-b
svcs list

# 2. Project statistics
svcs stats --project /path/to/project-a
svcs recent --project /path/to/project-a --days 7

# 3. Soft delete (recoverable)
svcs remove /path/to/project-b
svcs list
svcs init --name "Project B Reactivated" /path/to/project-b

# 4. Cleanup utility demo
python3 svcs_cleanup.py --temp-dirs --dry-run
python3 svcs_cleanup.py --inactive --dry-run
python3 svcs_cleanup.py --pattern "*test*" --dry-run

# 5. Hard delete (permanent)
python3 svcs_cleanup.py --pattern "demo_*"
```

### 📸 Key Screenshots:
- Project listings before/after operations
- Cleanup utility options
- Safety confirmations

---

## 🌍 Session 6: Multi-Language Support
**Duration**: 5-6 minutes | **Objective**: Cross-language analysis

### Recording Flow:
```bash
# 1. Create multi-language files
cat > auth.py << EOF
class AuthService:
    def authenticate(self, username, password):
        return self._verify_credentials(username, password)
EOF

cat > auth.php << EOF
<?php
class AuthService {
    public function authenticate(\$username, \$password) {
        return \$this->verifyCredentials(\$username, \$password);
    }
}
?>
EOF

cat > auth.js << EOF
class AuthService {
    authenticate(username, password) {
        return this.verifyCredentials(username, password);
    }
}
EOF

# 2. Commit and analyze
git add auth.py auth.php auth.js
git commit -m "Add authentication service in multiple languages"

# 3. Language-specific queries
svcs search --project . --location "auth.py" --limit 5
svcs search --project . --location "auth.php" --limit 5
svcs search --project . --location "auth.js" --limit 5
```

### 📸 Key Screenshots:
- Multi-language file analysis
- Parser technology differences
- Consistent semantic events

---

## 🧠 Session 7: AI-Powered Features
**Duration**: 5-6 minutes | **Objective**: Conversational interface

### Recording Flow:
```bash
# 1. Start conversational interface
export GOOGLE_API_KEY="your_key_here"
python3 svcs_discuss.py
```

### Query Examples:
```
"What performance optimizations were made last week?"
"Show me all dependency changes by Alice"
"How has the DataProcessor class evolved?"
"What files were changed in commit abc123?"
"Show me examples of code simplification"
```

### 📸 Key Screenshots:
- Natural language queries
- Rich AI responses
- Context-aware conversations

---

## 💻 Session 8: Complete CLI Tour
**Duration**: 6-7 minutes | **Objective**: All CLI capabilities

### Recording Flow:
```bash
# 1. Basic queries
svcs search --limit 20
svcs search --author "John Doe" --limit 10
svcs search --since "1 week ago" --limit 10

# 2. Advanced filtering
svcs search --event-types "node_signature_changed" --limit 10
svcs search --min-confidence 0.8 --limit 10
svcs evolution "func:authenticate"

# 3. Project management
svcs list
svcs stats
svcs recent --days 7

# 4. Pattern analysis
svcs patterns performance
svcs patterns architecture
```

### 📸 Key Screenshots:
- Rich terminal formatting
- Color-coded output
- Filter capabilities

---

## ⚡ Quick Setup Commands

### Pre-Recording Environment:
```bash
# Clone and setup
git clone https://github.com/markomanninen/svcs.git
cd svcs
python3 -m venv venv
source venv/bin/activate

# Install dependencies
cd svcs_mcp && pip install -e . && cd ..
pip install -r requirements.txt
pip install -r requirements_web.txt

# Verify installation
svcs --help
./start_dashboard.sh &
curl http://127.0.0.1:8080/health
```

### Recording Settings:
- **Resolution**: 1920x1080 minimum
- **Font**: 16-18pt terminal font
- **Theme**: Dark terminal theme
- **Frame Rate**: 30 FPS
- **Audio**: Clear narration

---

## 📁 Output Organization

```
recordings/
├── 01-setup-first-analysis.mp4
├── 02-five-layer-analysis.mp4
├── 03-mcp-integration.mp4
├── 04-web-dashboard.mp4
├── 05-project-management.mp4
├── 06-multi-language.mp4
├── 07-ai-features.mp4
└── 08-cli-tour.mp4

screenshots/
├── setup/
├── analysis/
├── mcp/
├── dashboard/
├── management/
├── multi-lang/
├── ai/
└── cli/
```

This streamlined plan provides focused, actionable sessions for creating comprehensive SVCS demonstrations without redundancy or overlap.

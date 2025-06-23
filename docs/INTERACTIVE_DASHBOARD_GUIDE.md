# SVCS Interactive Web Dashboard

A comprehensive web interface for exploring and analyzing your codebase's semantic evolution using SVCS (Semantic Version Control System).

## 🚀 Quick Start

### 1. Start the Dashboard

```bash
# Option 1: Using the setup script (recommended)
./start_dashboard.sh

# Option 2: Manual startup
source .svcs/venv/bin/activate
pip install Flask Flask-CORS
python3 svcs_web_server.py
```

### 2. Access the Dashboard

Open your web browser and navigate to:
```
http://127.0.0.1:8080
```

## 🎯 Features

### 🔍 **Semantic Search**
- **Advanced Filtering**: Search by author, date range, confidence level, and analysis layer
- **Quick Actions**: One-click searches for performance, error handling, and architecture changes
- **Smart Results**: View semantic events with context and confidence scores

**Example Queries**:
- Find all performance optimizations by John in the last 7 days
- Show architecture changes with high confidence (>0.8)
- List recent error handling improvements

### 📝 **Git Integration**
- **Changed Files**: See exactly which files were modified in any commit
- **Raw Diffs**: View actual git diffs with syntax highlighting
- **Commit Summaries**: Get comprehensive commit info including semantic events
- **Recent Activity**: Browse recent commits with semantic context

**Example Usage**:
- Enter commit hash: `abc123def`
- View changed files, diffs, or complete summaries
- Filter diffs to specific files for focused analysis

### 📈 **Code Evolution Tracking**
- **Node Evolution**: Track how specific functions/classes evolved over time
- **Filtered History**: Search evolution by date, confidence, or event types
- **Pattern Recognition**: Identify improvement trends and architectural decisions

**Example Queries**:
- Track evolution of `func:process_data` since last month
- Show only high-confidence changes for `class:DataProcessor`
- Find all refactoring events for authentication functions

### 🎯 **Pattern Analysis**
- **AI-Detected Patterns**: Search for specific semantic patterns
- **Pattern Types**: Performance, architecture, error handling, design patterns, security
- **Confidence Filtering**: Focus on high-confidence AI detections

**Available Patterns**:
- Performance Optimization
- Architecture Changes  
- Error Handling Improvements
- Design Pattern Applications
- Refactoring Activities
- Security Enhancements

### 📋 **System Logs**
- **LLM Inference Logs**: See what AI analysis was performed
- **Error Logs**: Debug SVCS operation issues
- **Real-time Viewing**: Monitor system activity as it happens

### 🗂️ **Project Management**
- **Multi-Project Support**: Manage multiple SVCS-tracked projects
- **Project Statistics**: View comprehensive analytics per project
- **Registration**: Add new projects to SVCS tracking

### 📊 **Analytics & Reporting**
- **Quality Analysis**: Track code quality trends over time
- **Export Data**: Download SVCS data for external analysis
- **Report Generation**: Create comprehensive analytics reports

### 🔧 **Database Maintenance**
- **Orphaned Data Cleanup**: Remove semantic data for commits no longer in git history
- **Project-Specific Pruning**: Clean up data for specific projects
- **Global Cleanup**: Prune orphaned data across all projects
- **Safety Features**: Clear warnings and informational help text

**Why Prune?** Orphaned data occurs when:
- Commits are rebased, squashed, or force-pushed
- Branches are deleted
- Git history is rewritten (filter-branch, etc.)

**Warning**: Pruning permanently removes orphaned semantic data. Ensure you have backups before running.

## 🔧 API Endpoints

The dashboard provides a REST API for programmatic access:

### Search & Analysis
- `POST /api/search_events` - Advanced semantic event search
- `POST /api/search_patterns` - Search for AI-detected patterns
- `POST /api/get_recent_activity` - Get recent semantic activity

### Git Integration
- `POST /api/get_commit_changed_files` - List files changed in commit
- `POST /api/get_commit_diff` - Get git diff for commit
- `POST /api/get_commit_summary` - Get comprehensive commit summary

### Evolution Tracking
- `POST /api/get_node_evolution` - Track specific function/class evolution
- `POST /api/get_filtered_evolution` - Filtered evolution history

### Project Management
- `POST /api/list_projects` - List all SVCS projects
- `POST /api/register_project` - Register new project
- `POST /api/get_project_statistics` - Get project stats

### System
- `POST /api/get_logs` - View system logs
- `POST /api/prune_database` - Clean orphaned data from database
- `GET /health` - Health check

## 📱 Usage Examples

### Investigating a Bug
1. **Git Integration** → Enter the commit hash where the bug was introduced
2. **View Changed Files** → See what files were modified
3. **Show Diff** → Examine the actual code changes
4. **Semantic Search** → Look for related error handling or complexity changes

### Code Review
1. **Recent Activity** → See what's been changing in the codebase
2. **Pattern Analysis** → Check for design pattern applications
3. **Evolution Tracking** → Understand how key functions have evolved
4. **Quality Analysis** → Review overall code quality trends

### Architectural Analysis
1. **Pattern Analysis** → Search for "Architecture Changes"
2. **Semantic Search** → Filter by high confidence (>0.8)
3. **Evolution Tracking** → Track key classes over time
4. **Analytics** → Generate comprehensive reports

### Performance Investigation
1. **Quick Search** → Click "Performance" button
2. **Filter by Date** → Focus on recent optimizations
3. **Git Integration** → Examine specific performance commits
4. **Evolution** → Track performance-critical functions

### Database Maintenance
1. **Database Maintenance** → Navigate to maintenance section
2. **Project Path** → Enter specific project path (optional)
3. **Learn About Pruning** → Click "What is Pruning?" for help
4. **Prune Data** → Click "Prune Orphaned Data" to clean up
5. **Review Results** → See how many orphaned commits/events were removed

**Maintenance Scenarios**:
- After rebasing or squashing commits
- Following branch deletions or history rewrites
- Regular cleanup to optimize database size
- Before important backups or migrations

## 🎨 User Interface

### Modern Design
- **Gradient Backgrounds**: Beautiful visual design
- **Responsive Layout**: Works on desktop and mobile
- **Intuitive Navigation**: Clear section-based organization
- **Real-time Feedback**: Loading states and error handling

### Key UI Elements
- **Sidebar Navigation**: Easy switching between tools
- **Quick Actions**: One-click common operations
- **Smart Forms**: Auto-completion and validation
- **Rich Results**: Syntax-highlighted diffs and formatted JSON

## 🔒 Security & Performance

### Security
- **Local Operation**: All data stays on your machine
- **No External Calls**: SVCS analysis runs locally
- **CORS Protection**: Proper cross-origin request handling

### Performance
- **Efficient API**: Optimized database queries
- **Async Operations**: Non-blocking web interface
- **Smart Caching**: Reduced redundant operations
- **Pagination**: Handle large result sets gracefully

## 🛠️ Configuration

### Server Configuration
```bash
# Custom host and port
python3 svcs_web_server.py --host 0.0.0.0 --port 9000

# Debug mode for development
python3 svcs_web_server.py --debug
```

### Environment Variables
```bash
# For LLM features (optional)
export GOOGLE_API_KEY="your_gemini_api_key"

# Custom project path
export SVCS_PROJECT_PATH="/path/to/your/project"
```

## 🐛 Troubleshooting

### Common Issues

**Dashboard won't load**:
- Ensure Flask and Flask-CORS are installed: `pip install Flask Flask-CORS`
- Check that you're in the SVCS root directory
- Verify port 8080 isn't in use by another application

**No data showing**:
- Make sure you're in a git repository with SVCS tracking
- Run `python3 svcs.py log` to verify SVCS has data
- Check that semantic analysis has been performed on commits

**API errors**:
- Verify the `.svcs/api.py` file exists and is accessible
- Check that the SVCS database has been initialized
- Review server logs for specific error messages

**Performance issues**:
- Large repositories may take time to analyze
- Consider filtering results by date or confidence
- Use pagination for large result sets

### Getting Help

1. **Check Logs**: Use the "System Logs" section to see what's happening
2. **Debug Tools**: Use "Project Management" → "Debug Tools" for diagnostics
3. **API Testing**: Test individual API endpoints to isolate issues
4. **Console Logs**: Check browser developer console for JavaScript errors

## 🎯 Best Practices

### Effective Usage
1. **Start Broad**: Begin with recent activity to understand current state
2. **Drill Down**: Use specific searches to investigate interesting patterns
3. **Cross-Reference**: Combine semantic events with git diffs for full context
4. **Track Trends**: Use evolution tracking to understand long-term patterns

### Performance Tips
1. **Limit Results**: Use reasonable limits (20-50 items) for faster loading
2. **Filter Smart**: Use date ranges and confidence filters to reduce noise
3. **Cache Results**: The dashboard remembers your last search parameters
4. **Batch Operations**: Group related queries together

### Data Quality
1. **Regular Analysis**: Ensure SVCS runs on all commits for complete data
2. **Clean Data**: Periodically run `python3 svcs.py prune` to clean up
3. **Verify Results**: Cross-check semantic events with actual code changes
4. **Monitor Quality**: Use quality analysis to track improvement trends

---

## 🌟 **The SVCS Interactive Dashboard provides a powerful, user-friendly way to explore the semantic evolution of your codebase. Happy exploring!** 🚀

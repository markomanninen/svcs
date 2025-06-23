# SVCS Database Maintenance Guide

## 🔧 Overview

SVCS tracks semantic changes by linking them to specific git commits. When git history is modified (rebasing, squashing, force-pushing, etc.), some commits may no longer exist, leaving "orphaned" semantic data in the database.

## 🧹 Pruning Orphaned Data

### What is Orphaned Data?

Orphaned data occurs when:
- **Commits are rebased or squashed** - Original commit hashes no longer exist
- **Branches are deleted** - Commits from deleted branches become unreachable
- **History is rewritten** - Operations like `git filter-branch` or `git rebase -i`
- **Force pushes occur** - Previous commit history is overwritten

### Why Prune?

- **Database optimization** - Remove unnecessary data to improve performance
- **Accuracy** - Ensure semantic history matches actual git history
- **Storage efficiency** - Reduce database size and backup requirements
- **Data integrity** - Maintain clean, consistent semantic records

## 🚀 Pruning Methods

### 1. Interactive Dashboard (Recommended)

**Access**: Navigate to "🔧 Database Maintenance" in the web dashboard

**Features**:
- **Visual interface** - Easy-to-use web form
- **Project selection** - Choose specific project or prune all
- **Detailed results** - See exactly what was cleaned up
- **Help documentation** - Built-in explanations

**Steps**:
1. Open dashboard: `http://127.0.0.1:8080`
2. Click "🔧 Database Maintenance" in sidebar
3. Optional: Enter project path for single-project cleanup
4. Click "🧹 Prune Orphaned Data"
5. Review results showing orphaned commits and deleted events

### 2. Command Line Interface

**Global Prune (All Projects)**:
```bash
python3 svcs.py prune
```

**Single Project Prune**:
```bash
python3 svcs.py prune /path/to/project
```

**Example Output**:
```
🧹 Pruning orphaned data...
✅ Found 3 orphaned commits in project "MyApp"
   - Removed: abc123f (no longer in git history)
   - Removed: def456a (no longer in git history)
   - Removed: ghi789b (no longer in git history)
📊 Deleted 15 semantic events
✨ Database cleanup complete!
```

### 3. MCP Server (AI Integration)

Use in VS Code, Cursor, or other MCP-compatible editors:

```
> prune orphaned data for /path/to/project
> clean up database for all projects
> debug database for this project
```

## ⚠️ Safety Considerations

### Before Pruning

1. **Backup your database**:
   ```bash
   cp ~/.svcs/global.db ~/.svcs/global.db.backup
   ```

2. **Verify git state** - Ensure all important branches are properly merged

3. **Check with team** - Coordinate with team members if working on shared repositories

### Understanding Results

- **No orphaned data found** - Database is clean and synchronized with git
- **X orphaned commits removed** - Commits no longer exist in git history
- **Y semantic events deleted** - Associated semantic analysis data removed

### Recovery

If you accidentally prune needed data:
1. Restore from backup: `cp ~/.svcs/global.db.backup ~/.svcs/global.db`
2. Re-analyze affected commits: `python3 svcs.py analyze --force`

## 📊 Monitoring and Best Practices

### When to Prune

- **After major rebases** - Following interactive rebases or history cleanup
- **Post-merge cleanup** - After merging feature branches with complex history
- **Before backups** - Optimize database size before important backups
- **Regular maintenance** - Monthly or quarterly cleanup depending on activity

### Automation

Add to your maintenance scripts:
```bash
#!/bin/bash
# Monthly SVCS maintenance

# Backup database
cp ~/.svcs/global.db ~/.svcs/backup/global-$(date +%Y%m%d).db

# Prune orphaned data
python3 /path/to/svcs/svcs.py prune

# Generate analytics report
python3 /path/to/svcs/svcs_analytics.py
```

### Monitoring Database Health

Check database statistics:
```bash
# Via CLI
python3 svcs.py stats

# Via MCP
> show stats for all projects
> debug database for this project

# Via Dashboard
Navigate to "📊 Analytics" section
```

## 🔍 Troubleshooting

### Common Issues

**"No projects found"**
- Ensure projects are properly registered: `python3 svcs.py list`
- Re-register if needed: `python3 svcs.py init --name "Project" /path`

**"Git command failed"**
- Verify git repository is accessible
- Check git configuration and permissions
- Ensure project path exists and contains `.git` directory

**"Permission denied"**
- Check file permissions on `~/.svcs/` directory
- Verify database file is writable
- Run with appropriate user permissions

### Debug Information

Get detailed database information:
```bash
# Via CLI
python3 svcs.py debug /path/to/project

# Via Dashboard
Click "❓ What is Pruning?" for help
Navigate to debug sections in Analytics

# Via MCP
> debug database for this project
```

## 📈 Performance Impact

### Database Size Reduction

Typical pruning results:
- **Small projects** (< 100 commits): 0-5% size reduction
- **Medium projects** (100-1000 commits): 5-15% size reduction  
- **Large projects** (> 1000 commits): 10-30% size reduction

### Query Performance

Benefits after pruning:
- **Faster searches** - Fewer records to scan
- **Improved analytics** - More accurate statistics
- **Better caching** - Database fits better in memory
- **Reduced backup time** - Smaller database files

## 🔗 Related Documentation

- [Interactive Dashboard Guide](INTERACTIVE_DASHBOARD_GUIDE.md)
- [MCP Server Interface](../README.md#mcp-server-interface)
- [Project Management CLI](../README.md#project-management-cli)
- [Analytics & Reporting](../README.md#analytics--reporting)

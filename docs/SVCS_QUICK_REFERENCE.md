# SVCS Quick Reference

## Essential Commands

### Setup (One-time per repository)
```bash
svcs init                    # Initialize SVCS in current repository
                            # - Installs git hooks for automatic sync
                            # - Fetches existing semantic data if available
                            # - Sets up centralized configuration
```

### Daily Workflow (Automatic)
```bash
# Normal git workflow - SVCS works automatically
git add .
git commit -m "message"     # → Automatic semantic analysis
git push origin main        # → Semantic notes pushed with code
git pull origin main        # → Semantic notes synced automatically
```

### Viewing Semantic Data
```bash
svcs events                 # Recent semantic events
svcs events --limit 50      # More events
svcs events --author john   # Events by specific author
svcs search "auth"          # Search semantic events
svcs evolution func:login   # Track function evolution
```

### Project Analytics
```bash
svcs status                 # Repository status
svcs statistics             # Semantic statistics
svcs patterns              # Detected patterns
svcs compare main develop   # Compare branches
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No semantic events found | `svcs status` → `svcs init --force` |
| Data out of sync | `svcs sync --force` |
| Missing from new clone | `svcs init` (should be automatic) |
| Performance issues | `svcs config set analysis-depth shallow` |

## Configuration

```bash
svcs config list                           # Show all settings
svcs config set auto-sync true            # Enable auto-sync
svcs config set ignore-patterns "*.min.js" # Ignore files
svcs config set analysis-depth shallow    # Performance tuning
```

## File Locations

- **Semantic database**: `.svcs/semantic.db` (local only)
- **Configuration**: `.svcs/config.json` (local only)  
- **Git hooks**: `.git/hooks/post-commit`, `.git/hooks/post-merge`, etc.
- **Semantic notes**: `refs/notes/svcs-semantic` (shared via git)

## Team Best Practices

1. **Always run `svcs init`** after cloning a repository
2. **Use normal git workflow** - SVCS handles the rest automatically
3. **Check `svcs status`** if something seems wrong
4. **Include SVCS setup** in project documentation
5. **Monitor semantic trends** with `svcs analytics`

---
💡 **Remember**: SVCS is designed to be invisible to your normal git workflow. Just run `svcs init` once and continue using git as usual!

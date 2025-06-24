#!/usr/bin/env python3
"""
SVCS Utility Commands

Commands for help, workflow guidance, and utilities.
"""


def cmd_workflow(args):
    """Show SVCS workflow guide and tips."""
    print("🚀 SVCS Streamlined Workflow Guide")
    print("=" * 60)
    print()
    
    workflow_type = args.type if hasattr(args, 'type') else 'basic'
    
    if workflow_type == 'basic':
        print("📋 Basic Daily Workflow:")
        print("1. Initialize SVCS in any git repository:")
        print("   svcs init")
        print()
        print("2. Work normally - SVCS automatically tracks semantic changes:")
        print("   git add .")
        print("   git commit -m 'Your changes'")
        print()
        print("3. Pull changes with automatic semantic sync:")
        print("   svcs pull")
        print()
        print("4. Create and merge branches with automatic event transfer:")
        print("   git checkout -b feature/new-feature")
        print("   # ... make changes ...")
        print("   git checkout main")
        print("   svcs merge feature/new-feature")
        print()
        print("5. Push with semantic notes:")
        print("   svcs push")
        
    elif workflow_type == 'team':
        print("👥 Team Collaboration Workflow:")
        print("1. Each team member initializes SVCS:")
        print("   git clone <repository>")
        print("   svcs init")
        print()
        print("2. Regular sync to get team's semantic changes:")
        print("   svcs pull  # Gets code + semantic events")
        print()
        print("3. After resolving conflicts or complex merges:")
        print("   svcs sync --detect-merge")
        print()
        print("4. Share your semantic analysis:")
        print("   svcs push  # Pushes code + semantic notes")
        
    elif workflow_type == 'troubleshooting':
        print("🔧 Troubleshooting Common Issues:")
        print("1. Missing semantic events after merge:")
        print("   svcs sync --detect-merge")
        print()
        print("2. Semantic events not showing up from remote:")
        print("   svcs pull  # Automatically fetches semantic notes")
        print()
        print("3. Manual merge event transfer:")
        print("   svcs events process-merge --source-branch <branch>")
        print()
        print("4. Check what's happening:")
        print("   svcs status")
        print("   svcs events --limit 10")
        
    print()
    print("💡 Pro Tips:")
    print("• Use 'svcs pull/push' instead of 'git pull/push' for full semantic sync")
    print("• After complex git operations, run 'svcs sync' to fix any issues")
    print("• 'svcs events' shows the semantic history")
    print("• 'svcs compare branch1 branch2' shows semantic differences")
    print()
    print("📚 For more help: svcs workflow --type [basic|team|troubleshooting]")


def cmd_quick_help(args):
    """Show quick help for common SVCS workflows - streamlined cheat sheet."""
    print("🚀 SVCS Quick Help - Streamlined Workflow")
    print("=" * 50)
    print()
    print("📌 ESSENTIAL COMMANDS (replace git commands with these):")
    print("   svcs init        # Initialize SVCS (replaces: svcs init)")
    print("   svcs status      # Show semantic status")
    print("   svcs events      # View semantic changes")
    print()
    print("🔄 STREAMLINED SYNC COMMANDS:")
    print("   svcs sync-all    # Complete sync - handles everything automatically")
    print("   svcs sync        # Sync semantic data with remote")
    print("   svcs merge-resolve # Fix post-merge semantic issues")  
    print("   svcs auto-fix    # Auto-detect and fix common issues")
    print()
    print("🌿 BRANCH WORKFLOW:")
    print("   git checkout -b feature/xyz     # Create feature branch")
    print("   # Make changes, commit normally")
    print("   git checkout main && git merge feature/xyz")
    print("   # Semantic events automatically transferred!")
    print()
    print("🚨 AFTER COMPLEX MERGES:")
    print("   svcs auto-fix    # Fixes 90% of merge issues automatically")
    print("   svcs sync        # Syncs everything with remote")
    print()
    print("📊 USEFUL QUERIES:")
    print("   svcs events --limit 5")
    print("   svcs compare main feature/xyz")
    print("   svcs search --event-type function_added")
    print()
    print("💡 TIP: When in doubt, run 'svcs sync-all' first - it fixes most issues automatically!")
    print("📚 For detailed workflows: svcs workflow --type [basic|team|troubleshooting]")

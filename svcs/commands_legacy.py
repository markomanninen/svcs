#!/usr/bin/env python3
"""
SVCS CLI Commands Module
Individual command implementations for the SVCS CLI

This module contains all the command handler functions, separated from
the main CLI interface for better organization and maintainability.
"""

import json
import os
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Import core SVCS modules
try:
    from svcs_repo_local import RepositoryLocalSVCS, SVCSMigrator
    from svcs_repo_hooks import SVCSRepositoryManager
    from . import utils
except ImportError:
    # Development mode fallback
    current_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(current_dir))
    try:
        from svcs_repo_local import RepositoryLocalSVCS, SVCSMigrator
        from svcs_repo_hooks import SVCSRepositoryManager
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        import utils
    except ImportError:
        print("❌ Error: SVCS modules not found. Please ensure SVCS is properly installed.")
        sys.exit(1)

# Import smart initialization
try:
    from .centralized_utils import smart_init_svcs
except ImportError:
    try:
        from centralized_utils import smart_init_svcs
    except ImportError:
        # Fallback to a simple implementation
        def smart_init_svcs(repo_path):
            return "Smart init not available - using fallback"


# Core Repository Management Commands

def cmd_init(args):
    """Initialize SVCS for current repository with smart auto-detection."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    # Smart initialization logic
    result = smart_init_svcs(repo_path)
    print(result)


def cmd_status(args):
    """Show SVCS status for current repository."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    # Check if SVCS is initialized
    if not (repo_path / '.svcs' / 'semantic.db').exists():
        print(f"❌ SVCS not initialized for repository: {repo_path}")
        print("Run 'svcs init' to initialize SVCS for this repository.")
        return
    
    svcs = RepositoryLocalSVCS(repo_path)
    status = svcs.get_repository_status()
    
    print(f"✅ SVCS Repository Status")
    print(f"📁 Repository: {status['repository_path']}")
    print(f"🌿 Current branch: {status['current_branch']}")
    print(f"🔢 Semantic events: {status['semantic_events_count']}")
    print(f"📝 Commits analyzed: {status['commits_analyzed']}")
    print(f"📅 Initialized: {datetime.fromtimestamp(status['created_at']).strftime('%Y-%m-%d %H:%M:%S')}")


def cmd_cleanup(args):
    """Repository maintenance and cleanup."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not (repo_path / '.svcs' / 'semantic.db').exists():
        print(f"❌ SVCS not initialized. Run 'svcs init' first.")
        return
    
    print(f"🧹 Running cleanup for repository: {repo_path.name}")
    
    try:
        svcs = RepositoryLocalSVCS(repo_path)
        
        if args.git_unreachable:
            print("🔍 Cleaning semantic events for unreachable commits...")
            result = svcs.cleanup_unreachable_commits()
            print(result)
            
        elif args.show_stats:
            print("📊 Repository database statistics:")
            stats = svcs.get_database_stats()
            if isinstance(stats, dict):
                print(f"📈 Total events: {stats.get('total_events', 'N/A')}")
                print(f"📝 Commits tracked: {stats.get('commits_tracked', 'N/A')}")
                print(f"💾 Database size: {stats.get('database_size', 'N/A')}")
                
        else:
            print("🧹 Running general cleanup...")
            result = svcs.cleanup_orphaned_data()
            print(result)
            
    except Exception as e:
        print(f"❌ Error: {e}")


# Semantic Event Management Commands

def cmd_events(args):
    """List semantic events for current branch."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not (repo_path / '.svcs' / 'semantic.db').exists():
        print(f"❌ SVCS not initialized. Run 'svcs init' first.")
        return
        
    try:
        svcs = RepositoryLocalSVCS(repo_path)
        
        # Try different method names that might exist
        if hasattr(svcs, 'get_branch_events'):
            events = svcs.get_branch_events(branch=args.branch, limit=args.limit)
        elif hasattr(svcs, 'get_semantic_events'):
            events = svcs.get_semantic_events(branch=args.branch, limit=args.limit)
        else:
            print("❌ Error: Cannot find event retrieval method")
            return
        
        if not events:
            current_branch = svcs.get_current_branch()
            print(f"ℹ️ No semantic events found for branch: {current_branch}")
            return
        
        print(f"📊 Semantic Events ({len(events)} found)")
        print("=" * 60)
        
        for event in events:
            # Handle different timestamp formats
            timestamp = event.get('created_at', event.get('timestamp', ''))
            if isinstance(timestamp, (int, float)):
                timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"🔍 {event['event_type']}")
            print(f"   📝 {event['commit_hash'][:8]} | {event['branch']} | {event.get('author', 'N/A')} | {timestamp}")
            print(f"   🎯 {event['node_id']} @ {event['location']}")
            print(f"   💬 {event['details']}")
            print(f"   🧠 {event['reasoning']}")
            print()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        if '--debug' in sys.argv:
            import traceback
            traceback.print_exc()


def cmd_search(args):
    """Advanced semantic search."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not (repo_path / '.svcs' / 'semantic.db').exists():
        print(f"❌ SVCS not initialized. Run 'svcs init' first.")
        return
    
    try:
        # Import API functions
        sys.path.insert(0, str(repo_path / '.svcs'))
        from api import search_events_advanced, search_semantic_patterns
        
        # Determine search type
        if args.pattern_type:
            # Pattern-based search
            results = search_semantic_patterns(
                pattern_type=args.pattern_type,
                min_confidence=args.confidence,
                since_date=args.since,
                limit=args.limit
            )
            print(f"🎯 {args.pattern_type.title()} Patterns ({len(results)} found)")
        else:
            # Advanced event search
            search_params = {
                'author': args.author,
                'event_types': [args.event_type] if args.event_type else None,
                'min_confidence': args.confidence,
                'since_date': args.since,
                'limit': args.limit,
                'location_pattern': args.location
            }
            # Remove None values
            search_params = {k: v for k, v in search_params.items() if v is not None}
            
            results = search_events_advanced(**search_params)
            print(f"🔍 Search Results ({len(results)} found)")
        
        if not results:
            print("ℹ️ No results found. Try adjusting your search criteria.")
            return
            
        print("=" * 60)
        for result in results:
            timestamp = result.get('created_at', result.get('timestamp', ''))
            if isinstance(timestamp, (int, float)):
                timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                
            confidence = result.get('confidence', 1.0)
            if confidence < 1.0:
                confidence_str = f" ({confidence:.1%})"
            else:
                confidence_str = ""
                
            print(f"📊 {result['event_type']}{confidence_str}")
            print(f"   📝 {result.get('commit_hash', 'N/A')[:8]} | {result.get('branch', 'N/A')} | {result.get('author', 'N/A')} | {timestamp}")
            print(f"   🎯 {result.get('node_id', 'N/A')} @ {result.get('location', 'N/A')}")
            if 'details' in result:
                print(f"   💬 {result['details']}")
            if 'reasoning' in result:
                print(f"   🧠 {result['reasoning']}")
            print()
            
    except ImportError:
        print("❌ Error: API functions not available. Ensure SVCS is properly set up.")
    except Exception as e:
        print(f"❌ Error: {e}")


def cmd_evolution(args):
    """Track function/class evolution."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not (repo_path / '.svcs' / 'semantic.db').exists():
        print(f"❌ SVCS not initialized. Run 'svcs init' first.")
        return
    
    try:
        sys.path.insert(0, str(repo_path / '.svcs'))
        from api import get_filtered_evolution
        
        results = get_filtered_evolution(
            node_id=args.node_id,
            event_types=args.event_types,
            min_confidence=args.confidence,
            since_date=args.since
        )
        
        print(f"📈 Evolution of '{args.node_id}' ({len(results)} events)")
        print("=" * 60)
        
        if not results:
            print("ℹ️ No evolution events found for this node.")
            return
            
        for event in results:
            timestamp = event.get('created_at', event.get('timestamp', ''))
            if isinstance(timestamp, (int, float)):
                timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                
            confidence = event.get('confidence', 1.0)
            if confidence < 1.0:
                confidence_str = f" ({confidence:.1%})"
            else:
                confidence_str = ""
                
            print(f"🔄 {event['event_type']}{confidence_str}")
            print(f"   📝 {event.get('commit_hash', 'N/A')[:8]} | {event.get('branch', 'N/A')} | {event.get('author', 'N/A')} | {timestamp}")
            print(f"   📍 {event.get('location', 'N/A')}")
            if 'details' in event:
                print(f"   💬 {event['details']}")
            print()
            
    except ImportError:
        print("❌ Error: API functions not available. Ensure SVCS is properly set up.")
    except Exception as e:
        print(f"❌ Error: {e}")


def cmd_compare(args):
    """Compare semantic events between branches."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not (repo_path / '.svcs' / 'semantic.db').exists():
        print(f"❌ SVCS not initialized. Run 'svcs init' first.")
        return
    
    svcs = RepositoryLocalSVCS(repo_path)
    comparison = svcs.compare_branches(args.branch1, args.branch2, limit=args.limit)
    
    print(f"🔍 Comparing semantic events between branches: {args.branch1} ↔ {args.branch2}")
    print()
    print(f"🌿 Branch Comparison: {args.branch1} vs {args.branch2}")
    print("=" * 60)
    print(f"📊 Summary:")
    print(f"   {args.branch1}: {comparison['branch1_count']} total events")
    print(f"   {args.branch2}: {comparison['branch2_count']} total events")
    print(f"   Difference: {abs(comparison['branch1_count'] - comparison['branch2_count'])}")
    
    if comparison['branch1_events']:
        print(f"\n🌿 Recent events in '{args.branch1}':")
        for event in comparison['branch1_events'][:5]:
            # Handle different timestamp formats
            timestamp = event.get('created_at', event.get('timestamp', ''))
            if isinstance(timestamp, (int, float)):
                timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(timestamp, str) and len(timestamp) > 19:
                timestamp = timestamp[:19]
            print(f"  📊 {event['event_type']} at {event['location']} ({event['commit_hash'][:8]}) - {timestamp}")
    
    if comparison['branch2_events']:
        print(f"\n🌿 Recent events in '{args.branch2}':")
        for event in comparison['branch2_events'][:5]:
            # Handle different timestamp formats
            timestamp = event.get('created_at', event.get('timestamp', ''))
            if isinstance(timestamp, (int, float)):
                timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(timestamp, str) and len(timestamp) > 19:
                timestamp = timestamp[:19]
            print(f"  📊 {event['event_type']} at {event['location']} ({event['commit_hash'][:8]}) - {timestamp}")


def cmd_analytics(args):
    """Generate analytics reports."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not (repo_path / '.svcs' / 'semantic.db').exists():
        print(f"❌ SVCS not initialized. Run 'svcs init' first.")
        return
    
    print(f"📊 Generating analytics for repository: {repo_path.name}")
    
    try:
        # Try to use repository-local analytics if available
        try:
            from svcs_repo_analytics import generate_repository_analytics_report
            report = generate_repository_analytics_report(str(repo_path))
        except ImportError:
            # Fallback to adapted legacy analytics
            original_dir = os.getcwd()
            os.chdir(repo_path)
            
            # Import and adapt legacy analytics
            sys.path.insert(0, str(repo_path.parent))
            import svcs_analytics
            
            # Create a mock global context for legacy module
            class MockGlobalContext:
                def __init__(self, repo_path):
                    self.repo_path = repo_path
                    
                def get_projects(self):
                    return [{'path': str(repo_path), 'name': repo_path.name}]
                    
                def get_database_path(self, project_path):
                    return str(repo_path / '.svcs' / 'semantic.db')
            
            # Monkey patch for repository-local operation
            svcs_analytics.global_context = MockGlobalContext(repo_path)
            report = svcs_analytics.generate_analytics_report()
            os.chdir(original_dir)
        
        if args.output:
            output_path = Path(args.output)
            if args.format == 'json':
                with open(output_path, 'w') as f:
                    json.dump(report, f, indent=2)
                print(f"✅ Analytics report exported to: {output_path}")
            else:
                print("❌ Error: Only JSON export is currently supported")
        else:
            # Display summary
            print("✅ Analytics Report Generated")
            if isinstance(report, dict):
                print(f"📈 Total events: {report.get('total_events', 'N/A')}")
                print(f"👥 Authors: {report.get('author_count', 'N/A')}")
                print(f"📅 Date range: {report.get('date_range', 'N/A')}")
                print(f"🏆 Top event type: {report.get('top_event_type', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def cmd_quality(args):
    """Quality analysis."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not (repo_path / '.svcs' / 'semantic.db').exists():
        print(f"❌ SVCS not initialized. Run 'svcs init' first.")
        return
    
    print(f"🎯 Running quality analysis for repository: {repo_path.name}")
    
    try:
        # Try repository-local quality analysis if available
        try:
            from svcs_repo_quality import RepositoryQualityAnalyzer
            analyzer = RepositoryQualityAnalyzer(str(repo_path))
            report = analyzer.generate_quality_report()
        except ImportError:
            # Fallback to adapted legacy quality analysis
            original_dir = os.getcwd()
            os.chdir(repo_path)
            
            sys.path.insert(0, str(repo_path.parent))
            import svcs_quality
            
            # Adapt for repository-local operation
            report = svcs_quality.analyze_repository_quality(str(repo_path))
            os.chdir(original_dir)
        
        print("✅ Quality Analysis Complete")
        
        if isinstance(report, dict):
            print(f"📊 Quality Score: {report.get('quality_score', 'N/A')}")
            print(f"🔧 Improvement Areas: {len(report.get('improvement_areas', []))}")
            print(f"✨ Positive Trends: {len(report.get('positive_trends', []))}")
            print(f"⚠️ Quality Issues: {len(report.get('quality_issues', []))}")
            
            if args.verbose and 'improvement_areas' in report:
                print("\n🔧 Top Improvement Areas:")
                for area in report['improvement_areas'][:3]:
                    print(f"   • {area}")
                    
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"💾 Quality report exported to: {output_path}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def cmd_dashboard(args):
    """Generate static dashboard."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not (repo_path / '.svcs' / 'semantic.db').exists():
        print(f"❌ SVCS not initialized. Run 'svcs init' first.")
        return
    
    print(f"🎨 Generating dashboard for repository: {repo_path.name}")
    
    try:
        # Try repository-local dashboard generation
        try:
            from svcs_repo_web import generate_repository_dashboard
            dashboard_path = generate_repository_dashboard(str(repo_path), args.output)
        except ImportError:
            # Fallback to adapted legacy dashboard
            original_dir = os.getcwd()
            os.chdir(repo_path)
            
            sys.path.insert(0, str(repo_path.parent))
            import svcs_web
            
            # Generate dashboard for repository
            dashboard_path = args.output or f"{repo_path.name}_dashboard.html"
            svcs_web.generate_dashboard(dashboard_path)
            os.chdir(original_dir)
        
        print(f"✅ Dashboard generated: {dashboard_path}")
        print(f"🌐 Open in browser: file://{Path(dashboard_path).resolve()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


# Global web server state
web_server_process = None
web_server_thread = None


def cmd_web(args):
    """Interactive web dashboard management."""
    global web_server_process, web_server_thread
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if args.action == 'start':
        if not (repo_path / '.svcs' / 'semantic.db').exists():
            print(f"❌ SVCS not initialized. Run 'svcs init' first.")
            return
            
        print(f"🚀 Starting web dashboard for repository: {repo_path.name}")
        
        try:
            # Try to start repository-local web server
            original_dir = os.getcwd()
            os.chdir(repo_path)
            
            # Start web server in background
            def run_server():
                try:
                    sys.path.insert(0, str(repo_path.parent))
                    import svcs_web_server
                    
                    # Configure for repository-local operation
                    svcs_web_server.REPOSITORY_PATH = str(repo_path)
                    svcs_web_server.run_server(host=args.host, port=args.port, debug=args.debug)
                except Exception as e:
                    print(f"❌ Web server error: {e}")
            
            web_server_thread = threading.Thread(target=run_server, daemon=True)
            web_server_thread.start()
            
            # Give server time to start
            time.sleep(2)
            
            print(f"✅ Web dashboard started on http://{args.host}:{args.port}")
            print(f"🌐 Open in browser to explore semantic data")
            print(f"⏹️ Press Ctrl+C to stop or run 'svcs web stop'")
            
            # Keep main thread alive if not running in background
            if not args.background:
                try:
                    while web_server_thread.is_alive():
                        web_server_thread.join(1)
                except KeyboardInterrupt:
                    print("\n⏹️ Stopping web dashboard...")
                    
            os.chdir(original_dir)
            
        except Exception as e:
            print(f"❌ Error starting web server: {e}")
            os.chdir(original_dir)
            
    elif args.action == 'stop':
        print("⏹️ Stopping web dashboard...")
        # In a real implementation, you'd track and kill the server process
        print("ℹ️ Use Ctrl+C to stop the web server if running in foreground")
        
    elif args.action == 'status':
        print("📊 Web dashboard status:")
        if web_server_thread and web_server_thread.is_alive():
            print("✅ Web server is running")
        else:
            print("❌ Web server is not running")


def cmd_ci(args):
    """CI/CD integration."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not (repo_path / '.svcs' / 'semantic.db').exists():
        print(f"❌ SVCS not initialized. Run 'svcs init' first.")
        return
    
    print(f"🔄 Running CI command: {args.ci_command}")
    
    try:
        original_dir = os.getcwd()
        os.chdir(repo_path)
        
        sys.path.insert(0, str(repo_path.parent))
        # Try to use new repository-local CI integration first
        try:
            import svcs_repo_ci as svcs_ci
        except ImportError:
            # Fallback to legacy CI integration
            import svcs_ci
        
        if args.ci_command == 'pr-analysis':
            target_branch = args.target or 'main'
            result = svcs_ci.analyze_pr_semantic_impact(target_branch)
            print("✅ PR Analysis Complete")
            if isinstance(result, dict):
                print(f"📊 Semantic changes: {result.get('change_count', 'N/A')}")
                print(f"🎯 Risk level: {result.get('risk_level', 'N/A')}")
                
        elif args.ci_command == 'quality-gate':
            result = svcs_ci.run_quality_gate(strict=args.strict)
            print("✅ Quality Gate Complete")
            if isinstance(result, dict):
                passed = result.get('passed', False)
                print(f"{'✅' if passed else '❌'} Status: {'PASSED' if passed else 'FAILED'}")
                
        elif args.ci_command == 'report':
            format_type = args.format or 'text'
            result = svcs_ci.generate_ci_report(format_type)
            print(f"✅ CI Report generated in {format_type} format")
            
        os.chdir(original_dir)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        os.chdir(original_dir)


def cmd_discuss(args):
    """Start conversational interface."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not (repo_path / '.svcs' / 'semantic.db').exists():
        print(f"❌ SVCS not initialized. Run 'svcs init' first.")
        return
    
    print(f"🤖 Starting conversational interface for repository: {repo_path.name}")
    print("💬 Ask questions about your code's semantic evolution...")
    print("💡 Examples: 'show performance optimizations', 'what changed in main branch'")
    print("⏹️ Type 'exit' or 'quit' to end the session")
    print()
    
    try:
        original_dir = os.getcwd()
        os.chdir(repo_path)
        
        sys.path.insert(0, str(repo_path.parent))
        import legacy_scripts.svcs_discuss as svcs_discuss
        
        # Start interactive session
        svcs_discuss.start_interactive_session()
        
        os.chdir(original_dir)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        os.chdir(original_dir)


def cmd_query(args):
    """One-shot natural language query."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not (repo_path / '.svcs' / 'semantic.db').exists():
        print(f"❌ SVCS not initialized. Run 'svcs init' first.")
        return
    
    print(f"🤖 Processing query: '{args.query}'")
    
    try:
        original_dir = os.getcwd()
        os.chdir(repo_path)
        
        sys.path.insert(0, str(repo_path.parent))
        import legacy_scripts.svcs_discuss as svcs_discuss
        
        # Process single query
        result = svcs_discuss.process_query(args.query)
        print(result)
        
        os.chdir(original_dir)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        os.chdir(original_dir)


def cmd_notes(args):
    """Git notes management for team collaboration."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not (repo_path / '.svcs' / 'semantic.db').exists():
        print(f"❌ SVCS not initialized. Run 'svcs init' first.")
        return
    
    try:
        from svcs_repo_local import SVCSGitNotes
        notes_manager = SVCSGitNotes(str(repo_path))
        
        if args.notes_action == 'sync':
            print("🔄 Syncing semantic notes to remote...")
            result = notes_manager.sync_to_remote()
            print(result)
            
        elif args.notes_action == 'fetch':
            print("📥 Fetching semantic notes from remote...")
            result = notes_manager.fetch_from_remote()
            print(result)
            
        elif args.notes_action == 'show':
            commit_hash = args.commit or 'HEAD'
            print(f"📝 Showing semantic note for commit: {commit_hash}")
            note = notes_manager.get_note(commit_hash)
            if note:
                print(note)
            else:
                print("ℹ️ No semantic note found for this commit")
                
        elif args.notes_action == 'status':
            print("📊 Git notes status:")
            status = notes_manager.get_sync_status()
            print(f"Local notes: {status.get('local_count', 0)}")
            print(f"Remote status: {status.get('remote_status', 'Unknown')}")
            
    except ImportError:
        print("❌ Error: Git notes functionality not available")
    except Exception as e:
        print(f"❌ Error: {e}")


def cmd_process_hook(args):
    """Process git hook for semantic analysis."""
    hook_name = args.hook_name
    repo_path = Path(args.path or '.')
    
    # Determine the hook type and process accordingly
    if hook_name.endswith('post-commit'):
        # Post-commit: analyze the latest commit
        try:
            # Get the latest commit hash
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                  cwd=repo_path, capture_output=True, text=True, check=True)
            commit_hash = result.stdout.strip()
            
            # Initialize SVCS and analyzer
            from svcs_repo_local import RepositoryLocalSVCS
            from svcs_repo_analyzer import RepositoryLocalSemanticAnalyzer
            
            print("🔍 SVCS: Analyzing semantic changes...")
            svcs = RepositoryLocalSVCS(str(repo_path))
            analyzer = RepositoryLocalSemanticAnalyzer(str(repo_path))
            
            # Analyze the commit
            semantic_events = analyzer.analyze_commit(commit_hash)
            if semantic_events:
                stored_count, notes_success = svcs.analyze_and_store_commit(commit_hash, semantic_events)
                print(f'✅ SVCS: Stored {stored_count} semantic events')
                if notes_success:
                    print('📝 SVCS: Semantic data saved as git notes')
                else:
                    print('⚠️ SVCS: Failed to save git notes')
            else:
                print('ℹ️ SVCS: No semantic changes detected')
                
        except subprocess.CalledProcessError as e:
            print(f"❌ SVCS: Git command failed: {e}")
        except Exception as e:
            print(f"❌ SVCS: Analysis error: {e}")
            
    elif hook_name.endswith('post-merge'):
        # Post-merge: handle merge analysis and transfer semantic events
        try:
            print("🔍 SVCS: Processing merge...")
            
            # Initialize SVCS
            from svcs_repo_local import RepositoryLocalSVCS
            svcs = RepositoryLocalSVCS(str(repo_path))
            
            # First, import semantic events from git notes (for commits merged from remote)
            imported_count = svcs.import_semantic_events_from_notes()
            if imported_count > 0:
                print(f"📥 SVCS: Imported {imported_count} semantic events from git notes")
            
            # Then, automatically process merge and transfer semantic events between branches
            result = svcs.process_merge()
            print(f"✅ SVCS: {result}")
            
        except Exception as e:
            print(f"❌ SVCS: Merge processing error: {e}")
        
    elif hook_name.endswith('post-checkout'):
        # Post-checkout: handle branch switching
        print("🔍 SVCS: Processing checkout...")
        # Additional checkout processing can be added here
        
    elif hook_name.endswith('pre-push'):
        # Pre-push: validation or sync
        print("🔍 SVCS: Processing pre-push...")
        # Additional pre-push processing can be added here
        
    else:
        print(f"⚠️ SVCS: Unknown hook type: {hook_name}")


# Streamlined Workflow Commands

def cmd_pull(args):
    """Enhanced git pull that automatically handles semantic events from git notes."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not (repo_path / '.svcs' / 'semantic.db').exists():
        print("❌ SVCS not initialized. Run 'svcs init' first.")
        return
    
    print("🔄 SVCS: Enhanced pull with semantic event sync...")
    
    try:
        # Perform git pull
        result = subprocess.run(['git', 'pull'], cwd=repo_path, capture_output=True, text=True, check=True)
        print("📥 Git pull completed:")
        print(result.stdout)
        
        # Fetch semantic notes
        notes_result = subprocess.run([
            'git', 'fetch', 'origin', 'refs/notes/svcs-semantic:refs/notes/svcs-semantic'
        ], cwd=repo_path, capture_output=True, text=True)
        
        if notes_result.returncode == 0:
            print("📝 Semantic notes fetched from remote")
        
        # Import semantic events from newly fetched notes
        svcs = RepositoryLocalSVCS(repo_path)
        imported_count = svcs.import_semantic_events_from_notes()
        
        if imported_count > 0:
            print(f"✅ Imported {imported_count} semantic events from remote commits")
        else:
            print("ℹ️ No new semantic events to import")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Git pull failed: {e.stderr}")
    except Exception as e:
        print(f"❌ Error during enhanced pull: {e}")


def cmd_merge(args):
    """Enhanced git merge that automatically handles semantic event transfer."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not (repo_path / '.svcs' / 'semantic.db').exists():
        print("❌ SVCS not initialized. Run 'svcs init' first.")
        return
    
    branch_to_merge = args.branch
    merge_args = []
    
    if args.no_ff:
        merge_args.append('--no-ff')
    if args.message:
        merge_args.extend(['-m', args.message])
    
    print(f"🔄 SVCS: Enhanced merge of '{branch_to_merge}' with automatic semantic event transfer...")
    
    try:
        # Check if source branch has semantic events
        svcs = RepositoryLocalSVCS(repo_path)
        source_events = svcs.get_branch_events(branch_to_merge, limit=1)
        
        if source_events:
            print(f"📊 Found semantic events on '{branch_to_merge}' branch")
        
        # Perform git merge
        cmd = ['git', 'merge'] + merge_args + [branch_to_merge]
        result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True, check=True)
        
        print("✅ Git merge completed:")
        print(result.stdout)
        
        # The post-merge hook should automatically handle semantic event transfer
        # But let's also provide manual option for complex cases
        if args.manual_transfer:
            transfer_result = svcs.process_merge(source_branch=branch_to_merge)
            print(f"📋 Manual semantic transfer: {transfer_result}")
        
        # Show updated events
        print("\n📊 Updated semantic events on current branch:")
        current_events = svcs.get_branch_events(limit=5)
        for event in current_events[:3]:
            print(f"   🔍 {event.get('event_type', 'unknown')} | {event.get('node_id', 'N/A')} | {event.get('commit_hash', 'N/A')[:8]}")
        
        if len(current_events) > 3:
            print(f"   ... and {len(current_events) - 3} more events")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Git merge failed: {e.stderr}")
        if "conflict" in e.stderr.lower():
            print("💡 Tip: Resolve conflicts and run 'svcs sync' after committing")
    except Exception as e:
        print(f"❌ Error during enhanced merge: {e}")


def cmd_sync(args):
    """Sync semantic data with remote repository."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not (repo_path / '.svcs' / 'semantic.db').exists():
        print(f"❌ SVCS not initialized. Run 'svcs init' first.")
        return
    
    try:
        from svcs_repo_local import RepositoryLocalSVCS
        svcs = RepositoryLocalSVCS(repo_path)
        
        print("🔄 Syncing semantic data with remote...")
        
        # 1. Push local semantic notes to remote
        push_success = svcs.git_notes.sync_notes_to_remote()
        if push_success:
            print("📤 Pushed local semantic notes to remote")
        
        # 2. Fetch semantic notes from remote
        fetch_success = svcs.git_notes.fetch_notes_from_remote()
        if fetch_success:
            print("📥 Fetched semantic notes from remote")
            
            # 3. Import semantic events from fetched notes
            imported = svcs.import_semantic_events_from_notes()
            if imported > 0:
                print(f"📊 Imported {imported} semantic events from remote notes")
        
        # 4. Process any pending merges
        merge_result = svcs.process_merge()
        if "No source branch detected" not in merge_result:
            print(f"🔀 {merge_result}")
        
        print("✅ Semantic data sync completed")
        
    except Exception as e:
        print(f"❌ Sync error: {e}")


def cmd_merge_resolve(args):
    """Automatically resolve post-merge semantic event issues."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not (repo_path / '.svcs' / 'semantic.db').exists():
        print(f"❌ SVCS not initialized. Run 'svcs init' first.")
        return
    
    try:
        from svcs_repo_local import RepositoryLocalSVCS
        svcs = RepositoryLocalSVCS(repo_path)
        
        print("🔍 Checking for post-merge semantic event issues...")
        
        # Import semantic events from git notes first
        imported = svcs.import_semantic_events_from_notes()
        if imported > 0:
            print(f"📥 Imported {imported} semantic events from git notes")
        
        # Process merge event transfer
        merge_result = svcs.process_merge()
        print(f"🔀 {merge_result}")
        
        # Show final status
        status = svcs.get_repository_status()
        print(f"📊 Final status: {status['semantic_events_count']} semantic events on {status['current_branch']}")
        
    except Exception as e:
        print(f"❌ Merge resolve error: {e}")


def cmd_auto_fix(args):
    """Automatically detect and fix common SVCS issues after git operations."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not (repo_path / '.svcs' / 'semantic.db').exists():
        print(f"❌ SVCS not initialized. Run 'svcs init' first.")
        return
    
    try:
        from svcs_repo_local import RepositoryLocalSVCS
        svcs = RepositoryLocalSVCS(repo_path)
        
        print("🔧 Auto-detecting and fixing SVCS issues...")
        
        result = svcs.auto_resolve_merge()
        print(f"🔀 {result}")
        
        print("✅ Auto-fix completed")
        
    except Exception as e:
        print(f"❌ Auto-fix error: {e}")


def cmd_push(args):
    """Enhanced git push that automatically syncs semantic notes."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not (repo_path / '.svcs' / 'semantic.db').exists():
        print("❌ SVCS not initialized. Run 'svcs init' first.")
        return
    
    print("📤 SVCS: Enhanced push with semantic notes sync...")
    
    push_args = []
    if args.force:
        push_args.append('--force')
    if args.set_upstream:
        push_args.extend(['--set-upstream', 'origin'])
        
    branch = args.branch or 'HEAD'
    
    try:
        # Perform git push
        cmd = ['git', 'push'] + push_args + ['origin', branch]
        result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True, check=True)
        
        print("✅ Git push completed:")
        print(result.stdout)
        
        # Push semantic notes
        if not args.skip_notes:
            notes_result = subprocess.run([
                'git', 'push', 'origin', 'refs/notes/svcs-semantic:refs/notes/svcs-semantic'
            ], cwd=repo_path, capture_output=True, text=True)
            
            if notes_result.returncode == 0:
                print("📝 Semantic notes pushed to remote")
            else:
                print("ℹ️ No semantic notes to push (this is normal for new repositories)")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git push failed: {e.stderr}")
    except Exception as e:
        print(f"❌ Error during enhanced push: {e}")


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

def cmd_sync_all(args):
    """Complete sync after git operations - fetches, imports, and resolves everything."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not (repo_path / '.svcs' / 'semantic.db').exists():
        print(f"❌ SVCS not initialized. Run 'svcs init' first.")
        return
    
    try:
        from svcs_repo_local import RepositoryLocalSVCS
        svcs = RepositoryLocalSVCS(repo_path)
        
        print("🔄 Complete SVCS sync - fetching, importing, and resolving...")
        print()
        
        # Step 1: Try to sync with remote
        print("📡 Step 1: Syncing with remote...")
        try:
            # Push/pull semantic notes
            svcs.git_notes.sync_notes_to_remote()
            svcs.git_notes.fetch_notes_from_remote()
            print("✅ Remote sync completed")
        except Exception as e:
            print(f"ℹ️ Remote sync skipped: {str(e)[:50]}...")
        
        # Step 2: Import any semantic events from notes
        print("📥 Step 2: Importing semantic events from git notes...")
        imported = svcs.import_semantic_events_from_notes()
        if imported > 0:
            print(f"✅ Imported {imported} semantic events")
        else:
            print("ℹ️ No new semantic events to import")
        
        # Step 3: Process any pending merges
        print("🔀 Step 3: Processing merge operations...")
        merge_result = svcs.process_merge()
        if "No source branch detected" not in merge_result and "No new semantic events" not in merge_result:
            print(f"✅ {merge_result}")
        else:
            print("ℹ️ No pending merge operations")
        
        # Step 4: Final status
        print("📊 Step 4: Final status check...")
        status = svcs.get_repository_status()
        print(f"✅ Repository: {status['semantic_events_count']} semantic events on {status['current_branch']}")
        
        print()
        print("🎉 Complete sync finished! Your semantic data is now up-to-date.")
        
    except Exception as e:
        print(f"❌ Sync error: {e}")

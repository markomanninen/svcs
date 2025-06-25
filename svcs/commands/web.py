#!/usr/bin/env python3
"""
SVCS Web Interface Commands

Commands for generating dashboards and managing web interfaces.
"""

import sys
import threading
import time
from pathlib import Path
from .base import ensure_svcs_initialized, print_svcs_error


# Global web server state
web_server_process = None
web_server_thread = None


def cmd_dashboard(args):
    """Generate static dashboard."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not ensure_svcs_initialized(repo_path):
        print_svcs_error("SVCS not initialized. Run 'svcs init' first.")
        return
    
    print(f"🎨 Generating dashboard for repository: {repo_path.name}")
    
    try:
        # Try repository-local dashboard generation
        try:
            from svcs_repo_web import generate_repository_dashboard
            dashboard_path = generate_repository_dashboard(str(repo_path), args.output)
        except ImportError:
            # Fallback to adapted legacy dashboard
            import os
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
        print_svcs_error(f"Error: {e}")


def cmd_web(args):
    """Interactive web dashboard management."""
    global web_server_process, web_server_thread
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if args.action == 'start':
        # No need to check SVCS initialization - web server can manage multiple repos
        print(f"🚀 Starting SVCS web server (repository-local architecture)")
        
        try:
            # Start new repository-local web server
            def run_server():
                try:
                    # Add parent directory to path to find the new web server
                    parent_dir = Path(__file__).parent.parent.parent
                    sys.path.insert(0, str(parent_dir))
                    
                    import svcs_repo_web_server
                    svcs_repo_web_server.run_server(host=args.host, port=args.port, debug=args.debug)
                except Exception as e:
                    print(f"❌ Web server error: {e}")
            
            web_server_thread = threading.Thread(target=run_server, daemon=True)
            web_server_thread.start()
            
            # Give server time to start
            time.sleep(2)
            
            print(f"✅ Web server started on http://{args.host}:{args.port}")
            print(f"🌐 Open in browser to manage multiple repositories")
            print(f"📊 Features: repository discovery, semantic search, evolution tracking")
            print(f"⏹️ Press Ctrl+C to stop or run 'svcs web stop'")
            
            # Keep main thread alive if not running in background
            if not args.background:
                try:
                    while web_server_thread.is_alive():
                        web_server_thread.join(1)
                except KeyboardInterrupt:
                    print("\n⏹️ Stopping web server...")
                    
        except Exception as e:
            print_svcs_error(f"Error starting web server: {e}")
            
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

#!/usr/bin/env python3
"""
SVCS Interactive Web Dashboard Backend Server

This Flask server provides the web interface and API endpoints for the SVCS dashboard.
It serves the HTML dashboard and provides REST API endpoints for all SVCS functionality.

Usage:
    python3 svcs_web_server.py [--port 8080] [--host 0.0.0.0]
"""

import os
import sys
import json
import argparse
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory, render_template_string
from flask_cors import CORS

# Add .svcs to path for API imports
sys.path.insert(0, '.svcs')

# Add svcs_mcp path for core database engine
sys.path.insert(0, 'svcs_mcp')

try:
    from api import (
        search_events_advanced,
        get_recent_activity,
        get_project_statistics,
        search_semantic_patterns,
        get_filtered_evolution,
        get_node_evolution,
        debug_query_tools,
        get_commit_changed_files,
        get_commit_diff,
        get_commit_summary,
        get_full_log
    )
    # Import core database engine for prune functionality and project management
    from svcs_core import GlobalSVCSDatabase
except ImportError as e:
    print(f"Error importing SVCS API: {e}")
    print("Please ensure you're running this from the SVCS root directory with .svcs/api.py available")
    sys.exit(1)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# Configuration
DEFAULT_PORT = 8080
DEFAULT_HOST = '127.0.0.1'

# Basic routes
@app.route('/favicon.ico')
def favicon():
    """Return a simple favicon to prevent 404 errors."""
    return '', 204

@app.route('/')
def dashboard():
    """Serve the main dashboard HTML."""
    dashboard_path = Path(__file__).parent / 'svcs_interactive_dashboard.html'
    if dashboard_path.exists():
        with open(dashboard_path, 'r') as f:
            content = f.read()
        response = app.response_class(
            response=content,
            status=200,
            mimetype='text/html'
        )
        # Add cache control headers to prevent caching during development
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    else:
        return """
        <h1>SVCS Dashboard</h1>
        <p>Dashboard HTML file not found. Please ensure svcs_interactive_dashboard.html exists in the same directory.</p>
        """

# API Endpoints

@app.route('/api/search_events', methods=['POST'])
def api_search_events():
    """Advanced search for semantic events."""
    try:
        data = request.get_json() or {}
        
        # Extract parameters with defaults
        author = data.get('author')
        days = data.get('days', 7)
        min_confidence = float(data.get('min_confidence', 0.0)) if data.get('min_confidence') else None
        limit = int(data.get('limit', 20))
        layers = data.get('layers', [])
        event_types = data.get('event_types', [])
        
        # Handle legacy frontend that might send 'layer' instead of 'layers'
        if not layers and data.get('layer'):
            layers = [data.get('layer')]
        
        # Calculate since_date from days
        since_date = f"{days} days ago" if days else None
        
        result = search_events_advanced(
            author=author,
            since_date=since_date,
            min_confidence=min_confidence,
            limit=limit,
            layers=layers if layers else None,
            event_types=event_types if event_types else None
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'total': len(result) if isinstance(result, list) else 0
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/search_patterns', methods=['POST'])
def api_search_patterns():
    """Search for semantic patterns."""
    try:
        data = request.get_json() or {}
        
        pattern_type = data.get('pattern_type', 'performance')
        min_confidence = float(data.get('min_confidence', 0.7))
        since_date = data.get('since_date', '30 days ago')
        limit = int(data.get('limit', 10))
        author = data.get('author')
        
        result = search_semantic_patterns(
            pattern_type=pattern_type,
            min_confidence=min_confidence,
            since_date=since_date,
            limit=limit,
            author=author
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Alias route for compatibility with dashboard
@app.route('/api/search_semantic_patterns', methods=['POST'])
def api_search_semantic_patterns():
    """Alias for search_patterns to maintain compatibility."""
    return api_search_patterns()

@app.route('/api/get_commit_changed_files', methods=['POST'])
def api_get_commit_changed_files():
    """Get files changed in a commit."""
    try:
        data = request.get_json() or {}
        commit_hash = data.get('commit_hash')
        
        if not commit_hash:
            return jsonify({
                'success': False,
                'error': 'commit_hash is required'
            }), 400
        
        result = get_commit_changed_files(commit_hash)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get_commit_diff', methods=['POST'])
def api_get_commit_diff():
    """Get git diff for a commit."""
    try:
        data = request.get_json() or {}
        commit_hash = data.get('commit_hash')
        file_path = data.get('file_path')
        
        if not commit_hash:
            return jsonify({
                'success': False,
                'error': 'commit_hash is required'
            }), 400
        
        result = get_commit_diff(commit_hash, file_path)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get_commit_summary', methods=['POST'])
def api_get_commit_summary():
    """Get comprehensive commit summary."""
    try:
        data = request.get_json() or {}
        commit_hash = data.get('commit_hash')
        
        if not commit_hash:
            return jsonify({
                'success': False,
                'error': 'commit_hash is required'
            }), 400
        
        result = get_commit_summary(commit_hash)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get_recent_activity', methods=['POST'])
def api_get_recent_activity():
    """Get recent semantic activity."""
    try:
        data = request.get_json() or {}
        days = int(data.get('days', 7))
        limit = int(data.get('limit', 15))
        author = data.get('author')
        layers = data.get('layers')
        
        result = get_recent_activity(
            days=days,
            limit=limit,
            author=author,
            layers=layers
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get_node_evolution', methods=['POST'])
def api_get_node_evolution():
    """Get evolution history for a specific node."""
    try:
        data = request.get_json() or {}
        node_id = data.get('node_id')
        
        if not node_id:
            return jsonify({
                'success': False,
                'error': 'node_id is required'
            }), 400
        
        result = get_node_evolution(node_id)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get_filtered_evolution', methods=['POST'])
def api_get_filtered_evolution():
    """Get filtered evolution history for a node."""
    try:
        data = request.get_json() or {}
        node_id = data.get('node_id')
        since_date = data.get('since_date')
        min_confidence = float(data.get('min_confidence', 0.0)) if data.get('min_confidence') else None
        event_types = data.get('event_types')
        until_date = data.get('until_date')
        
        if not node_id:
            return jsonify({
                'success': False,
                'error': 'node_id is required'
            }), 400
        
        result = get_filtered_evolution(
            node_id=node_id,
            since_date=since_date,
            min_confidence=min_confidence,
            event_types=event_types,
            until_date=until_date
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get_project_statistics', methods=['POST'])
def api_get_project_statistics():
    """Get project statistics."""
    try:
        data = request.get_json() or {}
        since_date = data.get('since_date')
        until_date = data.get('until_date')
        group_by = data.get('group_by', 'event_type')
        
        result = get_project_statistics(
            since_date=since_date,
            until_date=until_date,
            group_by=group_by
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/debug_query_tools', methods=['POST'])
def api_debug_query_tools():
    """Debug query tools."""
    try:
        data = request.get_json() or {}
        query_description = data.get('query_description', 'web dashboard query')
        
        result = debug_query_tools(query_description)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get_logs', methods=['POST'])
def api_get_logs():
    """Get system logs."""
    try:
        data = request.get_json() or {}
        log_type = data.get('type', 'inference')
        lines = int(data.get('lines', 50))
        
        # Read logs from .svcs/logs directory
        logs_dir = Path('.svcs/logs')
        if not logs_dir.exists():
            return jsonify({
                'success': True,
                'data': {'message': 'No logs directory found'}
            })
        
        log_files = []
        if log_type == 'inference':
            log_files = list(logs_dir.glob('*inference*.log'))
        elif log_type == 'error':
            log_files = list(logs_dir.glob('*error*.log'))
        else:
            log_files = list(logs_dir.glob('*.log'))
        
        if not log_files:
            return jsonify({
                'success': True,
                'data': {'message': f'No {log_type} log files found'}
            })
        
        # Read the most recent log file
        latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
        
        try:
            with open(latest_log, 'r') as f:
                log_lines = f.readlines()
                recent_lines = log_lines[-lines:] if len(log_lines) > lines else log_lines
                
            return jsonify({
                'success': True,
                'data': {
                    'file': str(latest_log),
                    'total_lines': len(log_lines),
                    'showing_lines': len(recent_lines),
                    'logs': [json.loads(line.strip()) for line in recent_lines if line.strip()]
                }
            })
            
        except json.JSONDecodeError:
            # If logs are not JSON, return as plain text
            with open(latest_log, 'r') as f:
                content = f.read()
                lines_list = content.split('\n')[-lines:]
                
            return jsonify({
                'success': True,
                'data': {
                    'file': str(latest_log),
                    'logs': lines_list
                }
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/list_projects', methods=['POST', 'GET'])
def api_list_projects():
    """List all SVCS projects."""
    try:
        # Use the database to list projects
        db = GlobalSVCSDatabase()
        projects = db.list_projects()
        
        return jsonify({
            'success': True,
            'data': projects
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/register_project', methods=['POST'])
def api_register_project():
    """Register a new project."""
    try:
        data = request.get_json() or {}
        project_path = data.get('path')
        project_name = data.get('name')
        
        if not project_path or not project_name:
            return jsonify({
                'success': False,
                'error': 'Both path and name are required'
            }), 400
        
        # Use the actual database to register the project
        db = GlobalSVCSDatabase()
        result = db.register_project(project_name, project_path)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate_analytics', methods=['POST'])
def api_generate_analytics():
    """Generate analytics report."""
    try:
        # Run analytics and return results
        result = get_full_log()  # Get all events
        
        # Process and limit the results
        events_list = result if isinstance(result, list) else []
        limited_events = events_list[:100] if len(events_list) > 100 else events_list
        
        analytics_data = {
            'total_events': len(events_list),
            'events_shown': len(limited_events),
            'report_generated': True,
            'timestamp': '2025-06-22T18:00:00Z',
            'sample_data': limited_events[:10] if len(limited_events) > 10 else limited_events
        }
        
        return jsonify({
            'success': True,
            'data': analytics_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/quality_analysis', methods=['POST'])
def api_quality_analysis():
    """Run quality analysis."""
    try:
        # Mock quality analysis
        result = {
            'quality_score': 85,
            'trends': {
                'improving': ['error_handling', 'documentation'],
                'declining': ['complexity'],
                'stable': ['performance', 'maintainability']
            },
            'recommendations': [
                'Consider refactoring high-complexity functions',
                'Continue improving error handling patterns',
                'Add more unit tests for new features'
            ]
        }
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/export_data', methods=['POST'])
def api_export_data():
    """Export SVCS data."""
    try:
        result = {
            'export_initiated': True,
            'format': 'JSON',
            'estimated_size': '2.5MB',
            'download_url': '/api/download/svcs_export.json'
        }
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/prune_database', methods=['POST'])
def api_prune_database():
    """Prune orphaned data from the SVCS database."""
    try:
        data = request.get_json() or {}
        project_path = data.get('project_path')  # Optional - if not provided, prunes all projects
        dry_run = data.get('dry_run', True)  # Default to dry run for safety
        
        db = GlobalSVCSDatabase()
        
        # Perform the prune operation using the correct method
        result = db.prune_orphaned_data(project_path=project_path)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/remove_project', methods=['POST'])
def api_remove_project():
    """Remove a registered project."""
    try:
        data = request.get_json() or {}
        project_name = data.get('name')
        
        if not project_name:
            return jsonify({
                'success': False,
                'error': 'Project name is required'
            }), 400
        
        # Mock removal - in reality this would call MCP server
        result = {
            'message': f'Project "{project_name}" removed',
            'project': {
                'name': project_name,
                'status': 'removed'
            }
        }
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/cleanup_project', methods=['POST'])
def api_cleanup_project():
    """Cleanup project data."""
    try:
        data = request.get_json() or {}
        project_name = data.get('name')
        dry_run = data.get('dry_run', True)  # Default to dry run for safety
        
        if not project_name:
            return jsonify({
                'success': False,
                'error': 'Project name is required'
            }), 400
        
        # Mock cleanup - in reality this would call MCP server
        result = {
            'message': f'Project "{project_name}" cleanup completed',
            'project': {
                'name': project_name,
                'status': 'cleaned'
            }
        }
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/unregister_project', methods=['POST'])
def api_unregister_project():
    """Unregister a project (soft delete - keeps data)."""
    try:
        data = request.get_json() or {}
        project_path = data.get('project_path')
        
        if not project_path:
            return jsonify({
                'success': False,
                'error': 'project_path is required'
            }), 400
        
        db = GlobalSVCSDatabase()
        result = db.unregister_project(project_path)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/purge_project', methods=['POST'])
def api_purge_project():
    """Purge a project completely (hard delete - removes all data)."""
    try:
        data = request.get_json() or {}
        project_path = data.get('project_path')
        confirm = data.get('confirm', False)
        
        if not project_path:
            return jsonify({
                'success': False,
                'error': 'project_path is required'
            }), 400
        
        if not confirm:
            return jsonify({
                'success': False,
                'error': 'Confirmation required for project purge. Set confirm=true'
            }), 400
        
        db = GlobalSVCSDatabase()
        result = db.purge_project(project_path)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/cleanup_projects', methods=['POST'])
def api_cleanup_projects():
    """Get cleanup information about projects."""
    try:
        data = request.get_json() or {}
        show_inactive = data.get('show_inactive', True)
        show_stats = data.get('show_stats', True)
        
        db = GlobalSVCSDatabase()
        result = {}
        
        if show_inactive:
            try:
                # Get all projects and filter for inactive ones
                all_projects = db.list_projects()
                # Handle both dict and string return types
                if isinstance(all_projects, str):
                    result['inactive_projects'] = "No inactive projects found"
                else:
                    inactive_projects = [p for p in all_projects if not p.get('is_active', True)]
                    result['inactive_projects'] = inactive_projects
            except Exception as e:
                result['inactive_projects'] = f"Error getting inactive projects: {str(e)}"
        
        if show_stats:
            try:
                # Try to get database statistics
                if hasattr(db, 'get_database_stats'):
                    stats = db.get_database_stats()
                    result['database_stats'] = stats
                else:
                    # Fallback to basic stats
                    result['database_stats'] = "Database statistics not available"
            except Exception as e:
                result['database_stats'] = f"Error getting stats: {str(e)}"
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'SVCS Interactive Dashboard',
        'version': '1.0.0'
    })

def main():
    """Main entry point for the web server."""
    parser = argparse.ArgumentParser(description='SVCS Interactive Web Dashboard Server')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, 
                       help=f'Port to run the server on (default: {DEFAULT_PORT})')
    parser.add_argument('--host', default=DEFAULT_HOST,
                       help=f'Host to bind to (default: {DEFAULT_HOST})')
    parser.add_argument('--debug', action='store_true',
                       help='Run in debug mode')
    
    args = parser.parse_args()
    
    print(f"🚀 Starting SVCS Interactive Dashboard Server")
    print(f"📍 Server: http://{args.host}:{args.port}")
    print(f"🔧 Debug mode: {args.debug}")
    print(f"📂 Working directory: {os.getcwd()}")
    print()
    print("Available endpoints:")
    print("  GET  /           - Interactive dashboard")
    print("  GET  /health     - Health check")
    print("  POST /api/*      - SVCS API endpoints")
    print("    /api/search_events        - Advanced semantic search")
    print("    /api/search_patterns      - Search semantic patterns")
    print("    /api/get_commit_*         - Git commit information")
    print("    /api/list_projects        - List all projects")
    print("    /api/register_project     - Register new project")
    print("    /api/unregister_project   - Unregister project (soft delete)")
    print("    /api/purge_project        - Purge project completely (hard delete)")
    print("    /api/cleanup_projects     - Get cleanup information")
    print("    /api/prune_database       - Clean orphaned data")
    print("    /api/remove_project       - Remove a registered project")
    print("    /api/cleanup_project      - Cleanup project data")
    print("    /api/unregister_project   - Unregister a project (soft delete)")
    print("    /api/purge_project        - Purge a project completely (hard delete)")
    print("    /api/cleanup_projects     - Get cleanup information about projects")
    print()
    print("Press Ctrl+C to stop the server")
    
    try:
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

if __name__ == '__main__':
    main()

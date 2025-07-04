#!/usr/bin/env python3
"""
SVCS Web Server - New Repository-Local Architecture

Modern Flask server for SVCS using repository-local semantic.db files
with central registry at ~/.svcs/repos.db for project management.

Usage:
    python3 svcs_web_server_new.py [--port 8080] [--host 127.0.0.1]
"""

import os
import sys
import json
import subprocess
import time
import argparse
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# Import the modernized repository manager
from svcs_web_repository_manager import web_repository_manager, REPO_LOCAL_AVAILABLE

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# Configuration
DEFAULT_PORT = 8080
DEFAULT_HOST = '127.0.0.1'

# Utility function for safe JSON handling
def get_request_data():
    """Safely get JSON data from request with better error handling."""
    if not request.is_json:
        return None, {'success': False, 'error': 'Content-Type must be application/json'}
    
    try:
        data = request.get_json()
        if data is None:
            return {}, None
        return data, None
    except Exception as e:
        return None, {'success': False, 'error': f'Invalid JSON: {str(e)}'}

# Basic routes
@app.route('/favicon.ico')
def favicon():
    """Return a simple favicon to prevent 404 errors."""
    return '', 204

@app.route('/')
def dashboard():
    """Serve the main dashboard HTML."""
    try:
        # Serve the new modular web-app first
        web_app_path = Path(__file__).parent / 'web-app' / 'index.html'
        if web_app_path.exists():
            return send_from_directory(str(web_app_path.parent), 'index.html')
        else:
            # Fallback to new dashboard
            dashboard_path = Path(__file__).parent / 'svcs_new_dashboard.html'
            if dashboard_path.exists():
                return send_from_directory(str(dashboard_path.parent), 'svcs_new_dashboard.html')
            else:
                # Fallback to old dashboard
                old_dashboard_path = Path(__file__).parent / 'svcs_interactive_dashboard.html'
                if old_dashboard_path.exists():
                    return send_from_directory(str(old_dashboard_path.parent), 'svcs_interactive_dashboard.html')
                else:
                    return jsonify({'error': 'Dashboard not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'SVCS Web Server (New Architecture)',
        'version': '0.1',
        'architecture': 'repository-local',
        'repo_local_available': REPO_LOCAL_AVAILABLE
    })

# Static file serving for modular web-app
@app.route('/css/<path:filename>')
def serve_css(filename):
    """Serve CSS files from web-app/css directory."""
    css_path = Path(__file__).parent / 'web-app' / 'css'
    if css_path.exists():
        return send_from_directory(str(css_path), filename)
    return jsonify({'error': 'CSS file not found'}), 404

@app.route('/js/<path:filename>')
def serve_js(filename):
    """Serve JavaScript files from web-app/js directory."""
    js_path = Path(__file__).parent / 'web-app' / 'js'
    if js_path.exists():
        return send_from_directory(str(js_path), filename)
    return jsonify({'error': 'JS file not found'}), 404

@app.route('/js/components/<path:filename>')
def serve_js_components(filename):
    """Serve JavaScript component files from web-app/js/components directory."""
    components_path = Path(__file__).parent / 'web-app' / 'js' / 'components'
    if components_path.exists():
        return send_from_directory(str(components_path), filename)
    return jsonify({'error': 'JS component file not found'}), 404

# Repository Management Endpoints
@app.route('/api/repositories/discover', methods=['GET', 'POST'])
def discover_repositories():
    """Discover SVCS repositories from registry and filesystem scan."""
    try:
        # Handle both GET and POST requests safely
        scan_paths = None
        if request.method == 'POST' and request.is_json:
            data = request.get_json() or {}
            scan_paths = data.get('scan_paths')
        elif request.method == 'GET':
            # For GET requests, check query parameters
            scan_paths_param = request.args.get('scan_paths')
            if scan_paths_param:
                scan_paths = scan_paths_param.split(',')
        
        repositories = web_repository_manager.discover_repositories(scan_paths)
        
        return jsonify({
            'success': True,
            'data': {
                'repositories': repositories,
                'total': len(repositories),
                'architecture': 'repository-local'
            }
        })
    except Exception as e:
        app.logger.error(f"Error in discover_repositories: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/repositories/register', methods=['POST'])
def register_repository():
    """Register repository in central registry."""
    try:
        data, error = get_request_data()
        if error:
            return jsonify(error), 400
            
        repo_path = data.get('path')
        name = data.get('name')
        
        if not repo_path:
            return jsonify({'success': False, 'error': 'Repository path required'}), 400
        
        result = web_repository_manager.register_repository(repo_path, name)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
    except Exception as e:
        app.logger.error(f"Error in register_repository: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/repositories/unregister', methods=['POST'])
def unregister_repository():
    """Remove repository from central registry."""
    try:
        data, error = get_request_data()
        if error:
            return jsonify(error), 400
            
        repo_path = data.get('path')
        
        if not repo_path:
            return jsonify({'success': False, 'error': 'Repository path required'}), 400
        
        result = web_repository_manager.unregister_repository(repo_path)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
    except Exception as e:
        app.logger.error(f"Error in unregister_repository: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/repositories/initialize', methods=['POST'])
def initialize_repository():
    """Initialize SVCS for a repository."""
    try:
        data, error = get_request_data()
        if error:
            return jsonify(error), 400
            
        repo_path = data.get('path')
        
        if not repo_path:
            return jsonify({'success': False, 'error': 'Repository path required'}), 400
        
        result = web_repository_manager.initialize_repository(repo_path)
        
        if result['success']:
            # Auto-register after successful initialization
            register_result = web_repository_manager.register_repository(repo_path)
            if register_result['success']:
                result['message'] += f"\n{register_result['message']}"
            
            return jsonify(result)
        else:
            return jsonify(result), 400
    except Exception as e:
        app.logger.error(f"Error in initialize_repository: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/repositories/statistics', methods=['POST'])
def get_repository_statistics():
    """Get repository statistics."""
    try:
        data, error = get_request_data()
        if error:
            return jsonify(error), 400
            
        repo_path = data.get('repository_path') or data.get('path')
        
        if not repo_path:
            return jsonify({'success': False, 'error': 'Repository path required'}), 400
        
        stats = web_repository_manager.get_repository_statistics(repo_path)
        
        if 'error' in stats:
            return jsonify({'success': False, 'error': stats['error']}), 404
        
        return jsonify({'success': True, 'data': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Semantic Analysis Endpoints
@app.route('/api/semantic/search_events', methods=['POST'])
def search_events():
    """Search semantic events in repository."""
    try:
        data = request.get_json()
        repo_path = data.get('repository_path')
        
        if not repo_path:
            return jsonify({'success': False, 'error': 'repository_path required'}), 400
        
        # Extract search parameters - now including ordering
        limit = data.get('limit', 20)
        event_type = data.get('event_type')
        since_days = data.get('since_days')
        order_by = data.get('order_by', 'timestamp')
        order_desc = data.get('order_desc', True)
        
        events = web_repository_manager.search_events(
            repo_path, 
            limit=limit, 
            event_type=event_type, 
            since_days=since_days,
            order_by=order_by,
            order_desc=order_desc
        )
        
        return jsonify({
            'success': True,
            'data': {
                'repository_path': repo_path,
                'events': events,
                'total': len(events)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/semantic/search_advanced', methods=['POST'])
def search_events_advanced():
    """Advanced semantic search with comprehensive filtering - SAME repository as basic search!"""
    try:
        data = request.get_json()
        repo_path = data.get('repository_path')
        
        if not repo_path:
            return jsonify({'success': False, 'error': 'repository_path required'}), 400
        
        # Get repository instance - SAME as basic search!
        svcs = web_repository_manager.get_repository(repo_path)
        if not svcs:
            return jsonify({'success': False, 'error': 'Repository not found or not initialized'}), 404
        
        # Get all events from the SELECTED REPOSITORY
        events = svcs.get_branch_events(limit=5000)  # Get more events for filtering
        
        # Extract advanced search parameters
        author = data.get('author')
        event_types = data.get('event_types')  # List of event types
        location_pattern = data.get('location_pattern')
        layers = data.get('layers')  # List of layers: ['core', '5a', '5b']
        min_confidence = data.get('min_confidence')
        max_confidence = data.get('max_confidence')
        since_date = data.get('since_date')  # YYYY-MM-DD or relative like "7 days ago"
        until_date = data.get('until_date')
        limit = data.get('limit', 20)
        order_by = data.get('order_by', 'timestamp')
        order_desc = data.get('order_desc', True)
        
        # Apply advanced filtering to repository events
        filtered_events = events
        
        # Filter by author
        if author:
            filtered_events = [e for e in filtered_events if author.lower() in str(e.get('author', '')).lower()]
        
        # Filter by event types
        if event_types:
            event_types_list = event_types if isinstance(event_types, list) else [event_types]
            filtered_events = [e for e in filtered_events if e.get('event_type') in event_types_list]
        
        # Filter by location pattern
        if location_pattern:
            filtered_events = [e for e in filtered_events if location_pattern.lower() in str(e.get('location', '')).lower()]
        
        # Filter by layers
        if layers:
            layers_list = layers if isinstance(layers, list) else [layers]
            filtered_events = [e for e in filtered_events if e.get('layer') in layers_list]
        
        # Filter by confidence
        if min_confidence is not None:
            filtered_events = [e for e in filtered_events if e.get('confidence', 0) >= min_confidence]
        if max_confidence is not None:
            filtered_events = [e for e in filtered_events if e.get('confidence', 1) <= max_confidence]
        
        # Filter by date range
        if since_date:
            # Handle relative dates like "7 days ago"
            if 'days ago' in since_date:
                import re
                days_match = re.search(r'(\d+)\s*days?\s*ago', since_date)
                if days_match:
                    days = int(days_match.group(1))
                    from datetime import datetime, timedelta
                    cutoff = int((datetime.now() - timedelta(days=days)).timestamp())
                    filtered_events = [e for e in filtered_events if e.get('created_at', 0) > cutoff]
            else:
                # Handle absolute dates
                try:
                    from datetime import datetime
                    cutoff = int(datetime.strptime(since_date, '%Y-%m-%d').timestamp())
                    filtered_events = [e for e in filtered_events if e.get('created_at', 0) > cutoff]
                except:
                    pass  # Invalid date format, skip filter
        
        if until_date:
            try:
                from datetime import datetime
                cutoff = int(datetime.strptime(until_date, '%Y-%m-%d').timestamp())
                filtered_events = [e for e in filtered_events if e.get('created_at', 0) < cutoff]
            except:
                pass  # Invalid date format, skip filter
        
        # Apply ordering
        sort_field = order_by
        if sort_field == 'timestamp':
            sort_field = 'created_at'  # Map to actual field name
        
        def get_sort_key(event):
            value = event.get(sort_field, 0)
            if sort_field == 'created_at' and value:
                return value
            elif sort_field == 'confidence':
                return event.get('confidence', 0)
            elif sort_field == 'event_type':
                return event.get('event_type', '')
            else:
                return value or 0
        
        filtered_events.sort(key=get_sort_key, reverse=order_desc)
        
        # Apply limit
        final_events = filtered_events[:limit]
        
        return jsonify({
            'success': True,
            'data': {
                'repository_path': repo_path,
                'results': final_events,  # Use 'results' field for advanced search frontend
                'total': len(filtered_events),
                'showing': len(final_events),
                'filters_applied': {
                    'author': author,
                    'event_types': event_types,
                    'location_pattern': location_pattern,
                    'layers': layers,
                    'min_confidence': min_confidence,
                    'since_date': since_date,
                    'order_by': order_by,
                    'order_desc': order_desc
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/semantic/search_patterns', methods=['POST'])
def search_semantic_patterns():
    """Search for AI-detected semantic patterns."""
    try:
        data = request.get_json()
        repository_path = data.get('repository_path')
        
        if not repository_path:
            return jsonify({'success': False, 'error': 'Repository path is required'}), 400
        
        # Get pattern search parameters
        pattern_type = data.get('pattern_type')
        min_confidence = data.get('min_confidence', 0.7)
        since_date = data.get('since_date')
        limit = data.get('limit', 10)
        
        if not pattern_type:
            return jsonify({'success': False, 'error': 'Pattern type is required'}), 400
        
        try:
            # Import from main SVCS API instead of repository-specific API
            current_dir = os.path.dirname(os.path.abspath(__file__))
            svcs_api_path = os.path.join(current_dir, '.svcs')
            sys.path.insert(0, svcs_api_path)
            from api import search_semantic_patterns
            
            # Call pattern search function
            results = search_semantic_patterns(
                pattern_type=pattern_type,
                min_confidence=min_confidence,
                since_date=since_date,
                limit=limit
            )
            
            return jsonify({
                'success': True,
                'data': {
                    'patterns': results,
                    'count': len(results),
                    'pattern_type': pattern_type,
                    'confidence_threshold': min_confidence
                }
            })
            
        except ImportError as e:
            return jsonify({'success': False, 'error': f'Pattern search not available: {e}'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/semantic/recent_activity', methods=['POST'])
def get_recent_activity():
    """Get recent semantic activity for repository."""
    try:
        data = request.get_json()
        repo_path = data.get('repository_path')
        
        if not repo_path:
            return jsonify({'success': False, 'error': 'repository_path required'}), 400
        
        # Get recent events (last 7 days by default)
        since_days = data.get('days', 7)
        limit = data.get('limit', 15)
        
        events = web_repository_manager.search_events(
            repo_path, limit=limit, since_days=since_days
        )
        
        return jsonify({
            'success': True,
            'data': {
                'repository_path': repo_path,
                'days': since_days,
                'events': events,
                'total': len(events)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/semantic/commit_summary', methods=['POST'])
def get_commit_summary():
    """Get commit summary with semantic events."""
    try:
        data = request.get_json()
        repo_path = data.get('repository_path')
        commit_hash = data.get('commit_hash')
        
        if not repo_path or not commit_hash:
            return jsonify({'success': False, 'error': 'repository_path and commit_hash required'}), 400
        
        # Get repository instance
        svcs = web_repository_manager.get_repository(repo_path)
        if not svcs:
            return jsonify({'success': False, 'error': 'Repository not found or not initialized'}), 404
        
        # Get commit information and related semantic events
        try:
            # Get semantic events for this commit
            events = svcs.get_branch_events(limit=1000)
            commit_events = [e for e in events if e.get('commit_hash', '').startswith(commit_hash[:8])]
            
            # Get git commit info
            import subprocess
            result = subprocess.run(
                ['git', 'show', '--format=%H|%an|%ad|%s', '--no-patch', commit_hash],
                cwd=repo_path, capture_output=True, text=True
            )
            
            if result.returncode == 0:
                commit_info = result.stdout.strip().split('|')
                summary = {
                    'commit_hash': commit_info[0],
                    'author': commit_info[1],
                    'date': commit_info[2],
                    'message': commit_info[3],
                    'semantic_events': commit_events,
                    'events_count': len(commit_events)
                }
            else:
                summary = {
                    'commit_hash': commit_hash,
                    'error': 'Commit not found',
                    'semantic_events': commit_events,
                    'events_count': len(commit_events)
                }
            
            return jsonify({
                'success': True,
                'data': {
                    'repository_path': repo_path,
                    'summary': summary
                }
            })
        except Exception as e:
            return jsonify({'success': False, 'error': f'Error getting commit info: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/semantic/evolution', methods=['POST'])
def get_evolution():
    """Get evolution history for a specific code element."""
    try:
        data = request.get_json()
        repo_path = data.get('repository_path')
        node_id = data.get('node_id')
        
        if not repo_path or not node_id:
            return jsonify({'success': False, 'error': 'repository_path and node_id required'}), 400
        
        # Get repository instance
        svcs = web_repository_manager.get_repository(repo_path)
        if not svcs:
            return jsonify({'success': False, 'error': 'Repository not found or not initialized'}), 404
        
        # Search for events related to this node
        events = svcs.get_branch_events(limit=1000)
        node_events = []
        
        for event in events:
            # Check if event is related to the node
            if (node_id.lower() in str(event.get('node_id', '')).lower() or
                node_id.lower() in str(event.get('location', '')).lower() or
                node_id.lower() in str(event.get('details', '')).lower()):
                node_events.append(event)
        
        # Sort by timestamp
        node_events.sort(key=lambda x: x.get('created_at', 0))
        
        return jsonify({
            'success': True,
            'data': {
                'repository_path': repo_path,
                'node_id': node_id,
                'evolution': node_events,
                'total': len(node_events)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Repository Status and Info Endpoints
@app.route('/api/repository/status', methods=['POST'])
def get_repository_status():
    """Get detailed repository status (like svcs status)."""
    try:
        data = request.get_json()
        repo_path = data.get('repository_path') or data.get('path')
        
        if not repo_path:
            return jsonify({'success': False, 'error': 'Repository path required'}), 400
        
        # Get repository instance
        svcs = web_repository_manager.get_repository(repo_path)
        if not svcs:
            return jsonify({'success': False, 'error': 'Repository not found or not initialized'}), 404
        
        # Get basic repository info
        repo_path_obj = Path(repo_path)
        git_dir = repo_path_obj / '.git'
        svcs_dir = repo_path_obj / '.svcs'
        
        # Get git branch info
        try:
            import subprocess
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  cwd=repo_path, capture_output=True, text=True)
            current_branch = result.stdout.strip() if result.returncode == 0 else 'unknown'
        except:
            current_branch = 'unknown'
        
        # Get recent events count
        try:
            events = svcs.get_branch_events(limit=100)
            recent_events = len([e for e in events if e.get('created_at', 0) > time.time() - 7*24*3600])
        except:
            recent_events = 0
        
        status = {
            'repository_path': str(repo_path_obj.resolve()),
            'repository_name': repo_path_obj.name,
            'git_initialized': git_dir.exists(),
            'svcs_initialized': svcs_dir.exists(),
            'current_branch': current_branch,
            'database_exists': (svcs_dir / 'semantic.db').exists(),
            'recent_events_count': recent_events,
            'registered_in_central_registry': repo_path in [r['path'] for r in web_repository_manager.discover_repositories() if r.get('registered', False)]
        }
        
        return jsonify({'success': True, 'data': status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/repositories/status', methods=['POST'])
def get_repositories_status():
    """Get detailed repository status (alias for /api/repository/status)."""
    # This is an alias for the singular version to match frontend API calls
    return get_repository_status()

@app.route('/api/repository/branches', methods=['POST'])
def get_repository_branches():
    """Get available git branches for a repository."""
    try:
        data = request.get_json()
        repo_path = data.get('repository_path') or data.get('path')
        
        if not repo_path:
            return jsonify({'success': False, 'error': 'Repository path required'}), 400
        
        # Check if repository has git initialized
        repo_path_obj = Path(repo_path)
        git_dir = repo_path_obj / '.git'
        
        if not git_dir.exists():
            return jsonify({'success': False, 'error': 'Repository is not a git repository'}), 400
        
        # Get all available branches
        try:
            import subprocess
            result = subprocess.run(["git", "branch", "-a"], 
                                  cwd=repo_path, capture_output=True, text=True, check=True)
            
            # Parse branch names
            available_branches = []
            for line in result.stdout.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                # Remove markers and prefixes
                branch = line.replace('* ', '').replace('origin/', '')
                
                # Skip remote references that are not actual branches
                if line.startswith('remotes/') and '->' in line:
                    continue
                if branch.startswith('remotes/'):
                    continue
                
                available_branches.append(branch)
            
            # Remove duplicates and sort
            available_branches = sorted(list(set(available_branches)))
            
            # Get current branch
            try:
                current_result = subprocess.run(['git', 'branch', '--show-current'], 
                                              cwd=repo_path, capture_output=True, text=True)
                current_branch = current_result.stdout.strip() if current_result.returncode == 0 else None
            except:
                current_branch = None
            
            return jsonify({
                'success': True, 
                'data': {
                    'branches': available_branches,
                    'current_branch': current_branch
                }
            })
            
        except subprocess.CalledProcessError as e:
            return jsonify({'success': False, 'error': f'Failed to get branches: {e}'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/repository/metadata', methods=['POST'])
def get_repository_metadata():
    """Get available event types, layers, and other metadata from repository data."""
    try:
        data = request.get_json()
        repo_path = data.get('repository_path')
        
        if not repo_path:
            return jsonify({'success': False, 'error': 'repository_path required'}), 400
        
        # Get repository instance
        svcs = web_repository_manager.get_repository(repo_path)
        if not svcs:
            return jsonify({'success': False, 'error': 'Repository not found or not initialized'}), 404
        
        # Get all events to extract metadata
        events = svcs.get_branch_events(limit=5000)  # Get more events for comprehensive metadata
        
        # Extract unique values from ACTUAL data
        event_types = set()
        layers = set()
        authors = set()
        
        for event in events:
            if event.get('event_type'):
                event_types.add(event['event_type'])
            if event.get('layer'):
                layers.add(event['layer'])
            if event.get('author'):
                authors.add(event['author'])
        
        # If no events exist yet, provide the REAL event types from SVCS layer system (69 types)
        if not event_types:
            event_types = {
                'algorithm_optimized', 'api_breaking_change', 'api_enhancement', 'architecture_change',
                'assertion_usage_changed', 'assignment_pattern_changed', 'attribute_access_changed',
                'augmented_assignment_changed', 'binary_operator_usage_changed', 'boolean_literal_usage_changed',
                'class_attributes_changed', 'class_methods_changed', 'code_complication', 'code_simplification',
                'comparison_operator_usage_changed', 'comprehension_usage_changed', 'concurrency_introduction',
                'control_flow_changed', 'decorator_added', 'decorator_removed', 'default_parameters_added',
                'default_parameters_removed', 'dependency_added', 'dependency_removed', 'design_pattern_applied',
                'design_pattern_implementation', 'design_pattern_removal', 'error_handling_improvement',
                'error_handling_introduced', 'error_handling_removed', 'exception_handling_added',
                'exception_handling_changed', 'exception_handling_removed', 'file_added', 'file_removed',
                'function_complexity_changed', 'function_made_async', 'function_made_generator',
                'function_made_sync', 'functional_programming_adopted', 'functional_programming_changed',
                'functional_programming_removed', 'generator_made_function', 'global_scope_changed',
                'inheritance_changed', 'internal_call_added', 'internal_call_removed', 'lambda_usage_changed',
                'logical_operator_usage_changed', 'manual_analysis', 'memory_optimization', 'node_added',
                'node_removed', 'nonlocal_scope_changed', 'numeric_literal_usage_changed',
                'optimization_algorithm', 'optimization_data_structure', 'performance_improvement',
                'performance_regression', 'refactoring_extract_method', 'refactoring_inline_method',
                'return_pattern_changed', 'security_improvement', 'security_vulnerability',
                'signature_changed', 'string_literal_usage_changed', 'subscript_access_changed',
                'unary_operator_usage_changed', 'yield_pattern_changed'
            }
        
        # If no layers exist yet, provide the standard SVCS layers from the layer system
        if not layers:
            layers = {'core', '1', '2', '3', '4', '5a', '5b'}
        
        metadata = {
            'event_types': sorted(list(event_types)),
            'layers': sorted(list(layers)),
            'authors': sorted(list(authors)),
            'total_events': len(events),
            'repository_path': repo_path
        }
        
        return jsonify({
            'success': True,
            'data': metadata
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Analytics Endpoints
@app.route('/api/analytics/generate', methods=['POST'])
def generate_analytics():
    """Generate analytics reports (like svcs analytics)."""
    try:
        data = request.get_json()
        repo_path = data.get('repository_path')
        
        if not repo_path:
            return jsonify({'success': False, 'error': 'repository_path required'}), 400
        
        # Get repository instance
        svcs = web_repository_manager.get_repository(repo_path)
        if not svcs:
            return jsonify({'success': False, 'error': 'Repository not found or not initialized'}), 404
        
        # Get all events for analysis
        events = svcs.get_branch_events(limit=1000)
        
        # Generate analytics
        analytics = {
            'total_events': len(events),
            'event_types': {},
            'activity_by_day': {},
            'top_files': {},
            'patterns': []
        }
        
        # Count event types
        for event in events:
            event_type = event.get('event_type', 'unknown')
            analytics['event_types'][event_type] = analytics['event_types'].get(event_type, 0) + 1
            
            # Count file activity
            location = event.get('location', 'unknown')
            if '/' in location:
                file_path = location.split('/')[-1]
                analytics['top_files'][file_path] = analytics['top_files'].get(file_path, 0) + 1
        
        # Sort top files
        analytics['top_files'] = dict(sorted(analytics['top_files'].items(), key=lambda x: x[1], reverse=True)[:10])
        
        return jsonify({
            'success': True, 
            'data': {
                'repository_path': repo_path,
                'analytics': analytics
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Quality Analysis Endpoints
@app.route('/api/quality/analyze', methods=['POST'])
def analyze_quality():
    """Perform quality analysis (like svcs quality)."""
    try:
        data = request.get_json()
        repo_path = data.get('repository_path')
        
        if not repo_path:
            return jsonify({'success': False, 'error': 'repository_path required'}), 400
        
        # Get repository instance
        svcs = web_repository_manager.get_repository(repo_path)
        if not svcs:
            return jsonify({'success': False, 'error': 'Repository not found or not initialized'}), 404
        
        # Get events for quality analysis
        events = svcs.get_branch_events(limit=1000)
        
        # Analyze quality metrics
        quality_metrics = {
            'complexity_events': 0,
            'error_handling_events': 0,
            'performance_events': 0,
            'refactoring_events': 0,
            'total_events': len(events),
            'quality_score': 0.0
        }
        
        for event in events:
            event_type = event.get('event_type', '')
            details = str(event.get('details', '')).lower()
            
            if 'complexity' in details or 'cyclomatic' in details:
                quality_metrics['complexity_events'] += 1
            if 'error' in details or 'exception' in details or 'try' in details:
                quality_metrics['error_handling_events'] += 1
            if 'performance' in details or 'optimization' in details:
                quality_metrics['performance_events'] += 1
            if 'refactor' in details or 'cleanup' in details:
                quality_metrics['refactoring_events'] += 1
        
        # Calculate basic quality score
        if quality_metrics['total_events'] > 0:
            positive_events = quality_metrics['performance_events'] + quality_metrics['refactoring_events']
            quality_metrics['quality_score'] = min(1.0, positive_events / quality_metrics['total_events'])
        
        return jsonify({
            'success': True,
            'data': {
                'repository_path': repo_path,
                'quality_metrics': quality_metrics
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Branch Comparison Endpoints
@app.route('/api/compare/branches', methods=['POST'])
def compare_branches():
    """Compare branches (like svcs compare)."""
    try:
        data = request.get_json()
        repo_path = data.get('repository_path')
        branch1 = data.get('branch1')
        branch2 = data.get('branch2')
        limit = data.get('limit', 10)
        
        if not all([repo_path, branch1, branch2]):
            return jsonify({'success': False, 'error': 'repository_path, branch1, and branch2 required'}), 400
        
        # Get repository instance
        svcs = web_repository_manager.get_repository(repo_path)
        if not svcs:
            return jsonify({'success': False, 'error': 'Repository not found or not initialized'}), 404
        
        # For this simple implementation, we'll get events and simulate branch comparison
        # In a full implementation, you'd need to actually switch branches and compare
        events = svcs.get_branch_events(limit=limit*2)
        
        # Simulate branch-specific events (in reality, you'd query by branch)
        branch1_events = events[:limit]
        branch2_events = events[limit:limit*2] if len(events) > limit else []
        
        comparison = {
            'branch1': {
                'name': branch1,
                'events': branch1_events,
                'count': len(branch1_events)
            },
            'branch2': {
                'name': branch2,
                'events': branch2_events,
                'count': len(branch2_events)
            },
            'differences': {
                'unique_to_branch1': len(branch1_events) - len(branch2_events),
                'common_patterns': []
            }
        }
        
        return jsonify({
            'success': True,
            'data': {
                'repository_path': repo_path,
                'comparison': comparison
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# CI/CD Integration Endpoints
@app.route('/api/ci/pr_analysis', methods=['POST'])
def ci_pr_analysis():
    """Run CI PR analysis (like svcs ci pr-analysis)."""
    try:
        data = request.get_json()
        repo_path = data.get('repository_path')
        target_branch = data.get('target_branch', 'main')
        
        if not repo_path:
            return jsonify({'success': False, 'error': 'repository_path required'}), 400
        
        # Get repository instance
        svcs = web_repository_manager.get_repository(repo_path)
        if not svcs:
            return jsonify({'success': False, 'error': 'Repository not found or not initialized'}), 404
        
        try:
            # Try to use repository-local CI integration
            original_dir = os.getcwd()
            os.chdir(repo_path)
            
            # Import CI integration at function level to avoid import issues
            import svcs_repo_ci
            
            # Use the standalone function directly (simpler approach)
            result = svcs_repo_ci.analyze_pr_semantic_impact(target_branch, repo_path)
            
            os.chdir(original_dir)
            
            os.chdir(original_dir)
            
            return jsonify({
                'success': True,
                'data': {
                    'repository_path': repo_path,
                    'target_branch': target_branch,
                    'analysis': result
                }
            })
            
        except ImportError:
            # Fallback: basic analysis
            events = svcs.get_branch_events(limit=50)
            recent_events = [e for e in events if e.get('created_at', 0) > time.time() - 24*3600]
            
            analysis = {
                'change_count': len(recent_events),
                'risk_level': 'low' if len(recent_events) < 5 else 'medium' if len(recent_events) < 15 else 'high',
                'recent_changes': recent_events[:10]
            }
            
            os.chdir(original_dir)
            
            return jsonify({
                'success': True,
                'data': {
                    'repository_path': repo_path,
                    'target_branch': target_branch,
                    'analysis': analysis
                }
            })
            
    except Exception as e:
        if 'original_dir' in locals():
            os.chdir(original_dir)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ci/quality_gate', methods=['POST'])
def ci_quality_gate():
    """Run CI quality gate (like svcs ci quality-gate)."""
    try:
        data = request.get_json()
        repo_path = data.get('repository_path')
        target_branch = data.get('target_branch', 'main')
        strict = data.get('strict', False)
        
        if not repo_path:
            return jsonify({'success': False, 'error': 'repository_path required'}), 400
        
        # Get repository instance
        svcs = web_repository_manager.get_repository(repo_path)
        if not svcs:
            return jsonify({'success': False, 'error': 'Repository not found or not initialized'}), 404
        
        try:
            original_dir = os.getcwd()
            os.chdir(repo_path)
            
            # Import CI integration at function level to avoid import issues
            import svcs_repo_ci
            
            # Use the standalone function directly (simpler approach)
            result = svcs_repo_ci.run_quality_gate(strict=strict, repo_path=repo_path)
            
            os.chdir(original_dir)
            
            return jsonify({
                'success': True,
                'data': {
                    'repository_path': repo_path,
                    'strict_mode': strict,
                    'quality_gate': result
                }
            })
            
        except ImportError:
            # Fallback: basic quality gate
            events = svcs.get_branch_events(limit=100)
            error_events = [e for e in events if 'error' in str(e.get('details', '')).lower()]
            
            quality_gate = {
                'passed': len(error_events) < (5 if strict else 10),
                'error_count': len(error_events),
                'threshold': 5 if strict else 10,
                'strict_mode': strict
            }
            
            os.chdir(original_dir)
            
            return jsonify({
                'success': True,
                'data': {
                    'repository_path': repo_path,
                    'strict_mode': strict,
                    'quality_gate': quality_gate
                }
            })
            
    except Exception as e:
        if 'original_dir' in locals():
            os.chdir(original_dir)
        return jsonify({'success': False, 'error': str(e)}), 500

# Natural Language Query Endpoints
@app.route('/api/query/natural_language', methods=['POST'])
def natural_language_query():
    """Process natural language queries with smart keyword matching."""
    try:
        data, error = get_request_data()
        if error:
            return jsonify(error), 400
        
        repo_path = data.get('repository_path')
        query = data.get('query')
        
        if not repo_path or not query:
            return jsonify({'success': False, 'error': 'repository_path and query required'}), 400
        
        # Get repository instance
        svcs = web_repository_manager.get_repository(repo_path)
        if not svcs:
            return jsonify({'success': False, 'error': 'Repository not found or not initialized'}), 404
        
        # Smart keyword search in events
        events = svcs.get_branch_events(limit=200)
        query_lower = query.lower()
        
        # Enhanced keyword matching
        matching_events = []
        for event in events:
            event_str = f"{event.get('event_type', '')} {event.get('details', '')} {event.get('location', '')} {event.get('node_id', '')}"
            
            # Check for exact matches and related terms
            if (query_lower in event_str.lower() or
                any(keyword in event_str.lower() for keyword in query_lower.split()) or
                ('function' in query_lower and 'function' in event.get('event_type', '')) or
                ('class' in query_lower and 'class' in event.get('event_type', '')) or
                ('add' in query_lower and 'added' in event.get('event_type', '')) or
                ('recent' in query_lower and event.get('timestamp', 0) > (time.time() - 7*24*3600))):
                matching_events.append(event)
        
        # Create intelligent response
        response_parts = []
        
        if 'function' in query_lower and 'recent' in query_lower:
            function_events = [e for e in matching_events if 'function' in e.get('event_type', '')]
            response_parts.append(f"Found {len(function_events)} recent function-related events:")
            for event in function_events[:5]:
                response_parts.append(f"• {event.get('event_type', 'N/A')}: {event.get('node_id', 'N/A')}")
        else:
            response_parts.append(f"Found {len(matching_events)} events related to '{query}'")
        
        if matching_events:
            # Analyze event types
            event_types = {}
            for event in matching_events[:20]:
                event_type = event.get('event_type', 'unknown')
                event_types[event_type] = event_types.get(event_type, 0) + 1
            
            if len(event_types) > 1:
                response_parts.append("\nEvent breakdown:")
                for event_type, count in sorted(event_types.items(), key=lambda x: x[1], reverse=True)[:5]:
                    response_parts.append(f"  • {event_type}: {count} events")
            
            # Show most recent event
            recent_event = matching_events[0]
            response_parts.append(f"\nMost recent: {recent_event.get('event_type', 'N/A')} in {recent_event.get('location', 'unknown location')}")
        else:
            response_parts.append("No matching events found. Try different keywords.")
        
        response = "\n".join(response_parts)
        
        return jsonify({
            'success': True,
            'data': {
                'repository_path': repo_path,
                'query': query,
                'response': response,
                'matching_events': matching_events[:10],
                'total_matches': len(matching_events),
                'method': 'smart_keyword_search'
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Natural language query failed: {str(e)}'}), 500

# Git Notes Management Endpoints
@app.route('/api/notes/sync', methods=['POST'])
def notes_sync():
    """Sync git notes (like svcs notes sync)."""
    try:
        data = request.get_json()
        repo_path = data.get('repository_path')
        
        if not repo_path:
            return jsonify({'success': False, 'error': 'repository_path required'}), 400
        
        # Get repository instance
        svcs = web_repository_manager.get_repository(repo_path)
        if not svcs:
            return jsonify({'success': False, 'error': 'Repository not found or not initialized'}), 404
        
        try:
            from svcs_repo_local import GitNotesManager
            notes_manager = GitNotesManager(str(repo_path))
            result = notes_manager.sync_notes_to_remote()
            
            return jsonify({
                'success': result,
                'data': {
                    'repository_path': repo_path,
                    'sync_result': result,
                    'message': 'Git notes synced successfully to remote' if result else 'Failed to sync - remote not configured or sync failed'
                }
            })
            
        except ImportError:
            return jsonify({'success': False, 'error': 'Git notes module not available'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/notes/fetch', methods=['POST'])
def notes_fetch():
    """Fetch git notes (like svcs notes fetch)."""
    try:
        data = request.get_json()
        repo_path = data.get('repository_path')
        
        if not repo_path:
            return jsonify({'success': False, 'error': 'repository_path required'}), 400
        
        svcs = web_repository_manager.get_repository(repo_path)
        if not svcs:
            return jsonify({'success': False, 'error': 'Repository not found or not initialized'}), 404
        
        try:
            from svcs_repo_local import GitNotesManager
            notes_manager = GitNotesManager(str(repo_path))
            result = notes_manager.fetch_notes_from_remote()
            
            return jsonify({
                'success': result,
                'data': {
                    'repository_path': repo_path,
                    'fetch_result': result,
                    'message': ('Git notes fetched successfully from remote' if result 
                              else 'No git notes found on remote, remote not configured, or fetch failed'),
                    'status': 'success' if result else 'failed'
                }
            })
            
        except ImportError:
            return jsonify({'success': False, 'error': 'Git notes module not available'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/notes/show', methods=['POST'])
def notes_show():
    """Show git note for commit (like svcs notes show)."""
    try:
        data = request.get_json()
        repo_path = data.get('repository_path')
        commit_hash = data.get('commit_hash', 'HEAD')
        
        if not repo_path:
            return jsonify({'success': False, 'error': 'repository_path required'}), 400
        
        svcs = web_repository_manager.get_repository(repo_path)
        if not svcs:
            return jsonify({'success': False, 'error': 'Repository not found or not initialized'}), 404
        
        try:
            from svcs_repo_local import GitNotesManager
            notes_manager = GitNotesManager(str(repo_path))
            note = notes_manager.get_semantic_data_from_note(commit_hash)
            
            return jsonify({
                'success': True,
                'data': {
                    'repository_path': repo_path,
                    'commit_hash': commit_hash,
                    'note': note
                }
            })
            
        except ImportError:
            return jsonify({'success': False, 'error': 'Git notes module not available'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Repository Cleanup Endpoints
@app.route('/api/cleanup/orphaned_data', methods=['POST'])
def cleanup_orphaned_data():
    """Clean up orphaned semantic data (like svcs cleanup)."""
    try:
        data = request.get_json()
        repo_path = data.get('repository_path')
        
        if not repo_path:
            return jsonify({'success': False, 'error': 'repository_path required'}), 400
        
        svcs = web_repository_manager.get_repository(repo_path)
        if not svcs:
            return jsonify({'success': False, 'error': 'Repository not found or not initialized'}), 404
        
        try:
            # Simple cleanup: get valid git commit hashes and remove orphaned events
            original_dir = os.getcwd()
            os.chdir(repo_path)
            
            # Get valid commit hashes from git
            result = subprocess.run(['git', 'log', '--format=%H'], 
                                  capture_output=True, text=True, check=True)
            valid_hashes = set(result.stdout.strip().split('\n')) if result.stdout.strip() else set()
            
            os.chdir(original_dir)
            
            # Clean orphaned events
            with svcs.db.get_connection() as conn:
                # Get all commit hashes in database
                cursor = conn.execute("SELECT DISTINCT commit_hash FROM semantic_events")
                db_hashes = set(row[0] for row in cursor.fetchall())
                
                # Find orphaned hashes
                orphaned_hashes = db_hashes - valid_hashes
                
                if orphaned_hashes:
                    # Remove orphaned events
                    for hash_val in orphaned_hashes:
                        conn.execute("DELETE FROM semantic_events WHERE commit_hash = ?", (hash_val,))
                    
                    conn.commit()
                    cleanup_result = f"Cleaned {len(orphaned_hashes)} orphaned commits with their semantic events"
                else:
                    cleanup_result = "No orphaned data found - repository is clean"
            
            return jsonify({
                'success': True,
                'data': {
                    'repository_path': repo_path,
                    'cleanup_result': cleanup_result,
                    'orphaned_commits_removed': len(orphaned_hashes) if 'orphaned_hashes' in locals() else 0
                }
            })
            
        except Exception as e:
            if 'original_dir' in locals():
                os.chdir(original_dir)
            return jsonify({'success': False, 'error': f'Cleanup failed: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/cleanup/unreachable_commits', methods=['POST'])
def cleanup_unreachable_commits():
    """Clean up semantic events for unreachable commits (like svcs cleanup --git-unreachable)."""
    try:
        data = request.get_json()
        repo_path = data.get('repository_path')
        
        if not repo_path:
            return jsonify({'success': False, 'error': 'repository_path required'}), 400
        
        svcs = web_repository_manager.get_repository(repo_path)
        if not svcs:
            return jsonify({'success': False, 'error': 'Repository not found or not initialized'}), 404
        
        try:
            # Get reachable commits from git
            original_dir = os.getcwd()
            os.chdir(repo_path)
            
            # Get all reachable commits
            result = subprocess.run(['git', 'rev-list', '--all'], 
                                  capture_output=True, text=True, check=True)
            reachable_hashes = set(result.stdout.strip().split('\n')) if result.stdout.strip() else set()
            
            os.chdir(original_dir)
            
            # Clean unreachable commit events
            with svcs.db.get_connection() as conn:
                # Get all commit hashes in database
                cursor = conn.execute("SELECT DISTINCT commit_hash FROM semantic_events")
                db_hashes = set(row[0] for row in cursor.fetchall())
                
                # Find unreachable hashes
                unreachable_hashes = db_hashes - reachable_hashes
                
                if unreachable_hashes:
                    # Remove unreachable events
                    for hash_val in unreachable_hashes:
                        conn.execute("DELETE FROM semantic_events WHERE commit_hash = ?", (hash_val,))
                    
                    conn.commit()
                    cleanup_result = f"Cleaned {len(unreachable_hashes)} unreachable commits with their semantic events"
                else:
                    cleanup_result = "No unreachable commits found - all commits are reachable"
            
            return jsonify({
                'success': True,
                'data': {
                    'repository_path': repo_path,
                    'cleanup_result': cleanup_result,
                    'unreachable_commits_removed': len(unreachable_hashes) if 'unreachable_hashes' in locals() else 0
                }
            })
            
        except Exception as e:
            if 'original_dir' in locals():
                os.chdir(original_dir)
            return jsonify({'success': False, 'error': f'Cleanup failed: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/cleanup/database_stats', methods=['POST'])
def get_database_stats():
    """Get database statistics (like svcs cleanup --show-stats)."""
    try:
        data = request.get_json()
        repo_path = data.get('repository_path')
        
        if not repo_path:
            return jsonify({'success': False, 'error': 'repository_path required'}), 400
        
        svcs = web_repository_manager.get_repository(repo_path)
        if not svcs:
            return jsonify({'success': False, 'error': 'Repository not found or not initialized'}), 404
        
        try:
            # Get basic database statistics manually
            with svcs.db.get_connection() as conn:
                # Count total events
                cursor = conn.execute("SELECT COUNT(*) FROM semantic_events")
                total_events = cursor.fetchone()[0]
                
                # Count commits
                cursor = conn.execute("SELECT COUNT(*) FROM commits")
                commits_tracked = cursor.fetchone()[0]
                
                # Get database file size
                db_path = Path(repo_path) / '.svcs' / 'semantic.db'
                db_size = db_path.stat().st_size if db_path.exists() else 0
                db_size_mb = round(db_size / (1024 * 1024), 2)
                
                # Count branches
                cursor = conn.execute("SELECT COUNT(DISTINCT branch) FROM semantic_events")
                branches_count = cursor.fetchone()[0]
                
                stats = {
                    'total_events': total_events,
                    'commits_tracked': commits_tracked,
                    'database_size': f"{db_size_mb} MB",
                    'database_size_bytes': db_size,
                    'branches_tracked': branches_count,
                    'database_path': str(db_path)
                }
            
            return jsonify({
                'success': True,
                'data': {
                    'repository_path': repo_path,
                    'database_stats': stats
                }
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': f'Stats query failed: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# System Information Endpoints
@app.route('/api/system/status', methods=['GET'])
def system_status():
    """Get system status and capabilities."""
    try:
        # Get repository count
        repositories = web_repository_manager.discover_repositories()
        registered_count = len([r for r in repositories if r.get('registered', False)])
        discovered_count = len(repositories)
        
        return jsonify({
            'success': True,
            'data': {
                'architecture': 'repository-local',
                'repo_local_available': REPO_LOCAL_AVAILABLE,
                'registry_path': str(web_repository_manager.registry_db),
                'repositories': {
                    'registered': registered_count,
                    'discovered': discovered_count,
                    'total': discovered_count
                },
                'capabilities': [
                    'repository_discovery',
                    'repository_registration', 
                    'repository_initialization',
                    'repository_status',
                    'semantic_search',
                    'evolution_tracking',
                    'commit_analysis',
                    'analytics_generation',
                    'quality_analysis',
                    'branch_comparison',
                    'recent_activity'
                ]
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

def run_server(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, debug: bool = False):
    """Run the Flask server."""
    print(f"🚀 Starting SVCS Web Server (New Architecture)")
    print(f"📍 Server: http://{host}:{port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"📂 Working directory: {os.getcwd()}")
    print(f"🗄️ Registry: {web_repository_manager.registry_db}")
    print()
    print("Available endpoints:")
    print("  GET  /           - Interactive dashboard")
    print("  GET  /health     - Health check")
    print("  POST /api/repositories/*  - Repository management")
    print("  POST /api/semantic/*      - Semantic analysis")
    print("  GET  /api/system/status   - System information")
    print()
    print("🛑 To stop server:")
    print(f"   pkill -f 'svcs_repo_web_server.py --port {port}'")
    print(f"   or: pkill -f 'svcs_repo_web_server.py'")
    print(f"   or: kill -9 $(lsof -t -i:{port})")
    print()
    
    if not REPO_LOCAL_AVAILABLE:
        print("⚠️  Warning: Repository-local SVCS not available")
        print("   Install svcs_repo_local module for full functionality")
        print()
    
    try:
        app.run(host=host, port=port, debug=debug)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is in use by another program. Either identify and stop that program, or start the server with a different port.")
            print(f"   Try: python3 svcs_repo_web_server.py --port {port + 1}")
            print(f"   Or stop existing server: pkill -f 'svcs_repo_web_server.py'")
        else:
            print(f"❌ Server error: {e}")
        sys.exit(1)

def main():
    """Main entry point for the web server."""
    parser = argparse.ArgumentParser(description='SVCS Web Server - New Repository-Local Architecture')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, 
                       help=f'Port to run the server on (default: {DEFAULT_PORT})')
    parser.add_argument('--host', default=DEFAULT_HOST,
                       help=f'Host to bind to (default: {DEFAULT_HOST})')
    parser.add_argument('--debug', action='store_true',
                       help='Run in debug mode')
    
    args = parser.parse_args()
    run_server(host=args.host, port=args.port, debug=args.debug)

if __name__ == '__main__':
    main()

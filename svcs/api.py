# FILE: svcs/api.py
#
# Core SVCS API functions
# This file provides the centralized API for all SVCS functionality
# Used by CLI commands, conversational interface, and other tools

import os
import sys
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

# --- Configuration ---
SVCS_DIR = ".svcs"
# Use the new repository-local database path
DB_PATH = os.path.join(SVCS_DIR, "semantic.db")

def _get_db_connection():
    """Establishes a connection to the SQLite database."""
    # Try the new database first, then fall back to legacy
    new_db_path = os.path.join(SVCS_DIR, "semantic.db")
    legacy_db_path = os.path.join(SVCS_DIR, "history.db")
    
    if os.path.exists(new_db_path):
        db_path = new_db_path
    elif os.path.exists(legacy_db_path):
        db_path = legacy_db_path
    else:
        raise FileNotFoundError(f"SVCS database not found. Looked for '{new_db_path}' or '{legacy_db_path}'.")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def _execute_query(query, params=()):
    """A helper function to execute a query and return results."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results]

def get_valid_commit_hashes():
    """Returns a set of all commit hashes currently in the Git history."""
    try:
        cmd = ["git", "log", "--format=%H"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return set(result.stdout.strip().split('\n'))
    except subprocess.CalledProcessError:
        return set()

# --- Core API Functions ---

def get_full_log():
    """
    Fetches the entire log of all semantic events, including commit metadata.
    Use this for broad questions about the project history as a whole.
    """
    query = """
        SELECT
            e.event_id, e.commit_hash, e.event_type, e.node_id, e.location, e.details,
            e.layer, e.layer_description, e.confidence, e.reasoning, e.impact,
            c.author, c.branch, c.timestamp
        FROM semantic_events e
        JOIN commits c ON e.commit_hash = c.commit_hash
        ORDER BY c.timestamp DESC
    """
    return _execute_query(query)

def search_events(author=None, event_type=None, node_id=None, location=None):
    """Generic search for events, now including commit metadata. Primarily for the CLI."""
    if not any([author, event_type, node_id, location]):
        raise ValueError("At least one search criterion must be provided.")
    
    query_parts = []
    params = []
    base_query = """
        SELECT
            e.event_id, e.commit_hash, e.event_type, e.node_id, e.location, e.details,
            e.layer, e.layer_description, e.confidence, e.reasoning, e.impact,
            c.author, c.branch, c.timestamp
        FROM semantic_events e
        JOIN commits c ON e.commit_hash = c.commit_hash
        WHERE
    """
    
    if author:
        query_parts.append("c.author LIKE ?")
        params.append(f"%{author}%")
    if event_type:
        query_parts.append("e.event_type = ?")
        params.append(event_type)
    if node_id:
        query_parts.append("e.node_id = ?")
        params.append(node_id)
    if location:
        query_parts.append("e.location LIKE ?")
        params.append(f"%{location}%")
    
    final_query = base_query + " AND ".join(query_parts) + " ORDER BY c.timestamp DESC"
    return _execute_query(final_query, params)

def get_node_evolution(node_id: str):
    """
    Retrieves the evolution history of a specific function, class, or module.
    Use this to understand how a particular code element has changed over time.
    """
    query = """
        SELECT
            e.event_id, e.commit_hash, e.event_type, e.node_id, e.location, e.details,
            e.layer, e.layer_description, e.confidence, e.reasoning, e.impact,
            c.author, c.branch, c.timestamp
        FROM semantic_events e
        JOIN commits c ON e.commit_hash = c.commit_hash
        WHERE e.node_id = ?
        ORDER BY c.timestamp DESC
    """
    return _execute_query(query, (node_id,))

def find_dependency_changes(dependency_name: str):
    """
    Locates events related to dependency changes for a specific library or module.
    Useful for tracking when external dependencies were added, updated, or removed.
    """
    query = """
        SELECT
            e.event_id, e.commit_hash, e.event_type, e.node_id, e.location, e.details,
            e.layer, e.layer_description, e.confidence, e.reasoning, e.impact,
            c.author, c.branch, c.timestamp
        FROM semantic_events e
        JOIN commits c ON e.commit_hash = c.commit_hash
        WHERE e.details LIKE ? OR e.reasoning LIKE ?
        ORDER BY c.timestamp DESC
    """
    return _execute_query(query, (f"%{dependency_name}%", f"%{dependency_name}%"))

def get_commit_details(commit_hash: str):
    """
    Fetches semantic events associated with a specific commit.
    Use this to understand the semantic impact of a particular commit.
    """
    query = """
        SELECT
            e.event_id, e.commit_hash, e.event_type, e.node_id, e.location, e.details,
            e.layer, e.layer_description, e.confidence, e.reasoning, e.impact,
            c.author, c.branch, c.timestamp
        FROM semantic_events e
        JOIN commits c ON e.commit_hash = c.commit_hash
        WHERE e.commit_hash = ?
        ORDER BY e.layer, e.confidence DESC
    """
    return _execute_query(query, (commit_hash,))

def _parse_relative_date(date_str):
    """Parse relative date strings like '1 week ago' or '3 days ago'."""
    if not date_str:
        return None
    
    try:
        # Try to parse as absolute date first
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        pass
    
    # Parse relative dates
    parts = date_str.lower().split()
    if len(parts) >= 3 and parts[-1] == "ago":
        try:
            amount = int(parts[0])
            unit = parts[1].rstrip('s')  # Remove plural 's'
            
            now = datetime.now()
            if unit in ['day', 'days']:
                return now - timedelta(days=amount)
            elif unit in ['week', 'weeks']:
                return now - timedelta(weeks=amount)
            elif unit in ['month', 'months']:
                return now - timedelta(days=amount * 30)  # Approximate
            elif unit in ['year', 'years']:
                return now - timedelta(days=amount * 365)  # Approximate
        except (ValueError, IndexError):
            pass
    
    # Handle special cases
    if date_str.lower() == "yesterday":
        return datetime.now() - timedelta(days=1)
    elif date_str.lower() == "today":
        return datetime.now()
    
    return None

def search_events_advanced(
    event_types=None,
    layers=None,
    author=None,
    location_pattern=None,
    since_date=None,
    min_confidence=None,
    limit=20,
    order_by="timestamp",
    order_desc=True
):
    """
    Advanced search with comprehensive filtering options.
    
    Args:
        event_types: List of event types to filter by
        layers: List of layers to filter by
        author: Author name to filter by
        location_pattern: Location pattern to match
        since_date: Date string (YYYY-MM-DD or relative like '1 week ago')
        min_confidence: Minimum confidence threshold
        limit: Maximum number of results
        order_by: Field to order by
        order_desc: Whether to order in descending order
    
    Returns:
        List of matching semantic events
    """
    
    base_query = """
        SELECT
            e.event_id, e.commit_hash, e.event_type, e.node_id, e.location, e.details,
            e.layer, e.layer_description, e.confidence, e.reasoning, e.impact,
            c.author, c.branch, c.timestamp
        FROM semantic_events e
        JOIN commits c ON e.commit_hash = c.commit_hash
    """
    
    conditions = []
    params = []
    
    if event_types:
        placeholders = ','.join(['?' for _ in event_types])
        conditions.append(f"e.event_type IN ({placeholders})")
        params.extend(event_types)
    
    if layers:
        placeholders = ','.join(['?' for _ in layers])
        conditions.append(f"e.layer IN ({placeholders})")
        params.extend(layers)
    
    if author:
        conditions.append("c.author LIKE ?")
        params.append(f"%{author}%")
    
    if location_pattern:
        conditions.append("e.location LIKE ?")
        params.append(f"%{location_pattern}%")
    
    if since_date:
        parsed_date = _parse_relative_date(since_date)
        if parsed_date:
            conditions.append("c.timestamp >= ?")
            params.append(int(parsed_date.timestamp()))
    
    if min_confidence is not None:
        conditions.append("e.confidence >= ?")
        params.append(min_confidence)
    
    # Add WHERE clause if there are conditions
    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)
    
    # Add ORDER BY
    order_direction = "DESC" if order_desc else "ASC"
    if order_by == "timestamp":
        base_query += f" ORDER BY c.timestamp {order_direction}"
    else:
        base_query += f" ORDER BY e.{order_by} {order_direction}, c.timestamp {order_direction}"
    
    # Add LIMIT
    if limit:
        base_query += " LIMIT ?"
        params.append(limit)
    
    return _execute_query(base_query, params)

def get_recent_activity(
    days=7,
    author=None,
    layers=None,
    limit=15
):
    """
    Get recent project activity with filtering options.
    
    Args:
        days: Number of days to look back (default 7)
        author: Optional author filter
        layers: Optional list of layer filters
        limit: Maximum number of results (default 15)
    
    Returns:
        List of recent semantic events
    """
    
    since_date = datetime.now() - timedelta(days=days)
    
    return search_events_advanced(
        layers=layers,
        author=author,
        since_date=since_date.strftime("%Y-%m-%d"),
        limit=limit
    )

def get_project_statistics():
    """
    Get semantic statistics for the project.
    
    Returns:
        List of statistics about semantic events
    """
    
    queries = {
        "total_events": "SELECT COUNT(*) as count FROM semantic_events",
        "events_by_type": """
            SELECT event_type, COUNT(*) as count 
            FROM semantic_events 
            GROUP BY event_type 
            ORDER BY count DESC
        """,
        "events_by_layer": """
            SELECT layer, COUNT(*) as count 
            FROM semantic_events 
            GROUP BY layer 
            ORDER BY count DESC
        """,
        "events_by_author": """
            SELECT c.author, COUNT(*) as count 
            FROM semantic_events e
            JOIN commits c ON e.commit_hash = c.commit_hash
            GROUP BY c.author 
            ORDER BY count DESC
        """,
        "avg_confidence": "SELECT AVG(confidence) as avg_confidence FROM semantic_events"
    }
    
    results = []
    for stat_name, query in queries.items():
        try:
            result = _execute_query(query)
            results.append({"statistic": stat_name, "data": result})
        except Exception as e:
            results.append({"statistic": stat_name, "error": str(e)})
    
    return results

def search_semantic_patterns(
    pattern_type,
    min_confidence=0.7,
    since_date=None,
    limit=10
):
    """
    Search for specific AI-detected semantic patterns.
    
    Args:
        pattern_type: Pattern type (performance, architecture, error_handling, etc.)
        min_confidence: Minimum confidence threshold (default 0.7)
        since_date: Optional date filter (YYYY-MM-DD or relative)
        limit: Maximum number of results (default 10)
    
    Returns:
        List of matching semantic patterns
    """
    
    # Map pattern types to search terms
    pattern_mappings = {
        "performance": ["performance", "optimization", "speed", "efficiency"],
        "architecture": ["architecture", "design", "pattern", "structure"],
        "error_handling": ["error", "exception", "handling", "try", "catch"],
        "refactoring": ["refactor", "cleanup", "reorganize", "restructure"],
        "security": ["security", "authentication", "authorization", "validation"],
        "testing": ["test", "testing", "unit", "integration", "mock"],
        "documentation": ["documentation", "comment", "docstring", "readme"]
    }
    
    search_terms = pattern_mappings.get(pattern_type, [pattern_type])
    
    # Build query to search in details and reasoning
    conditions = []
    params = []
    
    # Search for pattern in details or reasoning
    pattern_conditions = []
    for term in search_terms:
        pattern_conditions.append("(e.details LIKE ? OR e.reasoning LIKE ?)")
        params.extend([f"%{term}%", f"%{term}%"])
    
    if pattern_conditions:
        conditions.append("(" + " OR ".join(pattern_conditions) + ")")
    
    # Add confidence filter
    if min_confidence is not None:
        conditions.append("e.confidence >= ?")
        params.append(min_confidence)
    
    # Add date filter
    if since_date:
        parsed_date = _parse_relative_date(since_date)
        if parsed_date:
            conditions.append("c.timestamp >= ?")
            params.append(int(parsed_date.timestamp()))
    
    query = """
        SELECT
            e.event_id, e.commit_hash, e.event_type, e.node_id, e.location, e.details,
            e.layer, e.layer_description, e.confidence, e.reasoning, e.impact,
            c.author, c.branch, c.timestamp
        FROM semantic_events e
        JOIN commits c ON e.commit_hash = c.commit_hash
    """
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY e.confidence DESC, c.timestamp DESC"
    
    if limit:
        query += " LIMIT ?"
        params.append(limit)
    
    return _execute_query(query, params)

def get_filtered_evolution(
    node_id,
    event_types=None,
    min_confidence=0.0,
    since_date=None
):
    """
    Get filtered evolution history for a specific node/function.
    
    Args:
        node_id: Node ID (e.g., "func:function_name")
        event_types: Optional list of event types to filter by
        min_confidence: Minimum confidence threshold (default 0.0)
        since_date: Optional date filter (YYYY-MM-DD or relative)
    
    Returns:
        List of filtered evolution events
    """
    
    conditions = ["e.node_id = ?"]
    params = [node_id]
    
    if event_types:
        placeholders = ','.join(['?' for _ in event_types])
        conditions.append(f"e.event_type IN ({placeholders})")
        params.extend(event_types)
    
    if min_confidence > 0:
        conditions.append("e.confidence >= ?")
        params.append(min_confidence)
    
    if since_date:
        parsed_date = _parse_relative_date(since_date)
        if parsed_date:
            conditions.append("c.timestamp >= ?")
            params.append(int(parsed_date.timestamp()))
    
    query = """
        SELECT
            e.event_id, e.commit_hash, e.event_type, e.node_id, e.location, e.details,
            e.layer, e.layer_description, e.confidence, e.reasoning, e.impact,
            c.author, c.branch, c.timestamp
        FROM semantic_events e
        JOIN commits c ON e.commit_hash = c.commit_hash
        WHERE """ + " AND ".join(conditions) + """
        ORDER BY c.timestamp ASC
    """
    
    return _execute_query(query, params)

def debug_query_tools(project_path=None, query_description="unspecified query"):
    """
    Diagnostic information for debugging query issues.
    
    Args:
        project_path: Project path (ignored for local database)
        query_description: Description of the query being debugged
    
    Returns:
        Dict with diagnostic information
    """
    
    try:
        # Get basic statistics
        total_events = _execute_query("SELECT COUNT(*) as count FROM semantic_events")[0]['count']
        
        # Get recent events count
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        recent_events = _execute_query(
            "SELECT COUNT(*) as count FROM semantic_events e JOIN commits c ON e.commit_hash = c.commit_hash WHERE c.timestamp >= ?",
            (week_ago,)
        )[0]['count']
        
        # Get performance-related events
        performance_events = _execute_query(
            "SELECT COUNT(*) as count FROM semantic_events WHERE details LIKE '%performance%' OR reasoning LIKE '%performance%'"
        )[0]['count']
        
        # Get AI-related events (high confidence)
        ai_events = _execute_query(
            "SELECT COUNT(*) as count FROM semantic_events WHERE confidence > 0.8"
        )[0]['count']
        
        # Get sample event types
        event_types = _execute_query(
            "SELECT DISTINCT event_type FROM semantic_events LIMIT 10"
        )
        
        return {
            "query": query_description,
            "total_events": total_events,
            "recent_events": recent_events,
            "performance_events": performance_events,
            "ai_events": ai_events,
            "approaches": [
                "Use search_events_advanced() for flexible filtering",
                "Use get_recent_activity() for time-based queries",
                "Use search_semantic_patterns() for pattern detection",
                "Use get_filtered_evolution() for specific node tracking"
            ],
            "sample_recent_event_types": [row['event_type'] for row in event_types]
        }
        
    except Exception as e:
        return {
            "query": query_description,
            "error": str(e),
            "total_events": 0,
            "recent_events": 0,
            "performance_events": 0,
            "ai_events": 0,
            "approaches": [],
            "sample_recent_event_types": []
        }

def get_commit_changed_files(commit_hash: str):
    """
    Get the list of files that were changed in a specific commit.
    
    Args:
        commit_hash: Commit hash (full or short)
    
    Returns:
        List of changed file paths
    """
    try:
        cmd = ["git", "show", "--name-only", "--format=", commit_hash]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
        return files
    except subprocess.CalledProcessError as e:
        return []

def get_commit_diff(commit_hash: str, file_path: str = None):
    """
    Get the git diff for a specific commit, optionally filtered to a specific file.
    
    Args:
        commit_hash: Commit hash (full or short)
        file_path: Optional specific file to show diff for
    
    Returns:
        String containing the diff
    """
    try:
        cmd = ["git", "show", commit_hash]
        if file_path:
            cmd.append(file_path)
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error getting diff: {e}"

def get_commit_summary(commit_hash: str):
    """
    Get comprehensive summary of a commit including metadata, changed files, and semantic events.
    
    Args:
        commit_hash: Commit hash (full or short)
    
    Returns:
        Dict with commit summary information
    """
    try:
        # Get commit metadata
        cmd = ["git", "show", "--format=%H|%an|%ae|%ad|%s", "--no-patch", commit_hash]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        if result.stdout.strip():
            parts = result.stdout.strip().split('|')
            commit_info = {
                "hash": parts[0] if len(parts) > 0 else commit_hash,
                "author": parts[1] if len(parts) > 1 else "Unknown",
                "email": parts[2] if len(parts) > 2 else "",
                "date": parts[3] if len(parts) > 3 else "",
                "message": parts[4] if len(parts) > 4 else ""
            }
        else:
            commit_info = {"hash": commit_hash, "error": "Commit not found"}
        
        # Get changed files
        changed_files = get_commit_changed_files(commit_hash)
        
        # Get semantic events for this commit
        semantic_events = get_commit_details(commit_hash)
        
        return {
            "commit_info": commit_info,
            "changed_files": changed_files,
            "semantic_events": semantic_events,
            "file_count": len(changed_files),
            "semantic_event_count": len(semantic_events)
        }
        
    except Exception as e:
        return {
            "commit_info": {"hash": commit_hash, "error": str(e)},
            "changed_files": [],
            "semantic_events": [],
            "file_count": 0,
            "semantic_event_count": 0
        }

def compare_branches(branch1: str, branch2: str, limit: int = 100):
    """
    Compare semantic events between two branches.
    
    Args:
        branch1: First branch name
        branch2: Second branch name
        limit: Maximum number of events to return per branch
    
    Returns:
        Dict with comparison results
    """
    try:
        # Get events for each branch
        branch1_events = search_events_advanced(limit=limit)  # Current branch events
        branch2_events = search_events_advanced(limit=limit)  # Same for now since we don't have branch-specific filtering
        
        # For now, we'll return the same events for both branches since we don't have branch-specific data
        # In a full implementation, you'd filter by branch in the semantic_events table
        
        return {
            "branch1": branch1,
            "branch2": branch2,
            "branch1_count": len(branch1_events),
            "branch2_count": len(branch2_events),
            "branch1_events": branch1_events,
            "branch2_events": branch2_events,
            "comparison_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "branch1": branch1,
            "branch2": branch2,
            "branch1_count": 0,
            "branch2_count": 0,
            "branch1_events": [],
            "branch2_events": [],
            "error": str(e),
            "comparison_date": datetime.now().isoformat()
        }

def generate_analytics(
    days=30,
    output_file=None,
    format_type="dict"
):
    """
    Generate analytics reports for the repository.
    
    Args:
        days: Number of days to analyze (default 30)
        output_file: Optional file to save results
        format_type: Output format ('dict', 'json')
    
    Returns:
        Dict with analytics data
    """
    try:
        # Get date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get events in date range
        events = search_events_advanced(
            since_date=start_date.strftime("%Y-%m-%d"),
            limit=1000
        )
        
        # Calculate analytics
        total_events = len(events)
        
        # Group by event type
        event_types = {}
        for event in events:
            event_type = event.get('event_type', 'unknown')
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        # Group by author
        authors = {}
        for event in events:
            author = event.get('author', 'unknown')
            authors[author] = authors.get(author, 0) + 1
        
        # Group by layer
        layers = {}
        for event in events:
            layer = event.get('layer', 'unknown')
            layers[layer] = layers.get(layer, 0) + 1
        
        analytics = {
            "total_events": total_events,
            "date_range": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d"),
                "days": days
            },
            "event_types": event_types,
            "authors": authors,
            "layers": layers,
            "avg_confidence": sum(event.get('confidence', 0) for event in events) / max(total_events, 1)
        }
        
        # Save to file if requested
        if output_file:
            import json
            with open(output_file, 'w') as f:
                json.dump(analytics, f, indent=2)
        
        return analytics
        
    except Exception as e:
        return {
            "total_events": 0,
            "date_range": {"error": str(e)},
            "error": str(e)
        }

def analyze_quality(
    verbose=False,
    output_file=None
):
    """
    Analyze code quality trends and patterns.
    
    Args:
        verbose: Whether to include detailed analysis
        output_file: Optional file to save results
    
    Returns:
        Dict with quality analysis
    """
    try:
        # Get all events for quality analysis
        events = get_full_log()
        
        # Calculate quality metrics
        total_events = len(events)
        
        # Quality indicators
        refactoring_events = sum(1 for e in events if 'refactor' in e.get('details', '').lower())
        performance_events = sum(1 for e in events if 'performance' in e.get('details', '').lower())
        error_handling_events = sum(1 for e in events if 'error' in e.get('details', '').lower())
        
        # Calculate quality score (0-100)
        if total_events > 0:
            quality_score = min(100, (refactoring_events + performance_events + error_handling_events) * 10)
        else:
            quality_score = 0
        
        analysis = {
            "quality_score": quality_score,
            "total_events": total_events,
            "refactoring_events": refactoring_events,
            "performance_events": performance_events,
            "error_handling_events": error_handling_events,
            "analysis_date": datetime.now().isoformat()
        }
        
        if verbose:
            analysis["detailed_breakdown"] = {
                "refactoring_ratio": refactoring_events / max(total_events, 1),
                "performance_ratio": performance_events / max(total_events, 1),
                "error_handling_ratio": error_handling_events / max(total_events, 1)
            }
        
        # Save to file if requested
        if output_file:
            import json
            with open(output_file, 'w') as f:
                json.dump(analysis, f, indent=2)
        
        return analysis
        
    except Exception as e:
        return {
            "quality_score": 0,
            "analysis_date": datetime.now().isoformat(),
            "error": str(e)
        }

def get_branch_events(branch: str, limit: int = 100):
    """
    Get semantic events for a specific branch.
    
    Args:
        branch (str): Branch name to query
        limit (int): Maximum number of events to return
        
    Returns:
        list: List of semantic events for the branch
    """
    query = """
        SELECT
            e.event_id, e.commit_hash, e.event_type, e.node_id, e.location, e.details,
            e.layer, e.layer_description, e.confidence, e.reasoning, e.impact,
            c.author, c.branch, c.timestamp,
            datetime(c.timestamp, 'unixepoch') as readable_date
        FROM semantic_events e
        JOIN commits c ON e.commit_hash = c.commit_hash
        WHERE c.branch = ?
        ORDER BY c.timestamp DESC
        LIMIT ?
    """
    return _execute_query(query, (branch, limit))

def get_repository_status():
    """
    Get comprehensive repository status including SVCS configuration and data.
    
    Returns:
        dict: Repository status information
    """
    try:
        # Check if database exists and get basic info
        if not os.path.exists(DB_PATH):
            return {
                "initialized": False,
                "database_exists": False,
                "error": "SVCS database not found"
            }
        
        # Get current branch
        try:
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True, check=True)
            current_branch = result.stdout.strip()
        except:
            current_branch = "unknown"
        
        # Get total events count
        total_query = "SELECT COUNT(*) as count FROM semantic_events"
        total_result = _execute_query(total_query, ())
        total_events = total_result[0].get('count', 0) if total_result else 0
        
        # Get recent events
        recent_events = get_recent_activity(days=7, limit=10)
        
        # Get branch-specific events
        branch_events = get_branch_events(current_branch, limit=10)
        
        return {
            "initialized": True,
            "database_exists": True,
            "current_branch": current_branch,
            "total_events": total_events,
            "semantic_events_count": len(branch_events),
            "recent_activity_count": len(recent_events),
            "last_analysis": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "initialized": False,
            "error": f"Failed to get repository status: {e}"
        }

# Export all functions
__all__ = [
    '_get_db_connection',
    '_execute_query',
    'get_valid_commit_hashes',
    'get_full_log',
    'search_events',
    'get_node_evolution',
    'find_dependency_changes',
    'get_commit_details',
    'search_events_advanced',
    'get_recent_activity',
    'get_project_statistics',
    'search_semantic_patterns',
    'get_filtered_evolution',
    'debug_query_tools',
    'get_commit_changed_files',
    'get_commit_diff',
    'get_commit_summary',
    'compare_branches',
    'generate_analytics',
    'analyze_quality',
    'get_branch_events',
    'get_repository_status'
]

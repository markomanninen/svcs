# FILE: .svcs/api.py
#
# This file contains the core logic for querying the SVCS database.
# This version includes joins to fetch commit metadata and comprehensive
# docstrings for all functions intended for LLM tool use.

import sqlite3
import os
import subprocess

# --- Configuration ---
SVCS_DIR = ".svcs"
# Support both old and new database names for compatibility
DB_PATH = os.path.join(SVCS_DIR, "semantic.db")
if not os.path.exists(DB_PATH):
    DB_PATH = os.path.join(SVCS_DIR, "history.db")

def _get_db_connection():
    """Establishes a connection to the SQLite database."""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"SVCS database not found at '{DB_PATH}'.")
    
    conn = sqlite3.connect(DB_PATH)
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

# --- API Functions (Now with Metadata and Docstrings for LLM) ---

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
        query_parts.append("e.event_type LIKE ?")
        params.append(f"%{event_type}%")
    if node_id:
        query_parts.append("e.node_id LIKE ?")
        params.append(f"%{node_id}%")
    if location:
        query_parts.append("e.location LIKE ?")
        params.append(f"%{location}%")

    full_query = base_query + " AND ".join(query_parts) + " ORDER BY c.timestamp DESC"
    return _execute_query(full_query, tuple(params))

def get_node_evolution(node_id: str):
    """
    Retrieves the complete, ordered history of a single semantic node (a function or class).
    Use this to answer questions about the full history or "story" of a specific node.

    Args:
        node_id (str): The unique ID of the node (e.g., 'func:greet', 'class:MyClass').
    """
    query = """
        SELECT
            e.event_id, e.commit_hash, e.event_type, e.node_id, e.location, e.details,
            e.layer, e.layer_description, e.confidence, e.reasoning, e.impact,
            c.author, c.branch, c.timestamp
        FROM semantic_events e
        JOIN commits c ON e.commit_hash = c.commit_hash
        WHERE e.node_id = ?
        ORDER BY c.timestamp ASC
    """
    return _execute_query(query, (node_id,))

def find_dependency_changes(dependency_name: str):
    """
    Finds all commits where a specific dependency or library was added or removed.
    Use this to answer questions like 'when was the math library added?'.

    Args:
        dependency_name (str): The name of the library or module to search for (e.g., 'math', 'os').
    """
    query = """
        SELECT 
            e.event_id, e.commit_hash, e.event_type, e.node_id, e.location, e.details,
            e.layer, e.layer_description, e.confidence, e.reasoning, e.impact,
            c.author, c.branch, c.timestamp 
        FROM semantic_events e
        JOIN commits c ON e.commit_hash = c.commit_hash
        WHERE e.event_type LIKE 'dependency_%' AND e.details LIKE ? ORDER BY c.timestamp DESC
    """
    return _execute_query(query, (f"%{dependency_name}%",))

def get_commit_details(commit_hash: str):
    """
    Gets all semantic events that occurred in a single, specific commit.
    Use this to find out everything that happened in a given commit.

    Args:
        commit_hash (str): The full or short hash of the commit to inspect.
    """
    query = """
        SELECT 
            e.event_id, e.commit_hash, e.event_type, e.node_id, e.location, e.details,
            e.layer, e.layer_description, e.confidence, e.reasoning, e.impact,
            c.author, c.branch, c.timestamp 
        FROM semantic_events e
        JOIN commits c ON e.commit_hash = c.commit_hash
        WHERE e.commit_hash LIKE ? ORDER BY c.timestamp DESC
    """
    return _execute_query(query, (f"{commit_hash}%",))


def prune_orphaned_data():
    """Removes data for orphaned commits from the database."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT commit_hash FROM commits")
    db_hashes = {row[0] for row in cursor.fetchall()}
    git_hashes = get_valid_commit_hashes()
    orphaned_hashes = db_hashes - git_hashes
    if not orphaned_hashes:
        conn.close()
        return 0
    with conn:
        for commit_hash in orphaned_hashes:
            cursor.execute("DELETE FROM semantic_events WHERE commit_hash = ?", (commit_hash,))
            cursor.execute("DELETE FROM commits WHERE commit_hash = ?", (commit_hash,))
    conn.close()
    return len(orphaned_hashes)

# --- Enhanced API Functions for Conversational Interface ---

def search_events_advanced(
    author=None, 
    event_types=None,  # List of event types
    location_pattern=None,
    layers=None,  # List of layers: ['core', '5a', '5b']
    min_confidence=None,
    max_confidence=None,
    since_date=None,  # YYYY-MM-DD or relative like "7 days ago"
    until_date=None,
    limit=20,
    offset=0,
    order_by="timestamp",  # timestamp, confidence, event_type
    order_desc=True
):
    """
    Advanced search with comprehensive filtering and pagination.
    Perfect for complex conversational queries like "show me performance optimizations 
    by John in the last week with high confidence".
    
    Args:
        author: Filter by commit author (partial match)
        event_types: List of event types to include
        location_pattern: File/location pattern to match
        layers: List of analysis layers ['core', '5a', '5b']  
        min_confidence: Minimum confidence score (0.0-1.0)
        max_confidence: Maximum confidence score (0.0-1.0)
        since_date: Start date (YYYY-MM-DD or relative like "7 days ago")
        until_date: End date (YYYY-MM-DD or relative like "1 day ago")
        limit: Maximum results to return (default 20)
        offset: Results offset for pagination (default 0)
        order_by: Sort field (timestamp, confidence, event_type)
        order_desc: Sort descending (default True)
    """
    # Build dynamic query
    query_parts = []
    params = []
    
    base_query = """
        SELECT
            e.event_id, e.commit_hash, e.event_type, e.node_id, e.location, e.details,
            e.layer, e.layer_description, e.confidence, e.reasoning, e.impact,
            c.author, c.branch, c.timestamp,
            datetime(c.timestamp, 'unixepoch') as readable_date
        FROM semantic_events e
        JOIN commits c ON e.commit_hash = c.commit_hash
        WHERE 1=1
    """
    
    # Author filtering
    if author:
        query_parts.append("c.author LIKE ?")
        params.append(f"%{author}%")
    
    # Event types filtering
    if event_types:
        placeholders = ",".join("?" * len(event_types))
        query_parts.append(f"e.event_type IN ({placeholders})")
        params.extend(event_types)
    
    # Location filtering
    if location_pattern:
        query_parts.append("e.location LIKE ?")
        params.append(f"%{location_pattern}%")
    
    # Layer filtering
    if layers:
        placeholders = ",".join("?" * len(layers))
        query_parts.append(f"e.layer IN ({placeholders})")
        params.extend(layers)
    
    # Confidence filtering
    if min_confidence is not None:
        query_parts.append("e.confidence IS NOT NULL AND e.confidence >= ?")
        params.append(min_confidence)
    
    if max_confidence is not None:
        query_parts.append("e.confidence IS NOT NULL AND e.confidence <= ?")
        params.append(max_confidence)
    
    # Date filtering with enhanced parsing
    if since_date:
        parsed_date = _parse_relative_date(since_date)
        if parsed_date:
            try:
                import time
                import datetime
                since_timestamp = int(time.mktime(datetime.datetime.strptime(parsed_date, "%Y-%m-%d").timetuple()))
                query_parts.append("c.timestamp >= ?")
                params.append(since_timestamp)
            except:
                pass  # Skip invalid dates
    
    if until_date:
        parsed_until = _parse_relative_date(until_date)
        if parsed_until:
            try:
                import time
                import datetime
                until_timestamp = int(time.mktime(datetime.datetime.strptime(parsed_until, "%Y-%m-%d").timetuple()))
                query_parts.append("c.timestamp <= ?")
                params.append(until_timestamp)
            except:
                pass  # Skip invalid dates
    
    # Build complete query
    if query_parts:
        full_query = base_query + " AND " + " AND ".join(query_parts)
    else:
        full_query = base_query
    
    # Add ordering
    valid_order_fields = ["timestamp", "confidence", "event_type", "author"]
    if order_by not in valid_order_fields:
        order_by = "timestamp"
    
    order_direction = "DESC" if order_desc else "ASC"
    
    if order_by == "confidence":
        full_query += f" ORDER BY e.confidence {order_direction}"
    elif order_by in ["timestamp", "author"]:
        full_query += f" ORDER BY c.{order_by} {order_direction}"
    else:
        full_query += f" ORDER BY e.{order_by} {order_direction}"
    
    # Add pagination
    full_query += " LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    return _execute_query(full_query, tuple(params))

def get_recent_activity(
    days=7,
    layers=None,
    event_types=None,
    author=None,
    limit=20
):
    """
    Get recent semantic activity in the project.
    Use for queries like "what happened last week?" or "recent changes by John".
    
    Args:
        days: Number of days back to search (default 7)
        layers: Filter by analysis layers
        event_types: Filter by specific event types
        author: Filter by author
        limit: Maximum results (default 20)
    """
    import time
    import datetime
    
    # Calculate timestamp for 'days' ago
    since_timestamp = int(time.time()) - (days * 24 * 60 * 60)
    
    query_parts = ["c.timestamp >= ?"]
    params = [since_timestamp]
    
    base_query = """
        SELECT
            e.event_id, e.commit_hash, e.event_type, e.node_id, e.location, e.details,
            e.layer, e.layer_description, e.confidence, e.reasoning, e.impact,
            c.author, c.branch, c.timestamp,
            datetime(c.timestamp, 'unixepoch') as readable_date
        FROM semantic_events e
        JOIN commits c ON e.commit_hash = c.commit_hash
        WHERE
    """
    
    # Layer filtering
    if layers:
        placeholders = ",".join("?" * len(layers))
        query_parts.append(f"e.layer IN ({placeholders})")
        params.extend(layers)
    
    # Event types filtering
    if event_types:
        placeholders = ",".join("?" * len(event_types))
        query_parts.append(f"e.event_type IN ({placeholders})")
        params.extend(event_types)
    
    # Author filtering
    if author:
        query_parts.append("c.author LIKE ?")
        params.append(f"%{author}%")
    
    # Build complete query
    full_query = base_query + " AND ".join(query_parts)
    full_query += " ORDER BY c.timestamp DESC LIMIT ?"
    params.append(limit)
    
    return _execute_query(full_query, tuple(params))

def get_project_statistics(
    since_date=None,
    until_date=None,
    group_by="event_type"  # event_type, layer, author, location
):
    """
    Get statistical overview of project semantic events.
    Use for queries like "project summary" or "what types of changes happen most?".
    
    Args:
        since_date: Start date for statistics
        until_date: End date for statistics  
        group_by: How to group the statistics
    """
    query_parts = []
    params = []
    
    # Valid group_by options
    valid_groups = {
        "event_type": "e.event_type",
        "layer": "e.layer", 
        "author": "c.author",
        "location": "e.location"
    }
    
    if group_by not in valid_groups:
        group_by = "event_type"
    
    group_field = valid_groups[group_by]
    
    base_query = f"""
        SELECT
            {group_field} as category,
            COUNT(*) as count,
            AVG(CASE WHEN e.confidence IS NOT NULL THEN e.confidence ELSE 0 END) as avg_confidence,
            MAX(c.timestamp) as latest_timestamp,
            datetime(MAX(c.timestamp), 'unixepoch') as latest_date
        FROM semantic_events e
        JOIN commits c ON e.commit_hash = c.commit_hash
        WHERE 1=1
    """
    
    # Date filtering
    if since_date:
        try:
            import time
            import datetime
            if since_date.replace("-", "").isdigit():
                since_timestamp = int(time.mktime(datetime.datetime.strptime(since_date, "%Y-%m-%d").timetuple()))
                query_parts.append("c.timestamp >= ?")
                params.append(since_timestamp)
        except:
            pass
    
    if until_date:
        try:
            import time
            import datetime
            if until_date.replace("-", "").isdigit():
                until_timestamp = int(time.mktime(datetime.datetime.strptime(until_date, "%Y-%m-%d").timetuple()))
                query_parts.append("c.timestamp <= ?")
                params.append(until_timestamp)
        except:
            pass
    
    # Build complete query
    if query_parts:
        full_query = base_query + " AND " + " AND ".join(query_parts)
    else:
        full_query = base_query
    
    full_query += f" GROUP BY {group_field} ORDER BY count DESC"
    
    return _execute_query(full_query, tuple(params))

def search_semantic_patterns(
    pattern_type=None,  # "performance", "architecture", "error_handling", "readability"
    min_confidence=0.7,
    author=None,
    since_date=None,
    limit=15
):
    """
    Search for specific semantic patterns detected by AI layers.
    Use for queries like "show me performance optimizations" or "architecture changes".
    
    Args:
        pattern_type: Type of semantic pattern to find
        min_confidence: Minimum AI confidence score
        author: Filter by author
        since_date: Start date for search
        limit: Maximum results
    """
    query_parts = []
    params = []
    
    base_query = """
        SELECT
            e.event_id, e.commit_hash, e.event_type, e.node_id, e.location, e.details,
            e.layer, e.layer_description, e.confidence, e.reasoning, e.impact,
            c.author, c.branch, c.timestamp,
            datetime(c.timestamp, 'unixepoch') as readable_date
        FROM semantic_events e
        JOIN commits c ON e.commit_hash = c.commit_hash
        WHERE e.layer IN ('5a', '5b')
    """
    
    # Pattern type mapping to event types
    pattern_mappings = {
        "performance": ["abstract_performance_optimization", "performance_pattern_optimized"],
        "architecture": ["abstract_architecture_change", "abstract_abstraction_improvement"],
        "error_handling": ["abstract_error_strategy_change", "error_handling_pattern_improved"],
        "readability": ["abstract_readability_improvement", "abstract_maintainability_improvement"]
    }
    
    # Pattern type filtering
    if pattern_type and pattern_type in pattern_mappings:
        event_types = pattern_mappings[pattern_type]
        placeholders = ",".join("?" * len(event_types))
        query_parts.append(f"e.event_type IN ({placeholders})")
        params.extend(event_types)
    elif pattern_type:
        # Direct pattern matching in event_type or details
        query_parts.append("(e.event_type LIKE ? OR e.details LIKE ?)")
        params.extend([f"%{pattern_type}%", f"%{pattern_type}%"])
    
    # Confidence filtering
    if min_confidence is not None:
        query_parts.append("e.confidence >= ?")
        params.append(min_confidence)
    
    # Author filtering
    if author:
        query_parts.append("c.author LIKE ?")
        params.append(f"%{author}%")
    
    # Date filtering with enhanced parsing
    if since_date:
        parsed_date = _parse_relative_date(since_date)
        if parsed_date:
            try:
                import time
                import datetime
                since_timestamp = int(time.mktime(datetime.datetime.strptime(parsed_date, "%Y-%m-%d").timetuple()))
                query_parts.append("c.timestamp >= ?")
                params.append(since_timestamp)
            except:
                pass
    
    # Build complete query
    if query_parts:
        full_query = base_query + " AND " + " AND ".join(query_parts)
    else:
        full_query = base_query
    
    full_query += " ORDER BY e.confidence DESC, c.timestamp DESC LIMIT ?"
    params.append(limit)
    
    return _execute_query(full_query, tuple(params))

def get_filtered_evolution(
    node_id,
    event_types=None,
    since_date=None,
    until_date=None,
    min_confidence=None
):
    """
    Get filtered evolution history of a specific node.
    Use for queries like "show me only the signature changes for func:greet since June".
    
    Args:
        node_id: The node to track (e.g., "func:greet")
        event_types: List of event types to include in evolution
        since_date: Start date for evolution history
        until_date: End date for evolution history
        min_confidence: Minimum confidence for AI events
    """
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Build the query
        query = """
            SELECT 
                e.event_id, e.commit_hash, e.event_type, e.node_id, e.location, e.details,
                e.layer, e.layer_description, e.confidence, e.reasoning, e.impact,
                c.author, c.branch, c.timestamp
            FROM semantic_events e
            JOIN commits c ON e.commit_hash = c.commit_hash
            WHERE e.node_id = ?
        """
        params = [node_id]
        
        # Add filters
        if event_types:
            placeholders = ','.join(['?' for _ in event_types])
            query += f" AND e.event_type IN ({placeholders})"
            params.extend(event_types)
        
        if since_date:
            # Parse date using existing function
            date_str = _parse_relative_date(since_date)
            if date_str:
                # Convert to timestamp for comparison
                import datetime
                try:
                    dt = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                    timestamp = int(dt.timestamp())
                    query += " AND c.timestamp >= ?"
                    params.append(timestamp)
                except ValueError:
                    pass  # Skip invalid dates
        
        if until_date:
            date_str = _parse_relative_date(until_date)
            if date_str:
                import datetime
                try:
                    dt = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                    timestamp = int(dt.timestamp())
                    query += " AND c.timestamp <= ?"
                    params.append(timestamp)
                except ValueError:
                    pass  # Skip invalid dates
        
        if min_confidence is not None:
            query += " AND (e.confidence IS NULL OR e.confidence >= ?)"
            params.append(min_confidence)
        
        query += " ORDER BY c.timestamp DESC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        events = []
        for row in results:
            event_dict = dict(row)
            # Add readable date
            if event_dict['timestamp']:
                import datetime
                event_dict['readable_date'] = datetime.datetime.fromtimestamp(
                    event_dict['timestamp']
                ).strftime('%Y-%m-%d %H:%M:%S')
            events.append(event_dict)
        
        return events
        
    except Exception as e:
        print(f"Error in get_filtered_evolution: {e}")
        return []
    finally:
        conn.close()

# --- Git Integration Functions for Changed Files and Diffs ---

def get_commit_changed_files(commit_hash: str):
    """
    Gets the list of files that were changed in a specific commit.
    
    Args:
        commit_hash (str): The full or short hash of the commit to inspect.
        
    Returns:
        List[str]: List of file paths that were changed in the commit.
    """
    try:
        # Get parent commit
        parent_result = subprocess.run(
            ['git', 'rev-parse', f'{commit_hash}~1'],
            capture_output=True,
            text=True
        )
        
        if parent_result.returncode == 0:
            # Compare with parent commit
            parent_hash = parent_result.stdout.strip()
            cmd = ['git', 'diff', '--name-only', parent_hash, commit_hash]
        else:
            # Initial commit, list all files
            cmd = ['git', 'ls-tree', '-r', '--name-only', commit_hash]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
        return files
        
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to get changed files for commit {commit_hash}: {e}")

def get_commit_diff(commit_hash: str, file_path: str = None):
    """
    Gets the git diff for a specific commit, optionally filtered to a specific file.
    
    Args:
        commit_hash (str): The full or short hash of the commit to inspect.
        file_path (str, optional): If provided, only show diff for this specific file.
        
    Returns:
        str: The git diff output for the commit.
    """
    try:
        # Build the git show command
        cmd = ['git', 'show', commit_hash]
        
        # If file_path is provided, filter to just that file
        if file_path:
            cmd.extend(['--', file_path])
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
        
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to get diff for commit {commit_hash}: {e}")

def get_commit_summary(commit_hash: str):
    """
    Gets a comprehensive summary of a commit including metadata, changed files, and semantic events.
    
    Args:
        commit_hash (str): The full or short hash of the commit to inspect.
        
    Returns:
        dict: Comprehensive commit information including:
            - commit_info: Basic git metadata (author, message, date)
            - changed_files: List of files changed
            - semantic_events: List of semantic events detected
            - file_count: Number of files changed
            - semantic_event_count: Number of semantic events
    """
    try:
        # Get basic commit info
        author_result = subprocess.run(
            ['git', 'log', '-1', '--pretty=format:%an', commit_hash],
            capture_output=True, text=True, check=True
        )
        message_result = subprocess.run(
            ['git', 'log', '-1', '--pretty=format:%s', commit_hash],
            capture_output=True, text=True, check=True
        )
        date_result = subprocess.run(
            ['git', 'log', '-1', '--pretty=format:%ci', commit_hash],
            capture_output=True, text=True, check=True
        )
        
        commit_info = {
            'commit_hash': commit_hash,
            'author': author_result.stdout.strip(),
            'message': message_result.stdout.strip(),
            'date': date_result.stdout.strip()
        }
        
        # Get changed files
        changed_files = get_commit_changed_files(commit_hash)
        
        # Get semantic events
        semantic_events = get_commit_details(commit_hash)
        
        return {
            'commit_info': commit_info,
            'changed_files': changed_files,
            'semantic_events': semantic_events,
            'file_count': len(changed_files),
            'semantic_event_count': len(semantic_events)
        }
        
    except Exception as e:
        raise Exception(f"Failed to get commit summary for {commit_hash}: {e}")

# --- Helper Functions ---

def _parse_relative_date(date_str):
    """
    Parse relative dates like '7 days ago', 'last week', 'yesterday'.
    Returns a YYYY-MM-DD string or None if parsing fails.
    """
    import datetime
    import re
    
    if not date_str:
        return None
        
    date_str = date_str.lower().strip()
    now = datetime.datetime.now()
    
    # Direct date formats (YYYY-MM-DD, MM/DD/YYYY, etc.)
    if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
        return date_str
    
    # Days ago patterns
    days_match = re.search(r'(\d+)\s*days?\s*ago', date_str)
    if days_match:
        days = int(days_match.group(1))
        target_date = now - datetime.timedelta(days=days)
        return target_date.strftime('%Y-%m-%d')
    
    # Weeks ago patterns  
    weeks_match = re.search(r'(\d+)\s*weeks?\s*ago', date_str)
    if weeks_match:
        weeks = int(weeks_match.group(1))
        target_date = now - datetime.timedelta(weeks=weeks)
        return target_date.strftime('%Y-%m-%d')
    
    # Common relative terms
    if 'yesterday' in date_str:
        target_date = now - datetime.timedelta(days=1)
        return target_date.strftime('%Y-%m-%d')
    
    if 'last week' in date_str:
        # Start of last week (Monday)
        days_since_monday = now.weekday()
        target_date = now - datetime.timedelta(days=days_since_monday + 7)
        return target_date.strftime('%Y-%m-%d')
    
    if 'this week' in date_str:
        # Start of this week (Monday)
        days_since_monday = now.weekday()
        target_date = now - datetime.timedelta(days=days_since_monday)
        return target_date.strftime('%Y-%m-%d')
    
    if 'last month' in date_str:
        # First day of last month
        first_of_this_month = now.replace(day=1)
        target_date = (first_of_this_month - datetime.timedelta(days=1)).replace(day=1)
        return target_date.strftime('%Y-%m-%d')
    
    if 'this month' in date_str:
        # First day of this month
        target_date = now.replace(day=1)
        return target_date.strftime('%Y-%m-%d')
    
    # Sprint patterns (assuming 2-week sprints)
    if 'last sprint' in date_str:
        target_date = now - datetime.timedelta(weeks=2)
        return target_date.strftime('%Y-%m-%d')
    
    if 'this sprint' in date_str:
        # Approximate start of current sprint (2 weeks ago from now)
        target_date = now - datetime.timedelta(days=14)
        return target_date.strftime('%Y-%m-%d')
    
    # Quarter patterns
    if 'last quarter' in date_str:
        # Rough approximation: 3 months ago
        target_date = now - datetime.timedelta(days=90)
        return target_date.strftime('%Y-%m-%d')
    
    # Since patterns
    since_match = re.search(r'since\s+(\w+\s*\d*)', date_str)
    if since_match:
        since_part = since_match.group(1)
        # Try to parse common "since X" patterns
        if 'monday' in since_part:
            days_since_monday = now.weekday()
            target_date = now - datetime.timedelta(days=days_since_monday)
            return target_date.strftime('%Y-%m-%d')
        elif 'june' in since_part:
            # Default to June 1st of current year
            target_date = datetime.datetime(now.year, 6, 1)
            return target_date.strftime('%Y-%m-%d')
    
    # If nothing matches, return None
    return None

def _format_results_for_conversation(results, query_type="general"):
    """Format results appropriately for conversational display."""
    if not results:
        return _get_no_results_guidance(query_type)
    
    # Group results by type for better narrative
    if query_type == "recent_activity":
        return _format_recent_activity(results)
    elif query_type == "semantic_patterns":
        return _format_semantic_patterns(results)
    elif query_type == "advanced_search":
        return _format_advanced_search(results)
    else:
        return _format_general_results(results)

def _get_no_results_guidance(query_type="general"):
    """Provide helpful guidance when no results are found."""
    base_message = "No results found for your query."
    
    suggestions = {
        "recent_activity": [
            "Try expanding the time range (e.g., 'last 2 weeks')",
            "Check if there are any commits in the repository",
            "Use 'get_project_statistics()' to see overall activity"
        ],
        "semantic_patterns": [
            "Try lowering the confidence threshold (min_confidence=0.5)",
            "Use broader pattern types: 'performance', 'architecture', 'error_handling'",
            "Check what event types exist with get_project_statistics()"
        ],
        "advanced_search": [
            "Try broader date ranges or remove author filters",
            "Use get_recent_activity() to see what data is available",
            "Check spelling of author names and file patterns"
        ],
        "general": [
            "Use get_project_statistics() to see available data",
            "Try get_recent_activity() to see recent changes",
            "Use broader search terms or date ranges"
        ]
    }
    
    query_suggestions = suggestions.get(query_type, suggestions["general"])
    
    guidance = f"{base_message}\n\n**Suggestions:**\n"
    for suggestion in query_suggestions:
        guidance += f"• {suggestion}\n"
    
    guidance += "\n**Example queries that usually work:**\n"
    guidance += "• 'What happened in the last week?'\n"
    guidance += "• 'Show me all changes with confidence > 80%'\n"
    guidance += "• 'Give me a project overview'\n"
    
    return guidance

def _format_recent_activity(results):
    """Format recent activity results with narrative context."""
    if len(results) > 10:
        summary = f"Found {len(results)} recent events. Here are the most recent:\n\n"
    else:
        summary = f"Recent activity ({len(results)} events):\n\n"
    
    # Group by date for better readability
    by_date = {}
    for event in results[:10]:  # Limit to top 10
        date = event.get('readable_date', 'Unknown')[:10]  # YYYY-MM-DD
        if date not in by_date:
            by_date[date] = []
        by_date[date].append(event)
    
    for date in sorted(by_date.keys(), reverse=True):
        summary += f"**{date}:**\n"
        for event in by_date[date]:
            event_type = event.get('event_type', 'unknown')
            location = event.get('location', 'unknown')
            author = event.get('author', 'unknown')
            summary += f"• {event_type} in {location} by {author}\n"
        summary += "\n"
    
    return summary

def _format_semantic_patterns(results):
    """Format semantic pattern results with confidence and reasoning."""
    if not results:
        return _get_no_results_guidance("semantic_patterns")
    
    summary = f"Found {len(results)} semantic patterns:\n\n"
    
    for i, event in enumerate(results[:8], 1):  # Limit to top 8
        confidence = event.get('confidence', 0)
        location = event.get('location', 'unknown')
        details = event.get('details', 'No details available')
        reasoning = event.get('reasoning', 'No reasoning provided')
        
        summary += f"**{i}. {location}** (confidence: {confidence:.0%})\n"
        summary += f"   {details[:100]}{'...' if len(details) > 100 else ''}\n"
        if reasoning and reasoning != 'No reasoning provided':
            summary += f"   *Reasoning: {reasoning[:80]}{'...' if len(reasoning) > 80 else ''}*\n"
        summary += "\n"
    
    return summary

def _format_advanced_search(results):
    """Format advanced search results with categorization."""
    if not results:
        return _get_no_results_guidance("advanced_search")
    
    # Group by event type
    by_type = {}
    for event in results:
        event_type = event.get('event_type', 'unknown')
        if event_type not in by_type:
            by_type[event_type] = []
        by_type[event_type].append(event)
    
    summary = f"Found {len(results)} events across {len(by_type)} types:\n\n"
    
    for event_type, events in by_type.items():
        summary += f"**{event_type}** ({len(events)} events):\n"
        for event in events[:3]:  # Show top 3 per type
            location = event.get('location', 'unknown')
            author = event.get('author', 'unknown')
            date = event.get('readable_date', 'N/A')[:16]
            confidence = event.get('confidence')
            
            conf_str = f" (confidence: {confidence:.0%})" if confidence else ""
            summary += f"• {location} by {author} on {date}{conf_str}\n"
        
        if len(events) > 3:
            summary += f"  ... and {len(events) - 3} more\n"
        summary += "\n"
    
    return summary

def _format_general_results(results):
    """Format general results with basic information."""
    if not results:
        return _get_no_results_guidance("general")
    
    summary = f"Found {len(results)} results:\n\n"
    
    for i, event in enumerate(results[:10], 1):
        event_type = event.get('event_type', 'unknown')
        location = event.get('location', 'unknown')
        author = event.get('author', 'unknown')
        date = event.get('readable_date', 'N/A')[:16]
        
        summary += f"{i}. **{event_type}** in {location}\n"
        summary += f"   By {author} on {date}\n\n"
    
    if len(results) > 10:
        summary += f"... and {len(results) - 10} more results.\n"
    
    return summary

def debug_query_tools(query_description="unspecified query"):
    """
    Debug function to help troubleshoot when conversational queries don't find expected results.
    This function tries multiple approaches and reports what it finds.
    
    Args:
        query_description: Description of what the user was looking for
    """
    debug_info = {
        "query": query_description,
        "total_events": 0,
        "recent_events": 0,
        "performance_events": 0,
        "ai_events": 0,
        "approaches": {}
    }
    
    try:
        # Get total event count
        total_query = "SELECT COUNT(*) as count FROM semantic_events"
        total_result = _execute_query(total_query, ())
        debug_info["total_events"] = total_result[0].get('count', 0) if total_result else 0
        
        # Get recent events (last 7 days)
        recent = get_recent_activity(days=7, limit=100)
        debug_info["recent_events"] = len(recent)
        
        # Count performance-related events
        perf_events = [e for e in recent if 'performance' in e.get('event_type', '').lower() or 'optimization' in e.get('event_type', '').lower()]
        debug_info["performance_events"] = len(perf_events)
        
        # Count AI events (layer 5a, 5b)
        ai_events = [e for e in recent if e.get('layer') in ['5a', '5b']]
        debug_info["ai_events"] = len(ai_events)
        
        # Try different search approaches for performance
        debug_info["approaches"]["semantic_patterns_performance"] = len(search_semantic_patterns(pattern_type="performance", min_confidence=0.5, limit=20))
        debug_info["approaches"]["semantic_patterns_optimization"] = len(search_semantic_patterns(pattern_type="optimization", min_confidence=0.5, limit=20))
        debug_info["approaches"]["advanced_search_performance"] = len(search_events_advanced(event_types=["abstract_performance_optimization"], limit=20))
        
        # Sample of recent event types
        event_types = list(set([e.get('event_type', 'unknown') for e in recent[:20]]))
        debug_info["sample_recent_event_types"] = event_types[:10]
        
        return debug_info
        
    except Exception as e:
        debug_info["error"] = str(e)
        return debug_info

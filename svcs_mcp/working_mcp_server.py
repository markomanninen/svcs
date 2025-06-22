#!/usr/bin/env python3
"""
Working SVCS MCP Server - Functional Implementation

This is a working MCP server that can actually run and respond to semantic queries.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import mcp.types as types

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from svcs_mcp_server_simple import GlobalSVCSDatabase, ProjectManager, SVCSQueryEngine
    from svcs_mcp.semantic_analyzer import GlobalSemanticAnalyzer
    from svcs_mcp.cli import SVCSDatabase as CLIDatabase
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import components: {e}")
    COMPONENTS_AVAILABLE = False

# Initialize components
if COMPONENTS_AVAILABLE:
    db = GlobalSVCSDatabase()
    project_manager = ProjectManager(db)
    query_engine = SVCSQueryEngine(db)
    cli_db = CLIDatabase()  # Use CLI database for methods that need author data
    semantic_analyzer = GlobalSemanticAnalyzer(db)
else:
    db = None
    project_manager = None
    query_engine = None
    semantic_analyzer = None

# Create MCP server
server = Server("svcs-working-mcp")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="register_project",
            description="Register a new project for SVCS semantic tracking",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Project path"},
                    "name": {"type": "string", "description": "Project name"}
                },
                "required": ["path", "name"]
            }
        ),
        Tool(
            name="list_projects", 
            description="List all registered SVCS projects",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="get_project_statistics",
            description="Get semantic statistics for a project",
            inputSchema={
                "type": "object", 
                "properties": {
                    "project_id": {"type": "string", "description": "Project ID"}
                },
                "required": ["project_id"]
            }
        ),
        Tool(
            name="analyze_current_commit",
            description="Analyze the current/latest commit for semantic changes",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "Project path"}
                },
                "required": ["project_path"]
            }
        ),
        Tool(
            name="query_semantic_events",
            description="Query semantic events from the database",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "Project ID (optional)"},
                    "event_type": {"type": "string", "description": "Event type filter (optional)"},
                    "limit": {"type": "number", "description": "Max results (default 10)"}
                }
            }
        ),
        Tool(
            name="search_events_advanced",
            description="Advanced search with comprehensive filtering options",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "Project path"},
                    "author": {"type": "string", "description": "Author filter (optional)"},
                    "event_types": {"type": "array", "items": {"type": "string"}, "description": "Event type filters (optional)"},
                    "location_pattern": {"type": "string", "description": "Location pattern filter (optional)"},
                    "layers": {"type": "array", "items": {"type": "string"}, "description": "Layer filters (optional)"},
                    "min_confidence": {"type": "number", "description": "Minimum confidence threshold (optional)"},
                    "since_date": {"type": "string", "description": "Date filter (YYYY-MM-DD or 'N days ago') (optional)"},
                    "limit": {"type": "number", "description": "Max results (default 20)"},
                    "order_by": {"type": "string", "description": "Order by field (optional)"},
                    "order_desc": {"type": "boolean", "description": "Descending order (default true)"}
                },
                "required": ["project_path"]
            }
        ),
        Tool(
            name="get_recent_activity",
            description="Get recent project activity with filtering options",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "Project path"},
                    "days": {"type": "number", "description": "Number of days back (default 7)"},
                    "layers": {"type": "array", "items": {"type": "string"}, "description": "Layer filters (optional)"},
                    "author": {"type": "string", "description": "Author filter (optional)"},
                    "limit": {"type": "number", "description": "Max results (default 15)"}
                },
                "required": ["project_path"]
            }
        ),
        Tool(
            name="search_semantic_patterns",
            description="Search for specific AI-detected semantic patterns",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "Project path"},
                    "pattern_type": {"type": "string", "description": "Pattern type (performance, architecture, error_handling, etc.)"},
                    "min_confidence": {"type": "number", "description": "Minimum confidence threshold (default 0.7)"},
                    "since_date": {"type": "string", "description": "Date filter (YYYY-MM-DD or 'N days ago') (optional)"},
                    "limit": {"type": "number", "description": "Max results (default 10)"}
                },
                "required": ["project_path", "pattern_type"]
            }
        ),
        Tool(
            name="get_filtered_evolution",
            description="Get filtered evolution history for a specific node/function",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "Project path"},
                    "node_id": {"type": "string", "description": "Node ID (e.g., func:function_name)"},
                    "event_types": {"type": "array", "items": {"type": "string"}, "description": "Event type filters (optional)"},
                    "since_date": {"type": "string", "description": "Date filter (YYYY-MM-DD or 'N days ago') (optional)"},
                    "min_confidence": {"type": "number", "description": "Minimum confidence threshold (default 0.0)"}
                },
                "required": ["project_path", "node_id"]
            }
        ),
        Tool(
            name="debug_query_tools",
            description="Diagnostic information for debugging query issues",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "Project path"}
                },
                "required": ["project_path"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle MCP tool calls."""
    
    if not COMPONENTS_AVAILABLE:
        return [types.TextContent(
            type="text",
            text="❌ SVCS components not available. Please check installation."
        )]
    
    def get_project_id_from_path(project_path: str) -> str:
        """Helper function to get project_id from project_path."""
        project = db.get_project_by_path(project_path)
        if not project:
            raise Exception(f"Project not found: {project_path}")
        return project['project_id']
    
    try:
        if name == "register_project":
            path = arguments.get("path")
            project_name = arguments.get("name")
            
            # Check if it's a git repository, if not initialize it
            from pathlib import Path
            import subprocess
            
            git_dir = Path(path) / '.git'
            git_init_msg = ""
            
            if not git_dir.exists():
                try:
                    result = subprocess.run(['git', 'init'], cwd=path, capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        git_init_msg = f"📁 Directory was not a git repository. Git initialized in {path}\n"
                    else:
                        return [types.TextContent(
                            type="text",
                            text=f"❌ Error initializing git: {result.stderr.strip() or 'Git init failed'}"
                        )]
                except FileNotFoundError:
                    return [types.TextContent(
                        type="text",
                        text="❌ Error: git command not found. Please install git first."
                    )]
                except subprocess.TimeoutExpired:
                    return [types.TextContent(
                        type="text",
                        text="❌ Error: git init timed out"
                    )]
                except Exception as e:
                    return [types.TextContent(
                        type="text",
                        text=f"❌ Error initializing git: {str(e)}"
                    )]
            
            # Register with database
            project_id = db.register_project(project_name, path)
            
            # Install git hooks
            from svcs_mcp.git_hooks import GitHookManager
            hook_manager = GitHookManager()
            hook_success = hook_manager.install_project_hooks(path)
            
            result = git_init_msg
            result += f"✅ Project '{project_name}' registered!\n"
            result += f"📝 Project ID: {project_id[:8]}...\n"
            result += f"📁 Path: {path}\n"
            if hook_success:
                result += f"🔗 Git hooks installed successfully"
            else:
                result += f"⚠️ Git hooks installation failed"
                
            return [types.TextContent(type="text", text=result)]
        
        elif name == "list_projects":
            projects = db.list_projects()
            
            if not projects:
                return [types.TextContent(
                    type="text", 
                    text="📋 No projects registered with SVCS yet."
                )]
            
            result = f"📋 **SVCS Registered Projects** ({len(projects)} total)\n\n"
            for project in projects:
                result += f"• **{project['name']}**\n"
                result += f"  - ID: `{project['project_id'][:8]}...`\n"
                result += f"  - Path: `{project['path']}`\n"
                result += f"  - Status: {project['status']}\n\n"
            
            return [types.TextContent(type="text", text=result)]
        
        elif name == "get_project_statistics":
            project_id = arguments.get("project_id")
            
            try:
                # Handle partial project IDs
                if len(project_id) < 36:  # Not a full UUID
                    with db.get_connection() as conn:
                        cursor = conn.execute(
                            "SELECT project_id, name FROM projects WHERE project_id LIKE ?",
                            (f"{project_id}%",)
                        )
                        project = cursor.fetchone()
                    
                    if not project:
                        return [types.TextContent(
                            type="text",
                            text=f"❌ No project found with ID starting with: {project_id}"
                        )]
                    
                    full_project_id = project[0]
                    project_name = project[1]
                else:
                    full_project_id = project_id
                    project_name = "Unknown"
                
                stats = db.get_project_statistics(full_project_id)
                
                result = f"📊 **Statistics for '{project_name}'**\n\n"
                result += f"- **Project ID**: `{full_project_id[:8]}...`\n"
                result += f"- **Total Events**: {stats['total_events']}\n"
                result += f"- **Total Commits**: {stats['total_commits']}\n"
                
                if stats['event_types']:
                    result += f"- **Event Types**:\n"
                    for event_type, count in stats['event_types'].items():
                        result += f"  - {event_type}: {count}\n"
                else:
                    result += f"- **Event Types**: None yet\n"
                
                if stats['layers']:
                    result += f"- **Layers**:\n"
                    for layer, count in stats['layers'].items():
                        result += f"  - {layer}: {count}\n"
                
                return [types.TextContent(type="text", text=result)]
                
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Error getting statistics: {str(e)}"
                )]
        
        elif name == "analyze_current_commit":
            project_path = arguments.get("project_path")
            
            # Use the improved process_commit function
            from svcs_mcp_server_simple import process_commit
            
            try:
                # This will trigger the full semantic analysis with debug output
                process_commit(project_path)
                
                result = f"🔍 **Semantic Analysis Complete**\n\n"
                result += f"- **Project Path**: `{project_path}`\n"
                result += f"✅ Analysis completed successfully with full debug output in console\n"
                result += f"📊 Check the terminal for detailed event table and statistics"
                
                return [types.TextContent(type="text", text=result)]
                
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Analysis Error: {str(e)}"
                )]
        
        elif name == "query_semantic_events":
            project_id = arguments.get("project_id")
            event_type = arguments.get("event_type") 
            limit = arguments.get("limit", 10)
            
            # Use the improved query method that handles the correct column names
            try:
                # Handle partial project IDs
                full_project_id = project_id
                if project_id and len(project_id) < 36:  # Not a full UUID
                    with db.get_connection() as conn:
                        cursor = conn.execute(
                            "SELECT project_id FROM projects WHERE project_id LIKE ?",
                            (f"{project_id}%",)
                        )
                        project = cursor.fetchone()
                    
                    if project:
                        full_project_id = project[0]
                    else:
                        return [types.TextContent(
                            type="text",
                            text=f"❌ No project found with ID starting with: {project_id}"
                        )]
                
                events = db.query_semantic_events(project_id=full_project_id, event_type=event_type, limit=limit)
                
                if not events:
                    return [types.TextContent(
                        type="text",
                        text="📊 No semantic events found matching your criteria."
                    )]
                
                result = f"📊 **Semantic Events** ({len(events)} found)\n\n"
                for event in events:
                    result += f"• **{event['event_type']}** (Project: {event['project_name'] or 'Unknown'})\n"
                    result += f"  - Node: `{event['node_id']}`\n"
                    result += f"  - Location: `{event['location']}`\n"
                    result += f"  - Details: {event['details']}\n"
                    result += f"  - Author: {event['author'] or 'Unknown'}\n"
                    result += f"  - Commit: `{event['commit_hash'][:8]}...`\n"
                    result += f"  - Layer: {event['layer']}\n\n"
                
                return [types.TextContent(type="text", text=result)]
                
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Error executing query_semantic_events: {str(e)}"
                )]
        
        elif name == "search_events_advanced":
            project_path = arguments.get("project_path")
            
            kwargs = {}
            if arguments.get("author"):
                kwargs["author"] = arguments.get("author")
            if arguments.get("event_types"):
                kwargs["event_types"] = arguments.get("event_types")
            if arguments.get("location_pattern"):
                kwargs["location_pattern"] = arguments.get("location_pattern")
            if arguments.get("layers"):
                kwargs["layers"] = arguments.get("layers")
            if arguments.get("min_confidence") is not None:
                kwargs["min_confidence"] = arguments.get("min_confidence")
            if arguments.get("since_date"):
                kwargs["since_date"] = arguments.get("since_date")
            if arguments.get("limit"):
                kwargs["limit"] = arguments.get("limit")
            if arguments.get("order_by"):
                kwargs["order_by"] = arguments.get("order_by")
            if arguments.get("order_desc") is not None:
                kwargs["order_desc"] = arguments.get("order_desc")
            
            try:
                result = cli_db.search_events_advanced(project_path, **kwargs)
                return [types.TextContent(type="text", text=result)]
                
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Error executing search_events_advanced: {str(e)}"
                )]
        
        elif name == "get_recent_activity":
            project_path = arguments.get("project_path")
            
            kwargs = {}
            if arguments.get("days"):
                kwargs["days"] = arguments.get("days")
            if arguments.get("layers"):
                kwargs["layers"] = arguments.get("layers")
            if arguments.get("author"):
                kwargs["author"] = arguments.get("author")
            if arguments.get("limit"):
                kwargs["limit"] = arguments.get("limit")
            
            try:
                result = cli_db.get_recent_activity(project_path, **kwargs)
                return [types.TextContent(type="text", text=result)]
                
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Error executing get_recent_activity: {str(e)}"
                )]
        
        elif name == "search_semantic_patterns":
            project_path = arguments.get("project_path")
            pattern_type = arguments.get("pattern_type")
            
            kwargs = {}
            if arguments.get("min_confidence") is not None:
                kwargs["min_confidence"] = arguments.get("min_confidence")
            if arguments.get("since_date"):
                kwargs["since_date"] = arguments.get("since_date")
            if arguments.get("limit"):
                kwargs["limit"] = arguments.get("limit")
            
            try:
                result = cli_db.search_semantic_patterns(project_path, pattern_type, **kwargs)
                return [types.TextContent(type="text", text=result)]
                
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Error executing search_semantic_patterns: {str(e)}"
                )]
        
        elif name == "get_filtered_evolution":
            project_path = arguments.get("project_path")
            node_id = arguments.get("node_id")
            
            kwargs = {}
            if arguments.get("event_types"):
                kwargs["event_types"] = arguments.get("event_types")
            if arguments.get("since_date"):
                kwargs["since_date"] = arguments.get("since_date")
            if arguments.get("min_confidence") is not None:
                kwargs["min_confidence"] = arguments.get("min_confidence")
            
            try:
                result = cli_db.get_filtered_evolution(project_path, node_id, **kwargs)
                return [types.TextContent(type="text", text=result)]
                
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Error executing get_filtered_evolution: {str(e)}"
                )]
        
        elif name == "debug_query_tools":
            project_path = arguments.get("project_path")
            
            try:
                result = cli_db.debug_query_tools(project_path)
                return [types.TextContent(type="text", text=result)]
                
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Error executing debug_query_tools: {str(e)}"
                )]
        
        else:
            return [types.TextContent(
                type="text",
                text=f"❌ Unknown tool: {name}"
            )]
    
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Error executing {name}: {str(e)}"
        )]

async def main():
    """Run the working MCP server."""
    print("🚀 Starting SVCS Working MCP Server...")
    print("📡 Server ready for IDE connections")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())

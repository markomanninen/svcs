#!/usr/bin/env python3
"""
SVCS MCP Server

Provides repository-local semantic analysis through the Model Context Protocol,
enabling AI integration with git-aware semantic code analysis.
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from typing import Any, Dict, List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import mcp.types as types

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

# Add the main SVCS directory to path for new architecture imports
SVCS_ROOT = Path(__file__).parent.parent / "svcs"
sys.path.insert(0, str(SVCS_ROOT))

try:
    # Import new centralized architecture components
    from svcs_repo_local_core import RepositoryLocalMCPServer
    from svcs.centralized_utils import smart_init_svcs
    from svcs_web_repository_manager import web_repository_manager
    NEW_ARCH_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import new architecture components: {e}")
    NEW_ARCH_AVAILABLE = False

# Import SVCS API functions
try:
    from svcs.api import (
        search_events_advanced, get_recent_activity, search_semantic_patterns,
        get_filtered_evolution, debug_query_tools, get_commit_summary,
        get_commit_changed_files, get_repository_status
    )
    API_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import SVCS API functions: {e}")
    API_AVAILABLE = False

# Initialize components
if NEW_ARCH_AVAILABLE:
    # Use new architecture
    mcp_server = RepositoryLocalMCPServer()
    COMPONENTS_AVAILABLE = True
elif API_AVAILABLE:
    # Use SVCS API functions directly
    mcp_server = None
    COMPONENTS_AVAILABLE = True
else:
    # No components available
    print("Warning: No SVCS components available", file=sys.stderr)
    mcp_server = None
    COMPONENTS_AVAILABLE = False

# Create MCP server
server = Server("svcs-working-mcp")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """
    List available MCP tools - optimized for chat interfaces.
    
    This toolset has been carefully curated for LLM chat interfaces like Claude 
    and VS Code Chat. The focus is on information retrieval and semantic analysis
    rather than setup operations or tools that produce excessive output.
    
    Chat-appropriate criteria:
    - Quick information retrieval
    - Digestible output formats  
    - Support for conversational Q&A workflows
    - No complex setup or admin operations
    - Reasonable response sizes for chat UI
    """
    return [
        # === PROJECT OVERVIEW & STATISTICS ===
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
                    "project_path": {"type": "string", "description": "Project path"}
                },
                "required": ["project_path"]
            }
        ),
        
        # === SEMANTIC EVENT QUERIES ===
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
                    "since_date": {"type": "string", "description": "Date filter (YYYY-MM-DD or 'N days ago') (optional)"},
                    "limit": {"type": "number", "description": "Max results (default 10)"}
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
                    "author": {"type": "string", "description": "Author filter (optional)"},
                    "limit": {"type": "number", "description": "Max results (default 10)"}
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
                    "limit": {"type": "number", "description": "Max results (default 5)"}
                },
                "required": ["project_path", "pattern_type"]
            }
        ),
        
        # === CODE EVOLUTION TRACKING ===
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
                    "limit": {"type": "number", "description": "Max results (default 5)"}
                },
                "required": ["project_path", "node_id"]
            }
        ),
        
        # === COMMIT ANALYSIS ===
        Tool(
            name="get_commit_summary",
            description="Get comprehensive summary of a commit including metadata, changed files, and semantic events",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "Project path"},
                    "commit_hash": {"type": "string", "description": "Commit hash (full or short)"}
                },
                "required": ["project_path", "commit_hash"]
            }
        ),
        Tool(
            name="get_commit_changed_files",
            description="Get the list of files that were changed in a specific commit",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "Project path"},
                    "commit_hash": {"type": "string", "description": "Commit hash (full or short)"}
                },
                "required": ["project_path", "commit_hash"]
            }
        ),
        
        # === DEBUG & DIAGNOSTICS ===
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
    
    def format_events_result(events: List[Dict], title: str) -> str:
        """Helper function to format events consistently."""
        if not events:
            return f"📊 {title}: No events found."
        
        result = f"📊 **{title}** ({len(events)} found)\n\n"
        for event in events:
            result += f"• **{event.get('event_type', 'unknown')}**\n"
            if event.get('node_id'):
                result += f"  - Node: `{event['node_id']}`\n"
            if event.get('location'):
                result += f"  - Location: `{event['location']}`\n"
            if event.get('details'):
                result += f"  - Details: {event['details']}\n"
            if event.get('author'):
                result += f"  - Author: {event['author']}\n"
            if event.get('commit_hash'):
                result += f"  - Commit: `{event['commit_hash'][:8]}...`\n"
            if event.get('layer'):
                result += f"  - Layer: {event['layer']}\n"
            if event.get('confidence'):
                result += f"  - Confidence: {event['confidence']}\n"
            result += "\n"
        return result
    
    def change_to_project_dir(project_path: str):
        """Helper to change to project directory for API calls."""
        original_cwd = os.getcwd()
        os.chdir(project_path)
        return original_cwd
    
    try:
        if name == "list_projects":
            if NEW_ARCH_AVAILABLE:
                # Use new architecture
                projects = await mcp_server.list_projects()
                
                if not projects:
                    return [types.TextContent(
                        type="text", 
                        text="📋 No repositories registered with SVCS yet."
                    )]
                
                result = f"📋 **SVCS Repositories** ({len(projects)} total)\n\n"
                for project in projects:
                    result += f"• **{project.get('name', 'Unknown')}**\n"
                    result += f"  - Path: `{project.get('path', 'Unknown')}`\n"
                    result += f"  - Type: {project.get('type', 'repository-local')}\n"
                    result += f"  - Events: {project.get('events_count', 0)}\n"
                    if project.get('current_branch'):
                        result += f"  - Branch: {project['current_branch']}\n"
                    result += "\n"
                
                return [types.TextContent(type="text", text=result)]
            else:
                return [types.TextContent(
                    type="text", 
                    text="📋 Use repository-local MCP server for project listing."
                )]
        
        elif name == "get_project_statistics":
            project_path = arguments.get("project_path")
            
            if not project_path:
                return [types.TextContent(
                    type="text",
                    text="❌ Error: project_path parameter is required"
                )]
            
            try:
                original_cwd = change_to_project_dir(project_path)
                
                try:
                    status = get_repository_status()
                    
                    result = f"📊 **Statistics for Repository**\n\n"
                    result += f"- **Path**: `{project_path}`\n"
                    result += f"- **Initialized**: {status.get('initialized', False)}\n"
                    result += f"- **Current Branch**: {status.get('current_branch', 'unknown')}\n"
                    result += f"- **Total Events**: {status.get('total_events', 0)}\n"
                    result += f"- **Recent Activity**: {status.get('recent_activity_count', 0)} events in last 7 days\n"
                    
                    return [types.TextContent(type="text", text=result)]
                finally:
                    os.chdir(original_cwd)
                
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Error getting statistics: {str(e)}"
                )]
        
        elif name == "search_events_advanced":
            project_path = arguments.get("project_path")
            
            # Prepare arguments for the API function
            kwargs = {}
            if arguments.get("author"):
                kwargs["author"] = arguments.get("author")
            if arguments.get("event_types"):
                kwargs["event_types"] = arguments.get("event_types")
            if arguments.get("location_pattern"):
                kwargs["location_pattern"] = arguments.get("location_pattern")
            if arguments.get("since_date"):
                kwargs["since_date"] = arguments.get("since_date")
            if arguments.get("min_confidence") is not None:
                kwargs["min_confidence"] = arguments.get("min_confidence")
            if arguments.get("limit"):
                kwargs["limit"] = arguments.get("limit")
            
            try:
                original_cwd = change_to_project_dir(project_path)
                
                try:
                    events = search_events_advanced(**kwargs)
                    result = format_events_result(events, "Advanced Search Results")
                    return [types.TextContent(type="text", text=result)]
                finally:
                    os.chdir(original_cwd)
                
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Error executing search_events_advanced: {str(e)}"
                )]
        
        elif name == "get_recent_activity":
            project_path = arguments.get("project_path")
            
            # Prepare arguments for the API function
            kwargs = {}
            if arguments.get("days"):
                kwargs["days"] = arguments.get("days")
            if arguments.get("author"):
                kwargs["author"] = arguments.get("author")
            if arguments.get("limit"):
                kwargs["limit"] = arguments.get("limit")
            
            try:
                original_cwd = change_to_project_dir(project_path)
                
                try:
                    events = get_recent_activity(**kwargs)
                    result = format_events_result(events, "Recent Activity")
                    return [types.TextContent(type="text", text=result)]
                finally:
                    os.chdir(original_cwd)
                
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Error executing get_recent_activity: {str(e)}"
                )]
        
        elif name == "search_semantic_patterns":
            project_path = arguments.get("project_path")
            pattern_type = arguments.get("pattern_type")
            
            # Prepare arguments for the API function
            kwargs = {}
            if arguments.get("min_confidence") is not None:
                kwargs["min_confidence"] = arguments.get("min_confidence")
            if arguments.get("since_date"):
                kwargs["since_date"] = arguments.get("since_date")
            if arguments.get("limit"):
                kwargs["limit"] = arguments.get("limit")
            
            try:
                original_cwd = change_to_project_dir(project_path)
                
                try:
                    events = search_semantic_patterns(pattern_type, **kwargs)
                    result = format_events_result(events, f"Semantic Patterns: {pattern_type}")
                    return [types.TextContent(type="text", text=result)]
                finally:
                    os.chdir(original_cwd)
                
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Error executing search_semantic_patterns: {str(e)}"
                )]
        
        elif name == "get_filtered_evolution":
            project_path = arguments.get("project_path")
            node_id = arguments.get("node_id")
            
            # Prepare arguments for the API function
            kwargs = {}
            if arguments.get("event_types"):
                kwargs["event_types"] = arguments.get("event_types")
            if arguments.get("since_date"):
                kwargs["since_date"] = arguments.get("since_date")
            if arguments.get("min_confidence") is not None:
                kwargs["min_confidence"] = arguments.get("min_confidence")
            
            try:
                original_cwd = change_to_project_dir(project_path)
                
                try:
                    events = get_filtered_evolution(node_id, **kwargs)
                    result = format_events_result(events, f"Evolution: {node_id}")
                    return [types.TextContent(type="text", text=result)]
                finally:
                    os.chdir(original_cwd)
                
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Error executing get_filtered_evolution: {str(e)}"
                )]
        
        elif name == "debug_query_tools":
            project_path = arguments.get("project_path")
            
            try:
                original_cwd = change_to_project_dir(project_path)
                
                try:
                    debug_info = debug_query_tools(project_path)
                    
                    result = f"🔍 **Debug Information**\n\n"
                    result += f"- **Total Events**: {debug_info.get('total_events', 0)}\n"
                    result += f"- **Recent Events**: {debug_info.get('recent_events', 0)}\n"
                    result += f"- **Performance Events**: {debug_info.get('performance_events', 0)}\n"
                    result += f"- **High-Confidence Events**: {debug_info.get('ai_events', 0)}\n\n"
                    
                    if debug_info.get('approaches'):
                        result += "**Available Tools**:\n"
                        for approach in debug_info['approaches']:
                            result += f"- {approach}\n"
                    
                    return [types.TextContent(type="text", text=result)]
                finally:
                    os.chdir(original_cwd)
                
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Error executing debug_query_tools: {str(e)}"
                )]
        
        elif name == "get_commit_changed_files":
            project_path = arguments.get("project_path")
            commit_hash = arguments.get("commit_hash")
            
            try:
                original_cwd = change_to_project_dir(project_path)
                
                try:
                    changed_files = get_commit_changed_files(commit_hash)
                    
                    if not changed_files:
                        result = f"📄 No files changed in commit {commit_hash[:8]}"
                    else:
                        result = f"📁 **Files changed in commit {commit_hash[:8]}**:\n\n"
                        for i, file_path in enumerate(changed_files, 1):
                            result += f"{i}. {file_path}\n"
                        result += f"\nTotal: {len(changed_files)} files changed"
                    
                    return [types.TextContent(type="text", text=result)]
                finally:
                    os.chdir(original_cwd)
                    
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Error getting changed files for commit {commit_hash}: {str(e)}"
                )]
        
        elif name == "get_commit_summary":
            project_path = arguments.get("project_path")
            commit_hash = arguments.get("commit_hash")
            
            try:
                original_cwd = change_to_project_dir(project_path)
                
                try:
                    summary = get_commit_summary(commit_hash)
                    
                    result = f"📋 **Commit Summary for {commit_hash[:8]}**:\n\n"
                    
                    # Commit info
                    if 'commit_info' in summary and summary['commit_info']:
                        commit_info = summary['commit_info']
                        result += f"**Commit Information:**\n"
                        result += f"• Hash: {str(commit_info.get('hash', commit_hash))[:8]}\n"
                        result += f"• Author: {commit_info.get('author', 'Unknown')}\n"
                        result += f"• Date: {commit_info.get('date', 'Unknown')}\n"
                        result += f"• Message: {commit_info.get('message', 'No message')}\n\n"
                    
                    # Changed files
                    changed_files = summary.get('changed_files', [])
                    file_count = summary.get('file_count', len(changed_files))
                    result += f"**Changed Files ({file_count}):**\n"
                    if changed_files:
                        for file_path in changed_files:
                            result += f"• {file_path}\n"
                    else:
                        result += f"• No files found\n"
                    result += "\n"
                    
                    # Semantic events
                    semantic_events = summary.get('semantic_events', [])
                    semantic_event_count = summary.get('semantic_event_count', len(semantic_events))
                    result += f"**Semantic Events ({semantic_event_count}):**\n"
                    if semantic_events:
                        for event in semantic_events:
                            event_type = event.get('event_type', 'unknown')
                            node_id = event.get('node_id', '')
                            location = event.get('location', '')
                            layer = event.get('layer', 'core')
                            result += f"• {event_type}"
                            if node_id:
                                result += f" ({node_id})"
                            if layer != 'core':
                                result += f" [Layer {layer}]"
                            if location:
                                result += f" in {location}"
                            result += "\n"
                    else:
                        result += "• No semantic events detected\n"
                    
                    return [types.TextContent(type="text", text=result)]
                finally:
                    os.chdir(original_cwd)
                    
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                return [types.TextContent(
                    type="text",
                    text=f"❌ Error getting commit summary for {commit_hash}: {str(e)}\n\nDetailed error:\n{error_details}"
                )]
        
        else:
            return [types.TextContent(
                type="text",
                text=f"❌ Unknown tool: {name}"
            )]
    
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ MCP tool error: {str(e)}"
        )]


async def main():
    """Main function to run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

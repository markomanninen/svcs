# FILE: svcs_repo_discuss.py
#
# Enhanced conversational REPL for SVCS with full repository integration
# 🎯 SINGLE REPOSITORY FOCUSED - Works only with the current initialized repo
#
# 📋 FEATURES:
# • Semantic code evolution analysis with conversational AI
# • Team collaboration insights and patterns
# • Full conversation context maintained (increases token usage)
# • Detailed logging with metrics in .svcs/logs/
#
# 🔄 FOR MULTI-REPOSITORY: Use the MCP server architecture in svcs_mcp/
#
# Prerequisites:
# 1. Run `export GOOGLE_API_KEY="YOUR_API_KEY"` in your terminal
# 2. Ensure SVCS is initialized with `svcs init` for full functionality
# 3. Note: This is experimental and consumes Google API tokens
#
# 📊 LOGS: All prompts, responses, and metrics stored in .svcs/logs/
#
# Usage:
#   python3 svcs_repo_discuss.py

import os
import sys
import json
from pathlib import Path
from datetime import datetime

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

# Import all API functions from the centralized API
try:
    from svcs.api import *
except ImportError:
    # Fallback if svcs package is not in path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'svcs'))
    from api import *

# Enhanced logger class for LLM interactions
class LLMLogger:
    def __init__(self):
        self.log_dir = Path(".svcs/logs")
        self.log_dir.mkdir(exist_ok=True)
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.log_file = self.log_dir / f"svcs_repo_discuss_{self.today}.jsonl"
        self.error_file = self.log_dir / f"svcs_repo_discuss_errors_{self.today}.jsonl"
    
    def log_inference(self, prompt, response, model="gemini-1.5-flash", tools_used=False, mode="single_query"):
        """Log a successful LLM interaction."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "component": "svcs_repo_discuss",
            "model": model,
            "prompt": prompt,
            "response": response,
            "metadata": {
                "prompt_length": len(prompt),
                "response_length": len(response),
                "tools_used": tools_used,
                "svcs_enhanced": True,
                "mode": mode
            }
        }
        
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def log_error(self, prompt, error, model="gemini-1.5-flash", mode="single_query"):
        """Log an error during LLM interaction."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "component": "svcs_repo_discuss",
            "model": model,
            "prompt": prompt,
            "error": str(error),
            "metadata": {
                "prompt_length": len(prompt),
                "svcs_enhanced": True,
                "mode": mode
            }
        }
        
        with open(self.error_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

try:
    llm_logger = LLMLogger()
    API_AVAILABLE = True
    
except ImportError as e:
    print(f"Error: Could not import required components: {e}")
    print("Please ensure Python sqlite3 module is available.")
    sys.exit(1)

# --- LLM and Tool Setup ---

try:
    import google.generativeai as genai
except ImportError:
    print("Error: The 'google-generativeai' library is not installed.")
    print("Please run: ./.svcs/venv/bin/pip install google-generativeai")
    sys.exit(1)

console = Console()

def check_svcs_status():
    """Check SVCS initialization and repository status."""
    svcs_dir = Path('.svcs')
    git_dir = Path('.git')
    
    status = {
        'svcs_initialized': svcs_dir.exists() and (svcs_dir / 'config.json').exists(),
        'git_repository': git_dir.exists(),
        'semantic_db': (svcs_dir / 'semantic.db').exists() if svcs_dir.exists() else False,
        'hooks_installed': False,
        'notes_available': False
    }
    
    # Check for git hooks
    if git_dir.exists():
        hooks_dir = git_dir / 'hooks'
        post_commit = hooks_dir / 'post-commit'
        post_merge = hooks_dir / 'post-merge'
        status['hooks_installed'] = post_commit.exists() and post_merge.exists()
    
    # Check for semantic notes
    try:
        import subprocess
        result = subprocess.run(['git', 'notes', '--ref=refs/notes/svcs-semantic', 'list'], 
                              capture_output=True, text=True)
        status['notes_available'] = result.returncode == 0 and result.stdout.strip()
    except:
        pass
    
    return status

def display_startup_info():
    """Display startup information and repository status."""
    status = check_svcs_status()
    
    # Create status table
    table = Table(title="SVCS Repository Status", show_header=True)
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Notes", style="yellow")
    
    # Add status rows
    table.add_row(
        "Git Repository", 
        "✅ Ready" if status['git_repository'] else "❌ Missing",
        "Required for SVCS operation"
    )
    
    table.add_row(
        "SVCS Initialized", 
        "✅ Ready" if status['svcs_initialized'] else "❌ Missing",
        "Run 'svcs init' if missing" if not status['svcs_initialized'] else "Centralized configuration active"
    )
    
    table.add_row(
        "Semantic Database", 
        "✅ Ready" if status['semantic_db'] else "⚠️  Empty",
        "Contains local semantic events" if status['semantic_db'] else "Will be created on first analysis"
    )
    
    table.add_row(
        "Git Hooks", 
        "✅ Installed" if status['hooks_installed'] else "❌ Missing",
        "Automatic semantic sync enabled" if status['hooks_installed'] else "Manual sync required"
    )
    
    table.add_row(
        "Semantic Notes", 
        "✅ Available" if status['notes_available'] else "ℹ️  None",
        "Team semantic data available" if status['notes_available'] else "First repository or no team data yet"
    )
    
    console.print(table)
    console.print()
    
    # Display important information
    console.print(Panel(
        "[bold yellow]📋 IMPORTANT NOTES:[/bold yellow]\n\n"
        "🎯 [bold]Single Repository Focus[/bold]: This tool works only with the current repository\n"
        "🔄 [bold]Multi-Repository?[/bold] Use the MCP server architecture in 'svcs_mcp/' instead\n"
        "💬 [bold]Conversation Context[/bold]: Full chat history sent with each query (token expensive)\n"
        "📊 [bold]Detailed Logs[/bold]: All activity logged to .svcs/logs/ with metrics\n"
        "🧪 [bold]Experimental[/bold]: Requires Google API key and consumes tokens",
        title="Usage Information",
        border_style="yellow"
    ))
    console.print()
    
    # Display recommendations
    if not status['svcs_initialized']:
        console.print(Panel(
            "[bold red]⚠️  SVCS not initialized![/bold red]\n\n"
            "Run [bold cyan]svcs init[/bold cyan] to enable:\n"
            "• Automatic semantic analysis\n"
            "• Team semantic data sync\n"
            "• Git hooks for seamless collaboration",
            title="Recommendation",
            border_style="red"
        ))
    elif not status['hooks_installed']:
        console.print(Panel(
            "[bold yellow]⚠️  Git hooks not installed![/bold yellow]\n\n"
            "Run [bold cyan]svcs init --force[/bold cyan] to install hooks for:\n"
            "• Automatic semantic note sync\n"
            "• Seamless team collaboration",
            title="Recommendation",
            border_style="yellow"
        ))
    else:
        console.print(Panel(
            "[bold green]✅ SVCS fully configured![/bold green]\n\n"
            "• Semantic analysis active\n"
            "• Team sync enabled\n"
            "• Ready for conversational queries",
            title="Status",
            border_style="green"
        ))

def configure_llm():
    """Configures the Gemini model from the environment API key."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        console.print("[bold red]Error: GOOGLE_API_KEY environment variable not set.[/bold red]")
        console.print("Please get a key from https://aistudio.google.com/app/apikey and run 'export GOOGLE_API_KEY=...'")
        sys.exit(1)
    genai.configure(api_key=api_key)

def get_system_instruction():
    """Get the enhanced system instruction with awareness of SVCS features."""
    return """
You are the SVCS Semantic VCS Assistant, an expert software archeologist with deep knowledge
of collaborative development workflows. You help developers understand their codebase evolution
and leverage SVCS's seamless semantic transfer capabilities.

SVCS COLLABORATION AWARENESS:
You are working in a repository with SVCS's seamless semantic transfer system. This means:
- Semantic analysis happens automatically on every commit via git hooks
- Semantic notes are synchronized across the team automatically
- Developers can access the full semantic history without manual intervention
- The semantic database contains insights from all team members

AVAILABLE TOOLS:

1. **search_events_advanced** - Comprehensive filtering by date, author, confidence, layers, event types
   Use for complex queries like "show me all performance optimizations by John since last week"
   Parameters: event_types, author, since_date, layers, min_confidence, limit, order_by

2. **get_recent_activity** - Quick access to recent changes with team context
   Use for "what happened recently?" or "recent changes" or "team activity last week"
   Parameters: days, limit, author, layers

3. **search_semantic_patterns** - Find AI-detected architectural and performance patterns
   Use for "show me architecture changes" or "performance optimizations" or "error handling patterns"
   IMPORTANT: Available pattern types include:
   - "performance" - performance optimizations and bottlenecks
   - "architecture" - architectural patterns and design changes
   - "error_handling" - exception handling and error patterns
   - "refactoring" - code refactoring patterns
   
4. **get_project_statistics** - Overview and team collaboration metrics
   Use for "project summary" or "team statistics" or "what types of changes happen most?"

5. **get_node_evolution** - Complete history of a specific function/class
   Use for "tell me the story of func:greet" or "how did class:DatabaseManager evolve?"

6. **get_filtered_evolution** - Filtered evolution history with team context
   Use for "show only signature changes for func:greet since June" or "evolution by specific author"

7. **debug_query_tools** - Diagnostic tool when queries return no results
   Use when you get no results to understand the data structure and available options

8. **get_commit_changed_files** - Files changed in specific commits
   Use for "what files were changed in commit abc123?" or "show me files in that commit"

9. **get_commit_diff** - Actual git diff for commits
   Use for "show me the diff for commit abc123" or "what were the actual changes?"
   IMPORTANT: Present diff output in code blocks without interpretation

10. **get_commit_summary** - Comprehensive commit information with semantic context
    Use for "tell me everything about commit abc123" or "analyze that commit"

11. **compare_branches** - Compare semantic events between two branches
    Use for "compare main and feature branches" or "what differs between branches"
    Parameters: branch1, branch2, limit

12. **generate_analytics** - Generate comprehensive analytics reports
    Use for "generate analytics report" or "project analytics summary"
    Parameters: branch, output_format, since_date, until_date

13. **analyze_quality** - Analyze code quality trends and patterns
    Use for "analyze code quality" or "quality trends over time"
    Parameters: verbose, since_date, branch

14. **get_branch_events** - Get semantic events for a specific branch
    Use for "show me events in feature branch" or "what happened in branch X"
    Parameters: branch, limit

15. **get_repository_status** - Get comprehensive repository status and SVCS configuration
    Use for "repository status" or "SVCS status check"

11. **compare_branches** - Compare semantic events between branches
    Use for "what's different between main and feature branches?" or "compare changes in two branches"
    Parameters: branch1, branch2, limit

12. **generate_analytics** - Generate analytics report for the repository
    Use for "show me the project analytics" or "generate a report of recent changes"
    Parameters: branch, output_format, since_date, until_date

13. **analyze_quality** - Analyze code quality trends and patterns
    Use for "how is the code quality?" or "show me quality improvements over time"
    Parameters: verbose, since_date, branch

ENHANCED QUERY STRATEGIES:

For TEAM COLLABORATION queries:
- Use author parameter to filter by specific team members
- Combine recent_activity with author filtering for team insights
- Look for patterns across different team members' contributions

For PERFORMANCE queries:
- ALWAYS try search_semantic_patterns(pattern_type="performance") first
- If no results, try search_events_advanced(event_types=["abstract_performance_optimization"])
- Consider lowering min_confidence to 0.5-0.6 for broader results

For ARCHITECTURE queries:
- Use search_semantic_patterns(pattern_type="architecture") for high-level patterns
- Use search_events_advanced with layer filters for specific architectural layers
- Combine with evolution queries to show architectural progression

For TEMPORAL queries:
- Use since_date in "YYYY-MM-DD" format or relative terms like "7 days ago"
- For team activity over time, use get_recent_activity with different day ranges
- Compare different time periods for trend analysis

RESPONSE GUIDELINES:
- Always provide context about team collaboration and semantic transfer
- Limit results to 10-20 items by default to avoid overwhelming output
- Group similar events and create narrative stories about code evolution
- Highlight team contributions and collaborative patterns
- Include confidence scores for AI-detected events
- Format results with clear markdown tables and sections
- **For diffs: Show raw output in code blocks without interpretation**
- Suggest follow-up queries based on discovered patterns

TROUBLESHOOTING APPROACH:
1. If no results found, FIRST call debug_query_tools() to understand available data
2. Try multiple search strategies:
   - Different tool functions (events vs patterns vs activity)
   - Lower confidence thresholds (0.5 instead of 0.7)
   - Broader date ranges or no date filters
   - Alternative search terms or event types
3. Explain what was searched and suggest specific alternatives
4. Use debug information to guide refined searches

TEAM INSIGHTS:
- Always consider the collaborative context when analyzing code changes
- Highlight how different team members contribute to different aspects (architecture, performance, features)
- Point out semantic patterns that emerge from team collaboration
- Suggest ways the team can leverage semantic insights for better development
"""

def main():
    """The main entry point for the enhanced conversational REPL."""
    console.print(Panel(
        "[bold cyan]SVCS Enhanced Conversational Assistant[/bold cyan]\n"
        "Semantic analysis • Team collaboration • Repository insights",
        title="Welcome",
        border_style="cyan"
    ))
    
    # Check and display repository status
    display_startup_info()
    
    configure_llm()
    
    # Set up the Gemini Pro model with all available tools
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        tools=[
            # Core SVCS tools
            find_dependency_changes, 
            get_commit_details, 
            get_full_log, 
            get_node_evolution,
            # Enhanced conversational tools
            search_events_advanced,
            get_recent_activity,
            get_project_statistics,
            search_semantic_patterns,
            get_filtered_evolution,
            debug_query_tools,
            # Git integration tools
            get_commit_changed_files,
            get_commit_diff,
            get_commit_summary,
            # CLI Feature Parity tools
            compare_branches,
            generate_analytics,
            analyze_quality,
            get_branch_events,
            get_repository_status
        ],
        system_instruction=get_system_instruction()
    )

    console.print("\n[bold green]🚀 Ready for questions![/bold green] Ask about your code's history, team collaboration, or semantic patterns.")
    console.print("[bold yellow]💡 Context:[/bold yellow] Full conversation history is maintained (increases token usage with each exchange)")
    console.print("[bold blue]📊 Logs:[/bold blue] All activity logged to .svcs/logs/ with detailed metrics")
    console.print("[dim]Type 'exit', 'quit', or press Ctrl+C to end the session.[/dim]\n")

    chat_session = model.start_chat(enable_automatic_function_calling=True)

    # Enhanced example queries with specific use cases
    example_queries = [
        # Quick overview queries
        "What happened in this project in the last 7 days?",
        "Show me recent activity by all team members",
        "What types of changes happen most often in this codebase?",
        
        # Performance and architecture
        "Find all performance optimizations in the last month",
        "Show me architectural changes and refactoring patterns",
        "What error handling improvements have been made?",
        
        # Team collaboration
        "Who has been working on database-related code?",
        "Show me John's contributions to authentication features",
        "What patterns emerge from different team members' coding styles?",
        
        # Code evolution
        "How has the main API evolved over time?",
        "Tell me the story of func:authenticate",
        "Show me all changes to class:UserManager",
        
        # Commit analysis
        "Analyze the latest commit in detail",
        "What files were changed in commit abc123?",
        "Show me the diff for the most recent performance change",
        
        # Branch comparison
        "Compare the main and feature branches",
        "What are the differences between branch1 and branch2?",
        
        # Analytics and quality
        "Generate an analytics report for the last month",
        "Show me the code quality trends over time",
        "What recommendations do you have for improving code quality?"
    ]
    
    console.print(Panel(
        "💡 [bold]Example queries to try:[/bold]\n" + 
        "\n".join(f"• {query}" for query in example_queries),
        title="Getting Started",
        border_style="blue"
    ))
    console.print()

    while True:
        try:
            user_input = console.input("[bold green]❓ You: [/bold green]")
            if user_input.lower() in ["quit", "exit", "q"]:
                console.print("\n[bold cyan]👋 Goodbye! Happy coding![/bold cyan]")
                break
            
            if not user_input.strip():
                continue
            
            # Show thinking indicator
            with console.status("[bold blue]🤔 Analyzing your query..."):
                try:
                    response = chat_session.send_message(user_input)
                    
                    # Log successful inference
                    llm_logger.log_inference(
                        prompt=user_input,
                        response=response.text,
                        model="gemini-1.5-flash",
                        tools_used=bool(getattr(response, 'function_calls', None)),
                        mode="interactive"
                    )
                    
                except Exception as e:
                    # Log error
                    llm_logger.log_error(
                        prompt=user_input,
                        error=str(e),
                        model="gemini-1.5-flash",
                        mode="interactive"
                    )
                    raise
            
            console.print("\n[bold blue]🔍 Assistant:[/bold blue]")
            console.print(Markdown(response.text))
            console.print("\n" + "─" * 50 + "\n")

        except KeyboardInterrupt:
            console.print("\n\n[bold cyan]👋 Session interrupted. Goodbye![/bold cyan]")
            break
        except Exception as e:
            console.print(f"\n[bold red]❌ An unexpected error occurred: {e}[/bold red]")
            console.print("[dim]You can continue asking questions or type 'exit' to quit.[/dim]\n")

def process_query(query):
    """Process a single query and return the response."""
    configure_llm()
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        tools=[
            # Core SVCS tools
            find_dependency_changes, 
            get_commit_details, 
            get_full_log, 
            get_node_evolution,
            # Enhanced conversational tools
            search_events_advanced,
            get_recent_activity,
            get_project_statistics,
            search_semantic_patterns,
            get_filtered_evolution,
            debug_query_tools,
            # Git integration tools
            get_commit_changed_files,
            get_commit_diff,
            get_commit_summary,
            # CLI Feature Parity tools
            compare_branches,
            generate_analytics,
            analyze_quality,
            get_branch_events,
            get_repository_status
        ],
        system_instruction=get_system_instruction()
    )
    
    try:
        chat_session = model.start_chat(enable_automatic_function_calling=True)
        response = chat_session.send_message(query)
        
        # Log successful inference
        llm_logger.log_inference(
            prompt=query,
            response=response.text,
            model="gemini-1.5-flash",
            tools_used=bool(getattr(response, 'function_calls', None)),
            mode="single_query"
        )
        
        return response.text
        
    except Exception as e:
        # Log error
        llm_logger.log_error(
            prompt=query,
            error=str(e),
            model="gemini-1.5-flash",
            mode="single_query"
        )
        return f"Error processing query: {e}"

def start_interactive_session():
    """Start an interactive conversational session."""
    main()


if __name__ == "__main__":
    main()

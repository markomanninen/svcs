# FILE: svcs_discuss.py
#
# This is the conversational REPL for SVCS.
# This version has an enhanced system prompt for better narrative summarization.
#
# Prerequisites:
# 1. Run `export GOOGLE_API_KEY="YOUR_API_KEY"` in your terminal.
#
# Usage:
#   python3 svcs_discuss.py

import os
import sys

# --- Environment Self-Correction ---
VENV_PYTHON_PATH = os.path.abspath(os.path.join('.svcs', 'venv', 'bin', 'python3'))
if sys.executable != VENV_PYTHON_PATH:
    try:
        os.execv(VENV_PYTHON_PATH, [VENV_PYTHON_PATH] + sys.argv)
    except OSError:
        print(f"Error: Could not execute the script with the correct interpreter at '{VENV_PYTHON_PATH}'")
        sys.exit(1)
# --- End Self-Correction ---


from rich.console import Console
from rich.markdown import Markdown

sys.path.insert(0, '.svcs')
try:
    # Import all the specific API functions including new enhanced ones
    from api import (
        find_dependency_changes, 
        get_commit_details, 
        get_full_log,
        get_node_evolution,
        # New enhanced functions for conversational interface
        search_events_advanced,
        get_recent_activity,
        get_project_statistics,
        search_semantic_patterns,
        get_filtered_evolution,
        debug_query_tools,
        # New git integration functions
        get_commit_changed_files,
        get_commit_diff,
        get_commit_summary
    )
    # Import LLM logger
    from llm_logger import llm_logger
except ImportError:
    print("Error: Could not import from '.svcs/api.py'. Please ensure the file exists.")
    sys.exit(1)

# --- LLM and Tool Setup ---

try:
    import google.generativeai as genai
except ImportError:
    print("Error: The 'google-generativeai' library is not installed.")
    print("Please run: ./.svcs/venv/bin/pip install google-generativeai")
    sys.exit(1)

console = Console()

def configure_llm():
    """Configures the Gemini model from the environment API key."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        console.print("[bold red]Error: GOOGLE_API_KEY environment variable not set.[/bold red]")
        console.print("Please get a key from https://aistudio.google.com/app/apikey and run 'export GOOGLE_API_KEY=...'")
        sys.exit(1)
    genai.configure(api_key=api_key)

def main():
    """The main entry point for the conversational REPL."""
    configure_llm()
    
    # Enhanced system prompt for better conversational search capabilities
    system_instruction = """
You are the SVCS Semantic VCS Assistant, an expert software archeologist. Your
purpose is to help developers understand the history of their codebase by telling
clear, concise stories about how the code evolved.

You have access to powerful search and analysis tools:

1. **search_events_advanced** - Comprehensive filtering by date, author, confidence, layers, etc.
   Use for complex queries like "show me performance optimizations by John in the last week"

2. **get_recent_activity** - Quick access to recent changes
   Use for "what happened recently?" or "recent changes by X"

3. **search_semantic_patterns** - Find specific AI-detected patterns
   Use for "show me architecture changes" or "performance optimizations"
   IMPORTANT: For performance queries, use pattern_type="performance" which maps to "abstract_performance_optimization" events

4. **get_project_statistics** - Overview and summary information
   Use for "project summary" or "what types of changes happen most?"

5. **get_node_evolution** - Complete history of a specific function/class
   Use for "tell me the story of func:greet"

6. **get_filtered_evolution** - Filtered evolution history
   Use for "show only signature changes for func:greet since June"

7. **debug_query_tools** - Diagnostic tool when queries return no results
   Use when you get no results for a reasonable query to understand why

8. **get_commit_changed_files** - Get list of files changed in a specific commit
   Use for "what files were changed in commit abc123?" or "show me files in that commit"

9. **get_commit_diff** - Get actual git diff for a commit (optionally filtered to specific file)
   Use for "show me the diff for commit abc123" or "what were the actual changes in that commit?"
   Include file_path parameter to filter to specific file: get_commit_diff(commit_hash, file_path="path/to/file.py")
   IMPORTANT: When showing diff output, present it in a code block without interpretation or summary

10. **get_commit_summary** - Comprehensive commit information including metadata, files, and semantic events
    Use for "tell me everything about commit abc123" or "summarize that commit"

CRITICAL TOOL USAGE GUIDELINES:

For PERFORMANCE OPTIMIZATION queries:
- ALWAYS try search_semantic_patterns(pattern_type="performance") first
- If that returns no results, try search_events_advanced(event_types=["abstract_performance_optimization"])
- Consider lowering min_confidence to 0.5 or 0.6 to catch more results
- Check recent activity with get_recent_activity() and filter for performance events

For DATE-BASED queries:
- Use since_date parameter in format "YYYY-MM-DD" or relative terms like "7 days ago"
- For "last week" use since_date with a date 7 days ago
- For "recent" use get_recent_activity(days=7) or similar

RESPONSE GUIDELINES:
- Always limit results to 10-20 items by default to avoid overwhelming output
- If no results found, suggest trying with lower confidence thresholds or broader search terms
- Group similar events and tell a narrative story, don't just list events
- Format results clearly with markdown tables when appropriate
- Include readable dates, confidence scores for AI events
- Offer follow-up suggestions based on results
- **IMPORTANT: For get_commit_diff results, show the raw diff output in a code block without interpretation**

TROUBLESHOOTING:
- If you get no results for a reasonable query, FIRST call debug_query_tools() to understand the data available
- Then try multiple approaches:
  1. Different tool functions
  2. Lower confidence thresholds (try 0.5 or 0.6 instead of 0.7+)
  3. Broader date ranges
  4. Alternative search terms
- Always explain what you searched for and suggest alternatives if no results found
- Use the debug information to guide your alternative search strategies
"""

    # Set up the Gemini Pro model with enhanced tools
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        tools=[
            # Core tools
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
            # New git integration tools
            get_commit_changed_files,
            get_commit_diff,
            get_commit_summary
        ],
        system_instruction=system_instruction
    )

    console.print("[bold cyan]Welcome to the SVCS Conversational Assistant.[/bold cyan]")
    console.print("Ask questions about your code's history. Type 'exit' or 'quit' to end.")

    chat_session = model.start_chat(enable_automatic_function_calling=True)

    while True:
        try:
            user_input = console.input("[bold green]You: [/bold green]")
            if user_input.lower() in ["quit", "exit"]:
                console.print("[bold cyan]Goodbye![/bold cyan]")
                break
            
            # Log the prompt before sending
            try:
                response = chat_session.send_message(user_input)
                
                # Log successful inference
                llm_logger.log_inference(
                    component="svcs_discuss",
                    prompt=user_input,
                    response=response.text,
                    model="gemini-1.5-flash",
                    metadata={
                        "prompt_length": len(user_input),
                        "response_length": len(response.text),
                        "tools_used": bool(getattr(response, 'function_calls', None))
                    }
                )
                
            except Exception as e:
                # Log error
                llm_logger.log_error(
                    component="svcs_discuss",
                    prompt=user_input,
                    error=str(e),
                    model="gemini-1.5-flash",
                    metadata={"prompt_length": len(user_input)}
                )
                raise
            
            console.print("\n[bold blue]Assistant:[/bold blue]")
            console.print(Markdown(response.text))
            console.print("-" * 20)

        except KeyboardInterrupt:
            console.print("\n[bold cyan]Goodbye![/bold cyan]")
            break
        except Exception as e:
            console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")
            break

if __name__ == "__main__":
    main()

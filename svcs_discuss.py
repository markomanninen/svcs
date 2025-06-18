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
    # Import all the specific API functions
    from api import (
        find_dependency_changes, 
        get_commit_details, 
        get_full_log,
        get_node_evolution
    )
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
    
    # NEW: Enhanced system prompt for better summarization.
    system_instruction = """
You are the SVCS Semantic VCS Assistant, an expert software archeologist. Your
purpose is to help developers understand the history of their codebase by telling
clear, concise stories about how the code evolved.

You must use the provided tools to find semantic events. When asked for a history
or evolution of a node, use the `get_node_evolution` tool.

Synthesize the list of events into a high-level narrative. Do not just list every
single event. Instead, group similar changes. For example, instead of listing five
separate signature changes, summarize them as 'The function signature was changed
multiple times, eventually stabilizing with the arguments...'.

Always start with the creation event and end with the last known modification or
removal. Be concise and use markdown for clarity.
"""

    # Set up the Gemini Pro model with the enhanced system prompt.
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        tools=[find_dependency_changes, get_commit_details, get_full_log, get_node_evolution],
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
            
            response = chat_session.send_message(user_input)
            
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

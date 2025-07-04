from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console()

# ASCII Art
WELCOME_BANNER = """
*********************************************************
*                                                       *
*       Welcome to the SVCS Interactive Project Tour!   *
*                                                       *
*********************************************************
"""

PROJECT_SETUP_ICON = """
    .--.
   |o_o |
   |:_/ |
  //   \\ \\
 (|     | )
/'\\_   _/`\\
\\___)=(___/
"""

SVCS_INIT_ICON = """
  .--.  .--.
 (    )(    )
  `--'  `--'
  .-..-.
 (      )
  `-..-'
"""

FILE_ICON = """
__________
/         /|
/_________/ |
|         | |
|  main.py| /
|_________|/
"""

GIT_COMMIT_ICON = """
* --- * --- * (commit)
      |
      * (HEAD)
"""

MENU_BANNER = """
====================================
|          SVCS Tour Menu          |
====================================
"""

FAREWELL_BANNER = """
*********************************************************
*                                                       *
*            Thanks for using the SVCS Tour!            *
*              Happy Coding! (`\\(^_^)/`)                 *
*                                                       *
*********************************************************
"""

# Helper functions
def print_art(art_string, style="bold magenta"):
    console.print(Text(art_string, style=style))

def print_step_header(message):
    console.print(Panel(Text(message, justify="center", style="bold cyan")))

def print_info(message):
    console.print(f"[info]ℹ️ {message}[/info]", style="blue")

def print_command(command_str):
    console.print(f"[command]$ {command_str}[/command]", style="bold green")

def print_success(message):
    console.print(f"[success]✅ {message}[/success]", style="green")

def print_warning(message):
    console.print(f"[warning]⚠️ {message}[/warning]", style="yellow")

def print_error(message):
    console.print(f"[error]❌ {message}[/error]", style="red")

def ask_prompt(prompt_message, default=None, choices=None):
    # Remove unsupported rich markup tags from the prompt string
    return Prompt.ask(f"❓ {prompt_message}", default=default, choices=choices)

def ask_confirm(prompt_message, default=True):
    # Remove unsupported rich markup tags from the confirm string
    return Confirm.ask(f"❓ {prompt_message}", default=default)

def print_file_content(file_path, header=None):
    if header is None:
        header = f"Contents of {file_path.name}"
    try:
        content = file_path.read_text()
        console.print(Panel(content, title=Text(header, style="bold yellow"), expand=False))
    except Exception as e:
        print_error(f"Could not read file {file_path}: {e}")

COMMAND_DOCS = {
    "status": "Shows the current SVCS status of the repository, including untracked semantic changes and hook status.",
    "events": "Lists semantic events recorded by SVCS, showing what changes have been analyzed. Can be filtered.",
    "config": "Manages SVCS configuration. `svcs config list` shows current settings.",
    "search": "Allows searching for specific semantic patterns or events in the project's history.",
    "init": "Initializes SVCS in a Git repository, setting up .svcs directory, database, and Git hooks."
}

if __name__ == '__main__':
    # Demo of utils
    print_art(WELCOME_BANNER)
    print_step_header("Step 1: Project Setup")
    print_info("This is an informational message.")
    print_command("git init")
    print_success("Project initialized successfully!")
    print_warning("This is a warning.")
    print_error("Something went wrong!")

    # name = ask_prompt("Enter your name", default="User")
    # console.print(f"Hello, {name}!")

    # if ask_confirm("Proceed with caution?"):
    #     print_info("Proceeding...")
    # else:
    #     print_warning("Aborted.")

    print_art(SVCS_INIT_ICON, style="bold yellow")
    print_art(FAREWELL_BANNER)

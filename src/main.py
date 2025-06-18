# FILE: src/main.py (Comprehensive Test Version)

import sys  # NEW dependency
# The 'os' dependency has been removed.

# The 'get_system_info' function has been removed.

def log_error(error_message):
    """A new function to log errors."""
    print(f"ERROR: {error_message}", file=sys.stderr)

def greet(name, salutation="Greetings"): # SIGNATURE changed
    """
    Greets the user and demonstrates multiple semantic changes.
    """
    # CONTROL FLOW and EXCEPTION HANDLING added
    try:
        # INTERNAL CALL added
        message = f"{salutation}, {name}!"
        for i in range(2): # New 'for' loop
            print(f"({i+1}) {message}")
        
        # The unconditional call to get_system_info is removed.
        return message

    except TypeError as e:
        # INTERNAL CALL added
        log_error(f"Invalid type for greet: {e}")
        return None

if __name__ == "__main__":
    greet("Alice")
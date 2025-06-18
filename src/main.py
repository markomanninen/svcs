# FILE: src/main.py

import os

def get_system_info():
    """A new function to get system information."""
    return f"You are using the '{os.name}' operating system."

def greet(name="world", punctuation="!", show_details=False):
    """Greets the user and includes system details if requested."""
    message = f"A hearty hello to {name}{punctuation}" 
    if show_details:
        # This new line calls another function within the same file.
        message += f"\n{get_system_info()}"
    print(message)
    return message

if __name__ == "__main__":
    # To test the new logic, let's call it with show_details=True
    greet(show_details=True)
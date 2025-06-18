# FILE: src/main.py

import os

def get_system_info():
    """A new function to get system information."""
    return f"You are using the '{os.name}' operating system."

def greet(name="world", punctuation="!"):
    """Greets the user and ALWAYS includes system details."""
    
    system_details = get_system_info()
    
    message = f"A hearty hello to {name}{punctuation}\n{system_details}"
    
    print(message)
    return message

if __name__ == "__main__":
    greet()
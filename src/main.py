# FILE: src/main.py

import math

def greet(name="world", punctuation="!"): 
    """Greets the user and includes a constant."""
    # Logic is now changed
    message = f"Hello, {name}! Did you know pi starts with {math.pi}?"
    print(message)
    return message

if __name__ == "__main__":
    greet()
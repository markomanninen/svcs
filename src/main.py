# FILE: src/main.py

import math # <-- NEW dependency

def greet(name="world"):
    """Greets the user and includes a constant."""
    # Logic is now changed
    message = f"Hello, {name}! Did you know pi starts with {math.pi}?"
    print(message)
    return message # <-- Return statement's source is now different

if __name__ == "__main__":
    greet()
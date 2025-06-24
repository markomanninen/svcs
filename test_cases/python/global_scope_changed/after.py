counter = 0

def increment():
    """Function that modifies global variable."""
    global counter
    counter += 1
    return counter

def reset():
    """Function that uses global."""
    global counter
    counter = 0
    return counter

def outer_function():
    """Nested function without nonlocal."""
    x = 10
    
    def inner_function():
        x = 20  # Local variable
        return x
    
    return inner_function()

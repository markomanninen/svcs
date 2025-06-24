counter = 0

def increment():
    """Function that modifies local variable."""
    counter = 1
    return counter

def reset():
    """Function without global usage."""
    value = 0
    return value

def outer_function():
    """Nested function without nonlocal."""
    x = 10
    
    def inner_function():
        x = 20  # Local variable
        return x
    
    return inner_function()

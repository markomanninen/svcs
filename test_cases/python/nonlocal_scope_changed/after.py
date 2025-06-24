def outer_function():
    """Nested function with nonlocal."""
    x = 10
    y = 20
    
    def inner_function():
        nonlocal x, y
        x = 30  # Modifies outer scope
        y = 40  # Modifies outer scope
        return x + y
    
    def another_inner():
        nonlocal x
        x += 5  # Also modifies outer scope
        z = x + y
        return z
    
    return inner_function() + another_inner()

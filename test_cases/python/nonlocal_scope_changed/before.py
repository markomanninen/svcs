def outer_function():
    """Nested function without nonlocal."""
    x = 10
    y = 20
    
    def inner_function():
        x = 30  # Local variable
        y = 40  # Local variable
        return x + y
    
    def another_inner():
        z = x + y  # Uses outer scope vars
        return z
    
    return inner_function() + another_inner()

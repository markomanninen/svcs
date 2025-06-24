def validate_input(value):
    """Function with if-statements instead of assertions."""
    if value is None:
        raise ValueError("Value cannot be None")
    if not isinstance(value, (int, float)):
        raise TypeError("Value must be numeric")
    if value < 0:
        raise ValueError("Value must be non-negative")
    
    return value * 2

def process_data(data):
    """Function with fewer assertions."""
    assert data, "Data cannot be empty"
    
    return sum(data)

def calculate(x, y):
    """Function without assertions."""
    if x == 0:
        raise ZeroDivisionError("X cannot be zero")
    if y <= 0:
        raise ValueError("Y must be positive")
    
    return x / y

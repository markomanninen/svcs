def validate_input(value):
    """Function with assertions."""
    assert value is not None, "Value cannot be None"
    assert isinstance(value, (int, float)), "Value must be numeric"
    assert value >= 0, "Value must be non-negative"
    
    return value * 2

def process_data(data):
    """Function with more assertions."""
    assert data, "Data cannot be empty"
    assert len(data) > 0, "Data must have at least one item"
    assert all(isinstance(x, int) for x in data), "All items must be integers"
    
    return sum(data)

def calculate(x, y):
    """Function with assertion checks."""
    assert x != 0, "X cannot be zero"
    assert y > 0, "Y must be positive"
    
    return x / y

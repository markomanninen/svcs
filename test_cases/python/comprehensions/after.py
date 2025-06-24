def process_data(data):
    """Process a list of numbers by filtering and transforming."""
    # Using list comprehension
    return [item * 2 for item in data if item > 0]

def get_dict():
    """Create a dictionary from keys and values."""
    keys = ["a", "b", "c"]
    values = [1, 2, 3]
    # Using dictionary comprehension
    return {keys[i]: values[i] for i in range(len(keys))}

def nested_for():
    """Create a matrix with nested list comprehensions."""
    # Using nested list comprehension
    return [[i * j for j in range(3)] for i in range(3)]

def yield_items(data):
    """Return a generator expression instead of yield."""
    # Using generator expression
    return (item for item in data)

def process_data(data):
    """Process a list of numbers by filtering and transforming."""
    # Manual approach
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result

def get_dict():
    """Create a dictionary from keys and values."""
    keys = ["a", "b", "c"]
    values = [1, 2, 3]
    result = {}
    for i in range(len(keys)):
        result[keys[i]] = values[i]
    return result

def nested_for():
    """Create a matrix with nested for loops."""
    result = []
    for i in range(3):
        row = []
        for j in range(3):
            row.append(i * j)
        result.append(row)
    return result

def yield_items(data):
    """Yield items one by one."""
    for item in data:
        yield item

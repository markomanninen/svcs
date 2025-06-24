def process_data(data):
    """Function without exception handling."""
    result = []
    for item in data:
        # Removed exception handling
        processed = item.upper()
        result.append(processed)
    
    return result

def divide_numbers(x, y):
    """Division without error handling."""
    # Removed all exception handling
    return x / y

def access_file(filename):
    """File access without error handling."""
    # Removed exception handling
    with open(filename, 'r') as f:
        return f.read()

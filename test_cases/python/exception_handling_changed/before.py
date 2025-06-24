def process_data(data):
    """Function with basic exception handling."""
    result = []
    for item in data:
        try:
            # This could fail if item is not compatible
            processed = item.upper()
            result.append(processed)
        except ValueError as e:
            # Initial error handling for ValueError
            print(f"Value error: {e}")
            result.append(str(item))
    
    return result

def divide_numbers(x, y):
    """Division with basic error handling."""
    try:
        return x / y
    except ZeroDivisionError:
        return float('inf')

def access_file(filename):
    """File access with basic error handling."""
    try:
        with open(filename, 'r') as f:
            return f.read()
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return ""

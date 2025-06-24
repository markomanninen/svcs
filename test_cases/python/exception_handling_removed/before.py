def process_data(data):
    """Function with exception handling."""
    result = []
    for item in data:
        try:
            processed = item.upper()
            result.append(processed)
        except (AttributeError, ValueError) as e:
            print(f"Processing error: {e}")
            result.append(str(item))
    
    return result

def divide_numbers(x, y):
    """Division with error handling."""
    try:
        return x / y
    except ZeroDivisionError:
        return float('inf')
    except TypeError as e:
        print(f"Type error: {e}")
        return None

def access_file(filename):
    """File access with error handling."""
    try:
        with open(filename, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return ""
    except PermissionError as e:
        print(f"Permission denied: {e}")
        return ""

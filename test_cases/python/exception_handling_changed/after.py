def process_data(data):
    """Function with improved exception handling."""
    result = []
    for item in data:
        try:
            # This could fail if item is not compatible
            processed = item.upper()
            result.append(processed)
        except (AttributeError, TypeError) as e:
            # Changed from ValueError to AttributeError/TypeError
            print(f"Processing error: {e}")
            result.append(str(item))
    
    return result

def divide_numbers(x, y):
    """Division with comprehensive error handling."""
    try:
        return x / y
    except ZeroDivisionError:
        return float('inf')
    except (TypeError, ValueError) as e:
        # Added more exception types
        print(f"Invalid input: {e}")
        return None

def access_file(filename):
    """File access with different error handling."""
    try:
        with open(filename, 'r') as f:
            return f.read()
    except IOError as e:
        # Changed from FileNotFoundError to IOError
        print(f"IO error: {e}")
        return ""

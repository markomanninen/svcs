def greet(name, greeting, punctuation):
    """Function without default parameters."""
    return f"{greeting}, {name}{punctuation}"

def calculate(x, y, z):
    """Simple calculation function."""
    return x + y * z

def process_data(data, options, debug):
    """Data processing function."""
    if debug:
        print(f"Processing {len(data)} items")
    
    return [item for item in data if item in options]

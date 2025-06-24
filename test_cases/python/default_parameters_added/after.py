def greet(name, greeting="Hello", punctuation="!"):
    """Function with default parameters."""
    return f"{greeting}, {name}{punctuation}"

def calculate(x, y=1, z=0):
    """Simple calculation function with defaults."""
    return x + y * z

def process_data(data, options=None, debug=False):
    """Data processing function with defaults."""
    if options is None:
        options = []
    
    if debug:
        print(f"Processing {len(data)} items")
    
    return [item for item in data if item in options]

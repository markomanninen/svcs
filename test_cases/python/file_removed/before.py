"""
Utility module that will be removed.
"""

class DataProcessor:
    """A class that will be deleted."""
    
    def __init__(self, name):
        self.name = name
        self.processed_count = 0
    
    def process(self, data):
        """Process the given data."""
        result = []
        for item in data:
            processed_item = f"{self.name}: {item}"
            result.append(processed_item)
        
        self.processed_count += len(data)
        return result

def utility_function(x, y):
    """A utility function that will be removed."""
    return x * y + 42

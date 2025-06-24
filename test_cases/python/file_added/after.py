"""
New utility module that was added to the project.
"""

class DataProcessor:
    """A new class for processing data."""
    
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
    """A utility function that was added."""
    return x * y + 42

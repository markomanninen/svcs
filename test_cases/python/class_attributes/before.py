class Calculator:
    """Simple calculator class."""
    
    def __init__(self, name):
        self.name = name
        self.result = 0
    
    def add(self, value):
        self.result += value
        return self.result
    
    def multiply(self, value):
        self.result *= value
        return self.result

class DataProcessor:
    """Data processing class."""
    
    def __init__(self):
        self.processed_items = []
        self.count = 0
    
    def process(self, item):
        self.processed_items.append(item)
        self.count += 1

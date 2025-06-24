def update_counter(counter, increment):
    """Update a counter by adding an increment."""
    counter = counter + increment
    return counter

def build_string(parts):
    """Build a string from parts."""
    result = ""
    for part in parts:
        result = result + part
    return result

def multiply_value(value, factor):
    """Multiply a value by a factor."""
    value = value * factor
    return value

class Counter:
    def __init__(self, initial_value=0):
        self.count = initial_value
    
    def increment(self, value=1):
        self.count = self.count + value
    
    def decrement(self, value=1):
        self.count = self.count - value
    
    def multiply(self, value):
        self.count = self.count * value
    
    def divide(self, value):
        self.count = self.count / value

def update_dict(original, updates):
    """Update a dictionary with new values."""
    result = original.copy()
    for key, value in updates.items():
        result[key] = value
    return result

def update_counter(counter, increment):
    """Update a counter by adding an increment."""
    counter += increment
    return counter

def build_string(parts):
    """Build a string from parts."""
    result = ""
    for part in parts:
        result += part
    return result

def multiply_value(value, factor):
    """Multiply a value by a factor."""
    value *= factor
    return value

class Counter:
    def __init__(self, initial_value=0):
        self.count = initial_value
    
    def increment(self, value=1):
        self.count += value
    
    def decrement(self, value=1):
        self.count -= value
    
    def multiply(self, value):
        self.count *= value
    
    def divide(self, value):
        self.count /= value
    
    def floor_divide(self, value):
        self.count //= value
    
    def modulo(self, value):
        self.count %= value
    
    def power(self, value):
        self.count **= value
    
    def bit_and(self, value):
        self.count &= value
    
    def bit_or(self, value):
        self.count |= value
    
    def bit_xor(self, value):
        self.count ^= value

def update_dict(original, updates):
    """Update a dictionary with new values."""
    result = original.copy()
    result.update(updates)
    # Alternative using |= operator (Python 3.9+)
    # result |= updates
    return result

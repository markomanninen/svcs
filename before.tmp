# FILE: src/main.py (Enhanced with Multiple Semantic Patterns)

import sys  # Existing dependency
import asyncio  # NEW async dependency
from typing import List, Dict  # NEW type hint dependencies

# Decorator examples
def timing_decorator(func):
    """A simple timing decorator."""
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

class DataProcessor:
    """A class to demonstrate various semantic patterns."""
    
    def __init__(self, data: List[int] = None):
        self.data = data or []
        self.processed_count = 0
    
    @timing_decorator  # Existing decorator
    @property  # NEW decorator added
    def process_sync(self, multiplier: int = 2) -> List[int]:
        """Synchronous processing with comprehensions."""
        # List comprehension usage
        result = [x * multiplier for x in self.data if x > 0]
        # Generator expression usage
        squared = list(x**2 for x in result)
        
        # Binary operator usage (multiple types)
        self.processed_count += len(result)
        
        # Assert usage for validation
        assert len(squared) <= len(self.data), "Result length error"
        
        return squared
    
    async def process_async(self, callback=None) -> Dict[str, int]:  # NEW async method
        """Asynchronous processing with await patterns."""
        # Await usage
        await asyncio.sleep(0.1)
        
        # Dictionary comprehension
        result = {f"item_{i}": val for i, val in enumerate(self.data)}
        
        # Lambda function usage
        filtered = dict(filter(lambda kv: kv[1] > 5, result.items()))
        
        if callback:
            await callback(filtered)  # Another await call
            
        return filtered

def log_error(error_message):
    """A function to log errors."""
    print(f"ERROR: {error_message}", file=sys.stderr)

# Enhanced greet function with more patterns
def greet(name, salutation="Greetings", show_details=False): 
    """
    Greets the user and demonstrates multiple semantic changes.
    """
    global processed_items  # Global scope usage
    processed_items = 0
    
    try:
        # String manipulation with f-strings
        message = f"{salutation}, {name}!"
        
        # Control flow: for loop
        for i in range(2):
            print(f"({i+1}) {message}")
            processed_items += 1  # Augmented assignment
        
        # Control flow: conditional
        if show_details:
            # Attribute access
            details = sys.version_info
            print(f"Python version: {details.major}.{details.minor}")
            
        # Comparison and logical operators
        if name and len(name) > 0:
            return message
        else:
            return None

    except (TypeError, ValueError) as e:  # Multiple exception types
        # Function call
        log_error(f"Invalid input for greet: {e}")
        return None
    except Exception as e:  # Catch-all exception
        log_error(f"Unexpected error: {e}")
        return None

# Generator function example
def number_generator(limit: int):
    """A generator that yields numbers."""
    for i in range(limit):
        if i % 2 == 0:  # Modulo operator
            yield i * 2  # Yield statement

# Global variable for demonstration
processed_items = 0

if __name__ == "__main__":
    # Usage examples with various patterns
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    processor = DataProcessor(data)
    
    # Sync processing
    result = processor.process_sync(multiplier=3)
    print(f"Processed {len(result)} items")
    
    # Generator usage
    even_numbers = list(number_generator(10))
    print(f"Generated numbers: {even_numbers}")
    
    # Greet with different parameters
    greeting = greet("Alice", show_details=True)
    print(greeting)
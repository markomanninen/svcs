#!/usr/bin/env python3
"""
Demo script showing SVCS new semantic event types in action.
Run this to see various semantic changes detected by SVCS.
"""

# This will trigger: dependency_added (typing module)
from typing import List, Dict, Optional
import asyncio  # This will trigger: dependency_added (asyncio)

# Simple function that will be modified to show semantic evolution
def process_numbers(numbers):
    """Process a list of numbers."""
    result = []
    for num in numbers:
        if num > 0:
            result.append(num * 2)
    return result

# This will be enhanced to trigger multiple semantic events
class DataProcessor:
    """A simple data processor."""
    
    def __init__(self, data=None):
        self.data = data or []
    
    def calculate(self, multiplier):
        """Basic calculation method."""
        return [x * multiplier for x in self.data]

# Global variable to demonstrate scope changes
counter = 0

def increment_counter():
    """Function that modifies global state."""
    global counter
    counter += 1
    return counter

if __name__ == "__main__":
    # Demo the functionality
    processor = DataProcessor([1, 2, 3, 4, 5])
    result = processor.calculate(2)
    print(f"Result: {result}")
    
    numbers = [1, -2, 3, -4, 5]
    processed = process_numbers(numbers)
    print(f"Processed: {processed}")
    
    print(f"Counter: {increment_counter()}")

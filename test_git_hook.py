#!/usr/bin/env python3
"""
Simple test file to test git post-commit hook functionality
Updated with type hints and enhanced functionality
"""
from typing import Union

def simple_function(x: int) -> int:
    """A simple function for testing with type hints."""
    return x * 2

def advanced_function(x: Union[int, float], multiplier: float = 2.5) -> float:
    """A more advanced function with type hints."""
    return x * multiplier

class TestClass:
    """A test class with enhanced functionality."""
    
    def __init__(self, value: int = 0):
        self.value = value
        self._private_var = "hidden"
    
    def get_value(self) -> int:
        """Get the current value."""
        return self.value
    
    def set_value(self, new_value: int) -> None:
        """Set a new value."""
        if new_value < 0:
            raise ValueError("Value must be non-negative")
        self.value = new_value
    
    def compute_doubled(self) -> int:
        """Compute double of the current value."""
        return simple_function(self.value)

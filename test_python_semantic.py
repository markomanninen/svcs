#!/usr/bin/env python3
"""
Test Python semantic analysis capabilities in the new SVCS architecture.
"""

def simple_function(name="World"):
    """A simple function with a parameter."""
    return f"hello {name}"

class TestClass:
    """A test class."""
    
    def __init__(self, value):
        self.value = value
    
    def method(self):
        return self.value

async def async_function():
    """An async function."""
    # await some_async_call()  # Commented out
    return "async result"

@property
def new_property(self):
    """A new property method."""
    return self.value * 2

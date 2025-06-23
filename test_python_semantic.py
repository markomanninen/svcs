#!/usr/bin/env python3
"""
Test Python semantic analysis capabilities in the new SVCS architecture.
"""

def simple_function():
    """A simple function."""
    return "hello"

class TestClass:
    """A test class."""
    
    def __init__(self, value):
        self.value = value
    
    def method(self):
        return self.value

async def async_function():
    """An async function."""
    await some_async_call()
    return "async result"

#!/usr/bin/env python3
"""
Comprehensive test file for demonstrating all SVCS layers
This is the initial version before comprehensive changes
"""

def simple_add(a, b):
    return a + b

def process_list(items):
    result = []
    for item in items:
        if item > 0:
            result.append(item * 2)
    return result

class BasicProcessor:
    def __init__(self):
        self.count = 0
    
    def process(self, value):
        self.count += 1
        return value

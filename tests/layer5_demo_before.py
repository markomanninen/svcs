#!/usr/bin/env python3
"""
Layer 5 Demo: Shows AI-detectable semantic patterns - REFACTORED VERSION
"""

def process_data_modern_way(numbers):
    """Modern implementation with patterns that Layer 5 can detect as improvements."""
    # Pattern 1: Conditional logic replaced with abs() builtin
    absolute_values = [abs(num) for num in numbers]
    
    # Pattern 2: Manual max finding replaced with builtin
    maximum = max(absolute_values)
    
    # Pattern 3: O(n²) algorithm optimized to O(n) with set
    unique_values = list(set(absolute_values))
    
    return maximum, unique_values

def calculate_stats(data):
    """Modern statistics calculation with proper error handling."""
    if not data:
        raise ValueError("Cannot calculate statistics for empty data")  # Specific exception
    
    # Built-in functions for better performance and readability
    total = sum(data)
    count = len(data)
    average = total / count
    
    return average

# Usage with more Pythonic patterns
numbers = [-5, 3, -2, 8, -1, 6]
max_val, unique_nums = process_data_modern_way(numbers)
avg = calculate_stats(unique_nums)
print(f"Max: {max_val}, Unique: {unique_nums}, Average: {avg}")

# Additional modern patterns
def advanced_processing(data):
    """Demonstrates additional modern Python patterns."""
    # List comprehension with conditional
    positive_squares = [x**2 for x in data if x > 0]
    
    # Generator expression for memory efficiency
    processed = (x * 2 for x in positive_squares if x < 100)
    
    # Context manager for resource handling
    with open('/dev/null', 'w') as f:
        for item in processed:
            f.write(f"{item}\n")
    
    return positive_squares

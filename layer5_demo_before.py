#!/usr/bin/env python3
"""
Layer 5 Demo: Shows AI-detectable semantic patterns
"""

def process_data_old_way(numbers):
    """Old implementation with patterns that Layer 5 can detect."""
    # Pattern 1: Manual conditional for abs()
    result = []
    for num in numbers:
        if num < 0:
            absolute_value = -num
        else:
            absolute_value = num
        result.append(absolute_value)
    
    # Pattern 2: Manual max finding
    maximum = result[0]
    for value in result[1:]:
        if value > maximum:
            maximum = value
    
    # Pattern 3: Nested loops (O(n²))
    filtered = []
    for i in result:
        duplicate = False
        for j in filtered:
            if i == j:
                duplicate = True
                break
        if not duplicate:
            filtered.append(i)
    
    return maximum, filtered

def calculate_stats(data):
    """Manual statistics calculation."""
    total = 0
    count = 0
    for item in data:
        total += item
        count += 1
    
    if count == 0:
        raise Exception("Empty data")  # Generic exception
    
    average = total / count
    return average

# Usage
numbers = [-5, 3, -2, 8, -1, 6]
max_val, unique_nums = process_data_old_way(numbers)
avg = calculate_stats(unique_nums)
print(f"Max: {max_val}, Unique: {unique_nums}, Average: {avg}")

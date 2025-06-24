from functools import reduce
from operator import add, mul

def process_numbers(numbers):
    """Process numbers using advanced functional approach."""
    # Enhanced functional patterns with multiple lambda functions
    squared = list(map(lambda x: x ** 2, numbers))
    filtered = list(filter(lambda x: x > 10, squared))
    doubled = list(map(lambda x: x * 2, filtered))
    total = reduce(add, doubled, 0)  # Added reduce operation
    return total

def transform_data(data):
    """Transform data with enhanced functional style."""
    # Using map with lambda functions and comprehensions
    transformed = [item.upper() for item in data]  # List comprehension
    lengths = [len(item) for item in transformed]  # Another comprehension
    filtered_lengths = [x for x in lengths if x > 3]  # Third comprehension
    total_length = reduce(add, filtered_lengths)  # Added aggregation
    return transformed, total_length

class Calculator:
    """Calculator with enhanced functional methods."""
    
    def apply_operation(self, numbers, operation):
        """Apply operation using enhanced functional approach."""
        # Multiple lambda functions and map operations
        doubled = list(map(lambda x: x * 2, numbers))
        processed = list(map(operation, doubled))
        return processed
    
    def aggregate_results(self, numbers):
        """New method using reduce and lambda for aggregation."""
        # Multiple functional programming patterns
        filtered = list(filter(lambda x: x > 0, numbers))
        squared = list(map(lambda x: x ** 2, filtered))
        product = reduce(lambda x, y: x * y, squared, 1)
        sum_total = reduce(add, squared, 0)
        return {"product": product, "sum": sum_total}

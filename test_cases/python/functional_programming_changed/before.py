def process_numbers(numbers):
    """Process numbers using basic functional approach."""
    # Basic functional patterns
    squared = list(map(lambda x: x ** 2, numbers))
    return squared

def transform_data(data):
    """Transform data with simple functional style."""
    # Using one map operation
    transformed = list(map(str.upper, data))
    return transformed

class Calculator:
    """Calculator with basic functional methods."""
    
    def apply_operation(self, numbers, operation):
        """Apply operation using simple functional approach."""
        return list(map(operation, numbers))

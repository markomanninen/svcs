from functools import reduce

def sort_by_name(people):
    """Sort people by name using lambda."""
    return sorted(people, key=lambda person: person['name'])

# get_name function replaced by lambda in sort_by_name

def transform_values(values):
    """Transform values using map."""
    return list(map(lambda x: x * 2, values))

def filter_positive(values):
    """Filter out negative values using filter."""
    return list(filter(lambda x: x > 0, values))

def combine_operations(values):
    """Combine operations using functional programming."""
    return reduce(
        lambda acc, val: acc + val,
        map(lambda x: x * 2, filter(lambda x: x > 0, values)),
        0
    )

class Calculator:
    def __init__(self):
        # Create a dictionary of operation functions
        self.operations = {
            'sum': lambda values: sum(values),
            'average': lambda values: sum(values) / len(values),
            'max': lambda values: max(values),
            'min': lambda values: min(values),
            'product': lambda values: reduce(lambda a, b: a * b, values, 1)
        }
    
    def apply_operation(self, values, operation_name):
        operation = self.operations.get(operation_name)
        return operation(values) if operation else None
    
    # Add a method to register new operations
    def register_operation(self, name, operation_func):
        self.operations[name] = operation_func

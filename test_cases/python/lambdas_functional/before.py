def sort_by_name(people):
    """Sort people by name."""
    result = people.copy()
    result.sort(key=get_name)
    return result

def get_name(person):
    """Get the name from a person object."""
    return person['name']

def transform_values(values):
    """Transform values by multiplying by 2."""
    result = []
    for value in values:
        result.append(value * 2)
    return result

def filter_positive(values):
    """Filter out negative values."""
    result = []
    for value in values:
        if value > 0:
            result.append(value)
    return result

def combine_operations(values):
    """Combine multiple operations on a list."""
    # Filter
    filtered = []
    for value in values:
        if value > 0:
            filtered.append(value)
    
    # Transform
    transformed = []
    for value in filtered:
        transformed.append(value * 2)
    
    # Sum
    total = 0
    for value in transformed:
        total += value
    
    return total

class Calculator:
    def apply_operation(self, values, operation_name):
        if operation_name == 'sum':
            return sum(values)
        elif operation_name == 'average':
            return sum(values) / len(values)
        elif operation_name == 'max':
            return max(values)
        else:
            return None

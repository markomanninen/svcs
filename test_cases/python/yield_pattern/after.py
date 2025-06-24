def simple_generator(n):
    """Changed to use yield expression with send capability."""
    i = 0
    while i < n:
        # Using yield expression to receive multiplier
        multiplier = yield i
        # Use received value or default to 1
        i += (multiplier or 1)

def fibonacci(n):
    """Changed to use yield from."""
    def fib_helper(count):
        a, b = 0, 1
        for _ in range(count):
            yield a
            a, b = b, a + b
    
    # Using yield from to delegate to another generator
    yield from fib_helper(n)

def filter_generator(items):
    """Changed to use yield with exception handling."""
    for item in items:
        try:
            if item > 0:
                # Yield with exception handling
                yield item
        except TypeError:
            # Handle non-numeric items
            continue

def process_with_yields(data):
    """Changed from multiple yields to a single yield with tuple."""
    for item in data:
        # Combined processing
        processed = item * 2
        if processed > 10:
            # Yield a tuple instead of multiple yields
            yield (processed, processed + 1)
        else:
            yield (processed, None)

def nested_generators(outer_n, inner_n):
    """Changed to use yield from for flattening."""
    for i in range(outer_n):
        # Using yield from to flatten the nested generator
        yield from (i * j for j in range(inner_n))

class GeneratorCollection:
    def __init__(self, max_value=10):
        self.max_value = max_value
    
    def iter_values(self):
        """Changed to generator expression."""
        # Using generator expression instead of yield statements
        return (i * i for i in range(self.max_value))

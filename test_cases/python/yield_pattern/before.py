def simple_generator(n):
    """Simple generator yielding numbers 0 to n-1."""
    for i in range(n):
        yield i

def fibonacci(n):
    """Generate Fibonacci sequence up to n elements."""
    a, b = 0, 1
    count = 0
    while count < n:
        yield a
        a, b = b, a + b
        count += 1

def filter_generator(items):
    """Yield only positive items."""
    for item in items:
        if item > 0:
            yield item

def process_with_yields(data):
    """Process data with multiple yields."""
    for item in data:
        # Pre-processing
        processed = item * 2
        yield processed
        
        # Post-processing
        if processed > 10:
            yield processed + 1

def nested_generators(outer_n, inner_n):
    """Nested generator pattern."""
    for i in range(outer_n):
        def inner_generator():
            for j in range(inner_n):
                yield i * j
        
        yield inner_generator()

class GeneratorCollection:
    def __init__(self, max_value=10):
        self.max_value = max_value
    
    def iter_values(self):
        """Instance method generator."""
        for i in range(self.max_value):
            yield i * i

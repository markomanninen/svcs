import functools
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Decorators to be removed
def timing_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper

def logging_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Calling {func.__name__} with args: {args}, kwargs: {kwargs}")
        return func(*args, **kwargs)
    return wrapper

def deprecation_warning(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.warning(f"Function {func.__name__} is deprecated and will be removed in future versions")
        return func(*args, **kwargs)
    return wrapper

# Class with method decorators
class APIHandler:
    @timing_decorator
    def fetch_data(self, endpoint):
        time.sleep(0.1)  # Simulate API call
        return f"Data from {endpoint}"
    
    @logging_decorator
    @deprecation_warning
    def process_data(self, data):
        return f"Processed: {data}"

# Functions with decorators
@timing_decorator
@logging_decorator
def complex_calculation(x, y):
    time.sleep(0.1)  # Simulate complex calculation
    return x * y + x / y if y != 0 else 0

@deprecation_warning
def legacy_function(value):
    # Old implementation
    return value * 2

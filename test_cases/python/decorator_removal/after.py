import functools
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Decorators kept for other uses but removed from functions below
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

# Class with decorators removed
class APIHandler:
    # Removed timing_decorator
    def fetch_data(self, endpoint):
        # Added manual timing code instead
        start_time = time.time()
        time.sleep(0.1)  # Simulate API call
        result = f"Data from {endpoint}"
        end_time = time.time()
        logger.info(f"fetch_data took {end_time - start_time:.2f} seconds")
        return result
    
    # Removed both decorators
    def process_data(self, data):
        # Added manual logging instead
        logger.info(f"Calling process_data with data: {data}")
        logger.warning("This method is deprecated")
        return f"Processed: {data}"

# Functions with decorators removed
# Removed both decorators
def complex_calculation(x, y):
    # Added manual timing and logging
    start_time = time.time()
    logger.info(f"Calling complex_calculation with args: {x}, {y}")
    time.sleep(0.1)  # Simulate complex calculation
    result = x * y + x / y if y != 0 else 0
    end_time = time.time()
    logger.info(f"complex_calculation took {end_time - start_time:.2f} seconds")
    return result

# Removed deprecation_warning decorator
def legacy_function(value):
    # Added manual warning
    logger.warning("This function is deprecated")
    # Old implementation
    return value * 2

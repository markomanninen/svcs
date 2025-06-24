import time
import logging
import functools
from typing import Callable, Any, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache decorator
def memoize(func):
    """Memoization decorator to cache results."""
    cache = {}
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
            logger.info(f"Cache miss for {func.__name__}{args}")
        else:
            logger.info(f"Cache hit for {func.__name__}{args}")
        return cache[key]
    
    return wrapper

# Timing decorator
def timing(func):
    """Measure execution time of a function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    
    return wrapper

# Retry decorator
def retry(max_attempts: int = 3, delay: float = 0.5):
    """Retry a function if it fails."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts == max_attempts:
                        raise
                    logger.warning(f"Attempt {attempts} failed, retrying in {delay}s: {e}")
                    time.sleep(delay)
        return wrapper
    return decorator

@memoize
@timing
def fetch_data(url):
    """Fetch data from a URL."""
    logger.info(f"Fetching data from {url}")
    # Simulate network delay
    time.sleep(0.1)
    return f"Data from {url}"

@retry(max_attempts=2)
@timing
def process_user(user_id):
    """Process a user."""
    logger.info(f"Processing user {user_id}")
    # Simulate processing
    time.sleep(0.1)
    return f"Processed user {user_id}"

@memoize
def cache_result(key):
    """A function that would be used with a decorator."""
    # Simulate caching
    return f"Cached {key}"

# Class decorator
def log_all_methods(cls):
    """Decorator to log all method calls on a class."""
    for attr_name, attr_value in cls.__dict__.items():
        if callable(attr_value) and not attr_name.startswith("__"):
            setattr(cls, attr_name, timing(attr_value))
    return cls

@log_all_methods
class APIClient:
    def fetch_user(self, user_id):
        """Fetch a user from the API."""
        logger.info(f"Fetching user {user_id}")
        # Simulate API call
        time.sleep(0.1)
        return f"User {user_id}"
    
    def update_user(self, user_id, data):
        """Update a user in the API."""
        logger.info(f"Updating user {user_id}")
        # Simulate API call
        time.sleep(0.1)
        return f"Updated user {user_id}"

import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_data(url):
    """Fetch data from a URL."""
    logger.info(f"Fetching data from {url}")
    # Simulate network delay
    time.sleep(0.1)
    return f"Data from {url}"

def process_user(user_id):
    """Process a user."""
    logger.info(f"Processing user {user_id}")
    # Simulate processing
    time.sleep(0.1)
    return f"Processed user {user_id}"

def cache_result(key):
    """A function that would be used with a decorator."""
    # Simulate caching
    return f"Cached {key}"

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

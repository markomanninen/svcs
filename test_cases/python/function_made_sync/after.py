import time

def fetch_data(url):
    """Synchronous data fetching."""
    # Simulate network request with blocking sleep
    time.sleep(0.1)
    return f"Data from {url}"

def process_items(items):
    """Synchronous item processing."""
    results = []
    for item in items:
        # Process each item synchronously
        time.sleep(0.01)
        result = item * 2
        results.append(result)
    return results

def calculate_total(numbers):
    """Sync calculation function."""
    time.sleep(0.05)
    return sum(numbers)

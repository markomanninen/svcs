def fetch_data(url):
    """Synchronous data fetching."""
    # Simulate network request
    import time
    time.sleep(0.1)
    return f"Data from {url}"

def process_items(items):
    """Synchronous item processing."""
    results = []
    for item in items:
        # Process each item
        result = item * 2
        results.append(result)
    return results

def generate_numbers(n):
    """Generator function that yields values."""
    for i in range(n):
        yield i * i

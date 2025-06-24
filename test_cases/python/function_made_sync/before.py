import asyncio

async def fetch_data(url):
    """Asynchronous data fetching."""
    # Simulate async network request
    await asyncio.sleep(0.1)
    return f"Data from {url}"

async def process_items(items):
    """Asynchronous item processing."""
    results = []
    for item in items:
        # Process each item asynchronously
        await asyncio.sleep(0.01)
        result = item * 2
        results.append(result)
    return results

async def calculate_total(numbers):
    """Async calculation function."""
    await asyncio.sleep(0.05)
    return sum(numbers)

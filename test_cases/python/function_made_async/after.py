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

def generate_numbers(n):
    """Regular function that returns a list."""
    numbers = []
    for i in range(n):
        numbers.append(i * i)
    return numbers

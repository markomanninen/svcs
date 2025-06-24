def check_status():
    """Check status with different boolean logic."""
    is_active = False  # Changed from True
    is_valid = True   # Changed from False
    is_ready = True   # Added new boolean
    is_complete = False  # Added new boolean
    
    if is_active and is_ready:
        return "active and ready"
    elif is_valid and is_complete:
        return "valid and complete"
    
    return "inactive"

def process_data(data):
    """Process data with more boolean checks."""
    if data:
        result = False  # Changed from True
        success = True  # Added new boolean
        return result and success
    else:
        default_value = True  # Added new boolean
        return default_value

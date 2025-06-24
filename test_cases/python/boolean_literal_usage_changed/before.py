def check_status():
    """Check status with some boolean logic."""
    is_active = True
    is_valid = False
    
    if is_active:
        return "active"
    
    return "inactive"

def process_data(data):
    """Process data with boolean checks."""
    if data:
        result = True
        return result
    else:
        return False

class Calculator:
    """Enhanced calculator class with more attributes."""
    
    # Class attributes for better detection
    DEFAULT_PRECISION = 2
    OPERATIONS_LOG = []
    
    def __init__(self, name):
        self.name = name
        self.result = 0
        self.history = []  # New instance attribute
        self.precision = self.DEFAULT_PRECISION  # New instance attribute
        self.last_operation = None  # New instance attribute
        self.error_count = 0  # New instance attribute
    
    def add(self, value):
        self.last_operation = f"add {value}"
        self.history.append(self.last_operation)
        self.OPERATIONS_LOG.append(self.last_operation)  # Class attribute usage
        try:
            self.result += value
            return round(self.result, self.precision)
        except Exception:
            self.error_count += 1
            raise
    
    def multiply(self, value):
        self.last_operation = f"multiply {value}"
        self.history.append(self.last_operation)
        self.OPERATIONS_LOG.append(self.last_operation)  # Class attribute usage
        try:
            self.result *= value
            return round(self.result, self.precision)
        except Exception:
            self.error_count += 1
            raise

class DataProcessor:
    """Enhanced data processing class."""
    
    # Class attributes
    MAX_ITEMS = 1000
    PROCESS_COUNT = 0
    
    def __init__(self):
        self.processed_items = []
        self.count = 0
        self.errors = []  # New instance attribute
        self.start_time = None  # New instance attribute
        self.status = "initialized"  # New instance attribute
        self.batch_size = 10  # New instance attribute
    
    def process(self, item):
        import time
        if self.start_time is None:
            self.start_time = time.time()
        
        self.status = "processing"
        DataProcessor.PROCESS_COUNT += 1  # Class attribute modification
        
        try:
            if len(self.processed_items) >= self.MAX_ITEMS:
                raise ValueError("Maximum items exceeded")
            
            self.processed_items.append(item)
            self.count += 1
            self.status = "completed"
        except Exception as e:
            self.errors.append(str(e))
            self.status = "error"

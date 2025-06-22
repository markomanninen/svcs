#!/usr/bin/env python3
"""
Demo script showing SVCS new semantic event types in action.
Enhanced version with advanced Python patterns and error handling.
"""

# Enhanced imports for type annotations and async programming
from typing import List, Dict, Optional, Union, Callable
import asyncio
import logging  # New dependency added

# Enhanced function with type annotations, default parameters, and error handling
def process_numbers(numbers: List[int], multiplier: int = 2, filter_negative: bool = True) -> Optional[List[int]]:
    """
    Process a list of numbers with enhanced functionality.
    Now includes type hints, default parameters, and comprehensive error handling.
    """
    try:
        # Validate input with assertions
        assert isinstance(numbers, list), "Input must be a list"
        assert all(isinstance(n, (int, float)) for n in numbers), "All elements must be numbers"
        
        # Use functional programming patterns
        filter_func: Callable[[Union[int, float]], bool] = lambda x: x > 0 if filter_negative else True
        
        # Enhanced list comprehension with conditional logic
        result = [
            int(num * multiplier) 
            for num in numbers 
            if filter_func(num)
        ]
        
        # Multiple return patterns
        if not result:
            logging.warning("No valid numbers to process")
            return None
            
        return result
        
    except (TypeError, ValueError, AssertionError) as e:
        logging.error(f"Processing error: {e}")
        return None
    except Exception as e:
        logging.critical(f"Unexpected error: {e}")
        raise

# Enhanced class with inheritance, decorators, and async methods
class AdvancedDataProcessor:
    """
    Enhanced data processor with async capabilities and sophisticated error handling.
    Now inherits from a base class and includes decorators.
    """
    
    def __init__(self, data: Optional[List[Union[int, float]]] = None, batch_size: int = 100):
        self.data = data or []
        self.batch_size = batch_size
        self.processed_count = 0
        
    @property
    def has_data(self) -> bool:
        """Check if processor has data."""
        return len(self.data) > 0
    
    @staticmethod
    def validate_data(data: List) -> bool:
        """Static method to validate data."""
        return all(isinstance(x, (int, float)) for x in data)
    
    async def calculate_async(self, multiplier: float = 1.0) -> Dict[str, Union[List, int]]:
        """
        Async calculation method with comprehensive error handling.
        Uses await, generators, and dictionary comprehensions.
        """
        try:
            if not self.has_data:
                return {"result": [], "count": 0}
            
            # Simulate async processing
            await asyncio.sleep(0.01)
            
            # Generator expression for memory efficiency
            processed_data = list(
                item * multiplier 
                for item in self.data 
                if item is not None
            )
            
            # Dictionary comprehension for result formatting
            result = {
                f"batch_{i}": processed_data[i:i+self.batch_size]
                for i in range(0, len(processed_data), self.batch_size)
            }
            
            self.processed_count += len(processed_data)
            
            return {
                "result": result,
                "count": len(processed_data),
                "total_processed": self.processed_count
            }
            
        except Exception as e:
            logging.error(f"Async calculation failed: {e}")
            raise
    
    def __len__(self) -> int:
        """Magic method for length."""
        return len(self.data)
    
    def __str__(self) -> str:
        """String representation with f-string formatting."""
        return f"AdvancedDataProcessor(items={len(self.data)}, processed={self.processed_count})"

# Enhanced global scope usage with nonlocal patterns
total_operations = 0
error_count = 0

def track_operation(func: Callable) -> Callable:
    """Decorator to track function operations."""
    def wrapper(*args, **kwargs):
        global total_operations
        nonlocal_tracker = {"errors": 0}
        
        def inner_function():
            nonlocal nonlocal_tracker
            try:
                result = func(*args, **kwargs)
                total_operations += 1
                return result
            except Exception as e:
                nonlocal_tracker["errors"] += 1
                global error_count
                error_count += 1
                raise
        
        return inner_function()
    return wrapper

@track_operation
def complex_calculation(data: List[Union[int, float]], *operations: str, **options: Union[int, float, bool]) -> Dict:
    """
    Complex function demonstrating starred expressions, slice operations, and multiple patterns.
    """
    if not data:
        return {}
    
    # Slice operations
    first_half = data[:len(data)//2]
    second_half = data[len(data)//2:]
    
    results = {}
    
    # Process operations using starred expressions
    for op in operations:
        if op == "sum":
            results[op] = sum(data)
        elif op == "avg":
            results[op] = sum(data) / len(data) if data else 0
        elif op == "min_max":
            results[op] = (min(data), max(data)) if data else (None, None)
    
    # Use options with starred expressions  
    scaling = options.get("scale", 1.0)
    if scaling != 1.0:
        results["scaled"] = [x * scaling for x in data]
    
    return results

# Async main function
async def main():
    """
    Enhanced main function with async/await patterns and comprehensive error handling.
    """
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Create enhanced processor
        processor = AdvancedDataProcessor([1, 2, 3, 4, 5, None, 6.5, 7], batch_size=3)
        
        # Test async calculation
        result = await processor.calculate_async(2.5)
        print(f"Async result: {result}")
        
        # Test enhanced function
        numbers = [1, -2, 3, -4, 5, 0]
        processed = process_numbers(numbers, multiplier=3, filter_negative=True)
        print(f"Processed: {processed}")
        
        # Test complex calculation with starred expressions
        calc_result = complex_calculation(
            [1, 2, 3, 4, 5],
            "sum", "avg", "min_max",
            scale=2.0,
            precision=2
        )
        print(f"Complex calculation: {calc_result}")
        
        print(f"Total operations: {total_operations}")
        print(f"Error count: {error_count}")
        print(f"Processor info: {processor}")
        
    except Exception as e:
        logging.error(f"Main execution failed: {e}")
        raise

if __name__ == "__main__":
    # Run async main
    asyncio.run(main())

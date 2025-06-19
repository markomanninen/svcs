# FILE: src/main.py - COMPREHENSIVE SEMANTIC EVENTS TEST
# This file demonstrates ALL possible semantic changes for 5-layer SVCS testing

import sys
import os
import asyncio
import functools
import itertools
from typing import List, Dict, Optional, Generator, Union, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
from collections import defaultdict, Counter
import json
import re

# ==================== GLOBAL VARIABLES ====================
GLOBAL_COUNTER = 0
GLOBAL_CONFIG = {"debug": True, "verbose": False}

# ==================== DECORATORS ====================
def performance_monitor(func):
    """Performance monitoring decorator."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global GLOBAL_COUNTER
        GLOBAL_COUNTER += 1
        result = func(*args, **kwargs)
        return result
    return wrapper

def deprecated(reason="No reason provided"):
    """Deprecation warning decorator."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print(f"Warning: {func.__name__} is deprecated. {reason}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

@dataclass
class Config:
    """Configuration data class."""
    max_items: int = 100
    timeout: float = 30.0
    retry_count: int = 3
    debug_mode: bool = False

# ==================== ABSTRACT BASE CLASS ====================
class ProcessorInterface(ABC):
    """Abstract interface for processors."""
    
    @abstractmethod
    def process(self, data: Any) -> Any:
        """Process data method."""
        pass
    
    @abstractmethod
    async def process_async(self, data: Any) -> Any:
        """Async process data method."""
        pass

# ==================== COMPLEX CLASS HIERARCHY ====================
class BaseProcessor(ProcessorInterface):
    """Base processor with comprehensive patterns."""
    
    def __init__(self, config: Config = None, **kwargs):
        self.config = config or Config()
        self.stats = defaultdict(int)
        self.cache = {}
        self._private_data = []
        super().__init__()
    
    @property
    def item_count(self) -> int:
        """Property to get item count."""
        return len(self._private_data)
    
    @item_count.setter
    def item_count(self, value: int):
        """Property setter for item count."""
        if value >= 0:
            self._private_data = [0] * value
    
    @performance_monitor
    def process(self, data: List[Union[int, str]]) -> Dict[str, Any]:
        """Process data with multiple semantic patterns."""
        
        # Input validation with multiple assertions
        assert data is not None, "Data cannot be None"
        assert len(data) > 0, "Data cannot be empty"
        assert isinstance(data, list), "Data must be a list"
        
        # Global variable access
        global GLOBAL_COUNTER, GLOBAL_CONFIG
        
        # Nonlocal variable usage in nested function
        def inner_processor():
            nonlocal data
            # List comprehension with complex conditions
            filtered = [item for item in data if isinstance(item, int) and item > 0]
            
            # Dictionary comprehension with lambda
            mapped = {f"key_{i}": (lambda x: x ** 2)(val) for i, val in enumerate(filtered)}
            
            # Set comprehension
            unique_squares = {val ** 2 for val in filtered if val % 2 == 0}
            
            # Generator expression
            doubled = (x * 2 for x in filtered)
            
            return mapped, unique_squares, list(doubled)
        
        mapped_data, squares, doubled = inner_processor()
        
        # Multiple binary operators
        result_sum = sum(doubled) + GLOBAL_COUNTER * 2
        result_product = result_sum * len(data)
        result_division = result_product / max(len(data), 1)
        result_modulo = int(result_division) % 100
        
        # Comparison operators
        is_large = result_sum > 1000
        is_medium = 100 <= result_sum <= 1000
        is_small = result_sum < 100
        
        # Logical operators
        is_valid = is_large or is_medium or is_small
        is_processed = is_valid and len(mapped_data) > 0
        is_empty = not is_processed
        
        # Augmented assignments
        self.stats['processed'] += len(data)
        self.stats['filtered'] *= 2
        self.stats['errors'] //= 2
        self.stats['ratio'] **= 1.1
        
        # Attribute access patterns
        config_debug = self.config.debug_mode
        config_timeout = self.config.timeout
        stats_processed = self.stats['processed']
        
        # Subscript access patterns
        first_mapped = list(mapped_data.values())[0] if mapped_data else 0
        cache_key = f"result_{len(data)}"
        self.cache[cache_key] = result_sum
        
        # Control flow: complex if-elif-else
        if is_large and config_debug:
            status = "large_debug"
        elif is_medium:
            status = "medium"
        elif is_small and not config_debug:
            status = "small_production"
        else:
            status = "unknown"
        
        # Control flow: for loop with enumerate
        for index, item in enumerate(data):
            if isinstance(item, str):
                # String operations
                processed_item = item.upper().strip()
                self._private_data.append(len(processed_item))
        
        # Control flow: while loop
        counter = 0
        while counter < min(5, len(data)):
            self.stats['iterations'] += 1
            counter += 1
        
        # Exception handling with multiple catch blocks
        try:
            # Risky operation that might fail
            division_result = result_sum / (len(data) - len(data))
        except ZeroDivisionError:
            division_result = 0.0
        except (TypeError, ValueError) as e:
            division_result = -1.0
        except Exception as e:
            division_result = -2.0
        finally:
            self.stats['attempts'] += 1
        
        return {
            'status': status,
            'sum': result_sum,
            'mapped_count': len(mapped_data),
            'squares': squares,
            'division_result': division_result,
            'is_processed': is_processed,
            'iterations': counter
        }
    
    async def process_async(self, data: List[Any]) -> Dict[str, Any]:
        """Async processing with await patterns."""
        # Multiple await calls
        await asyncio.sleep(0.01)
        
        # Async comprehensions (if supported)
        async def async_generator():
            for item in data:
                await asyncio.sleep(0.001)
                yield item * 2
        
        # Collect async results
        async_results = []
        async for item in async_generator():
            async_results.append(item)
        
        # Another await call
        await asyncio.sleep(0.01)
        
        return {'async_results': async_results, 'count': len(async_results)}

# ==================== ADVANCED PROCESSOR ====================
class AdvancedProcessor(BaseProcessor):
    """Advanced processor demonstrating inheritance changes."""
    
    def __init__(self, config: Config = None, advanced_mode: bool = True):
        super().__init__(config)
        self.advanced_mode = advanced_mode
        self.neural_weights = [0.1, 0.2, 0.3, 0.4, 0.5]
    
    @deprecated("Use process_v2 instead")
    def process_legacy(self, data: Any) -> Any:
        """Legacy processing method."""
        return {'legacy': True, 'data': data}
    
    @performance_monitor
    def process_v2(self, data: List[Any]) -> Dict[str, Any]:
        """Enhanced processing with neural network simulation."""
        # Call parent method
        base_result = super().process(data)
        
        # Advanced mathematical operations
        import math
        
        # Complex mathematical expressions
        weights_sum = sum(self.neural_weights)
        normalized_weights = [w / weights_sum for w in self.neural_weights]
        
        # Functional programming patterns
        mapped_weights = list(map(lambda x: x ** 2, normalized_weights))
        filtered_weights = list(filter(lambda x: x > 0.1, mapped_weights))
        reduced_weight = functools.reduce(lambda a, b: a + b, filtered_weights, 0.0)
        
        # Advanced data structures
        weight_counter = Counter(self.neural_weights)
        weight_pairs = list(itertools.combinations(self.neural_weights, 2))
        
        # Complex slicing operations
        first_half = data[:len(data)//2]
        second_half = data[len(data)//2:]
        every_second = data[::2]
        reversed_data = data[::-1]
        
        # Pattern matching simulation (Python 3.10+ style with if-elif)
        data_length = len(data)
        if data_length == 0:
            pattern_result = "empty"
        elif 1 <= data_length <= 5:
            pattern_result = "small"
        elif 6 <= data_length <= 20:
            pattern_result = "medium"
        elif data_length > 20:
            pattern_result = "large"
        else:
            pattern_result = "unknown"
        
        base_result.update({
            'advanced': True,
            'weights_sum': weights_sum,
            'reduced_weight': reduced_weight,
            'pattern': pattern_result,
            'weight_pairs_count': len(weight_pairs),
            'neural_active': self.advanced_mode
        })
        
        return base_result

# ==================== UTILITY FUNCTIONS ====================
def fibonacci_generator(n: int) -> Generator[int, None, None]:
    """Generator function for Fibonacci sequence."""
    a, b = 0, 1
    count = 0
    while count < n:
        yield a
        a, b = b, a + b
        count += 1

def factorial_recursive(n: int) -> int:
    """Recursive factorial function."""
    if n <= 1:
        return 1
    return n * factorial_recursive(n - 1)

def prime_sieve(limit: int) -> List[int]:
    """Sieve of Eratosthenes for finding primes."""
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, limit + 1, i):
                sieve[j] = False
    
    return [num for num, is_prime in enumerate(sieve) if is_prime]

@performance_monitor
def complex_data_analysis(data: List[Union[int, float]]) -> Dict[str, Any]:
    """Complex data analysis function."""
    if not data:
        return {}
    
    # Statistical calculations
    mean_val = sum(data) / len(data)
    variance = sum((x - mean_val) ** 2 for x in data) / len(data)
    std_dev = variance ** 0.5
    
    # Sorting and ranking
    sorted_data = sorted(data)
    median = sorted_data[len(sorted_data) // 2]
    
    # Outlier detection
    q1 = sorted_data[len(sorted_data) // 4]
    q3 = sorted_data[3 * len(sorted_data) // 4]
    iqr = q3 - q1
    outliers = [x for x in data if x < q1 - 1.5 * iqr or x > q3 + 1.5 * iqr]
    
    return {
        'mean': mean_val,
        'median': median,
        'std_dev': std_dev,
        'outliers': outliers,
        'count': len(data)
    }

# ==================== MAIN EXECUTION ====================
def main():
    """Main function demonstrating all patterns."""
    global GLOBAL_COUNTER, GLOBAL_CONFIG
    
    print("🚀 COMPREHENSIVE SEMANTIC EVENTS TEST")
    print("=" * 50)
    
    # Configuration setup
    config = Config(max_items=50, debug_mode=True, retry_count=5)
    
    # Processor instances
    base_processor = BaseProcessor(config)
    advanced_processor = AdvancedProcessor(config, advanced_mode=True)
    
    # Test data with mixed types
    test_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, "hello", "world", 15, 20]
    numeric_data = [x for x in test_data if isinstance(x, (int, float))]
    
    # Test synchronous processing
    print("\n📊 Testing Base Processor...")
    base_result = base_processor.process(test_data)
    print(f"Base Result: {base_result}")
    
    print("\n🧠 Testing Advanced Processor...")
    advanced_result = advanced_processor.process_v2(test_data)
    print(f"Advanced Result: {advanced_result}")
    
    # Test utility functions
    print("\n🔢 Testing Utility Functions...")
    
    # Fibonacci sequence
    fib_sequence = list(fibonacci_generator(10))
    print(f"Fibonacci: {fib_sequence}")
    
    # Factorial
    fact_5 = factorial_recursive(5)
    print(f"Factorial of 5: {fact_5}")
    
    # Prime numbers
    primes = prime_sieve(30)
    print(f"Primes up to 30: {primes}")
    
    # Data analysis
    analysis = complex_data_analysis(numeric_data)
    print(f"Data Analysis: {analysis}")
    
    # Test legacy function
    legacy_result = advanced_processor.process_legacy({"test": "data"})
    print(f"Legacy Result: {legacy_result}")
    
    # Property access
    base_processor.item_count = 5
    print(f"Item count: {base_processor.item_count}")
    
    # Global variable modifications
    GLOBAL_COUNTER += 100
    GLOBAL_CONFIG["verbose"] = True
    
    print(f"\n✅ Test complete! Global counter: {GLOBAL_COUNTER}")
    print(f"Global config: {GLOBAL_CONFIG}")

async def async_main():
    """Async main function for testing async patterns."""
    print("\n🔄 Testing Async Patterns...")
    
    config = Config()
    processor = AdvancedProcessor(config)
    
    # Test async processing
    async_result = await processor.process_async([1, 2, 3, 4, 5])
    print(f"Async Result: {async_result}")

if __name__ == "__main__":
    # Run synchronous tests
    main()
    
    # Run asynchronous tests
    asyncio.run(async_main())
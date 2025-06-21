#!/usr/bin/env python3
"""
Comprehensive test file for demonstrating all SVCS layers
MAJOR REFACTOR: Added type hints, async support, error handling, design patterns, and modern Python features
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Union, Optional, Callable, TypeVar, Generic
from dataclasses import dataclass
from functools import wraps
from contextlib import contextmanager

# Configure logging for better error tracking
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T')

@dataclass
class ProcessingResult:
    """Result container with metadata."""
    value: Union[int, float, List]
    processing_time: float
    metadata: Dict[str, str]

def timing_decorator(func: Callable) -> Callable:
    """Decorator to measure function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start
            logger.info(f"{func.__name__} completed in {duration:.4f}s")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            raise
    return wrapper

class ProcessorInterface(ABC, Generic[T]):
    """Abstract base class for all processors implementing Strategy pattern."""
    
    @abstractmethod
    async def process_async(self, data: T) -> ProcessingResult:
        """Asynchronously process data."""
        pass
    
    @abstractmethod
    def validate_input(self, data: T) -> bool:
        """Validate input data."""
        pass

class MathProcessor(ProcessorInterface[Union[int, float]]):
    """Advanced mathematical processor with comprehensive error handling."""
    
    def __init__(self, operation_mode: str = "safe"):
        self.operation_mode = operation_mode
        self.operation_count = 0
        self._cache: Dict[str, Union[int, float]] = {}
        logger.info(f"MathProcessor initialized in {operation_mode} mode")
    
    def validate_input(self, data: Union[int, float]) -> bool:
        """Validate numerical input with comprehensive checks."""
        if not isinstance(data, (int, float)):
            raise TypeError(f"Expected int or float, got {type(data)}")
        if self.operation_mode == "safe" and abs(data) > 1000000:
            raise ValueError("Input value exceeds safe processing limits")
        return True
    
    @timing_decorator
    def advanced_add(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Enhanced addition with validation and caching."""
        self.validate_input(a)
        self.validate_input(b)
        
        cache_key = f"add_{a}_{b}"
        if cache_key in self._cache:
            logger.debug(f"Cache hit for {cache_key}")
            return self._cache[cache_key]
        
        result = a + b
        self._cache[cache_key] = result
        self.operation_count += 1
        return result
    
    async def process_async(self, data: Union[int, float]) -> ProcessingResult:
        """Asynchronously process numerical data with complex operations."""
        import time
        start_time = time.time()
        
        try:
            self.validate_input(data)
            
            # Simulate complex async processing
            await asyncio.sleep(0.01)  # Simulate I/O bound operation
            
            # Apply mathematical transformations
            if data < 0:
                processed_value = abs(data) ** 0.5
            elif data == 0:
                processed_value = 1.0
            else:
                processed_value = data * 2.5
            
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                value=processed_value,
                processing_time=processing_time,
                metadata={
                    "processor": "MathProcessor",
                    "operation_mode": self.operation_mode,
                    "input_type": type(data).__name__
                }
            )
        except Exception as e:
            logger.error(f"Processing failed for input {data}: {e}")
            raise

class ListProcessor(ProcessorInterface[List]):
    """Advanced list processor with functional programming patterns."""
    
    def __init__(self, filter_strategy: Optional[Callable] = None):
        self.filter_strategy = filter_strategy or (lambda x: x > 0)
        self.processed_items = 0
        
    def validate_input(self, data: List) -> bool:
        """Validate list input."""
        if not isinstance(data, list):
            raise TypeError(f"Expected list, got {type(data)}")
        if len(data) > 10000:
            raise ValueError("List too large for processing")
        return True
    
    @timing_decorator
    def enhanced_process_list(self, items: List[Union[int, float]]) -> List[Union[int, float]]:
        """Process list using modern functional programming approach."""
        self.validate_input(items)
        
        try:
            # Modern functional approach with list comprehension and filter
            result = [
                item * 2 if item > 0 else abs(item) * 1.5
                for item in items 
                if self.filter_strategy(item)
            ]
            
            self.processed_items += len(result)
            logger.info(f"Processed {len(result)} items from {len(items)} input items")
            return result
            
        except Exception as e:
            logger.error(f"List processing failed: {e}")
            raise
    
    async def process_async(self, data: List) -> ProcessingResult:
        """Asynchronously process list data."""
        import time
        start_time = time.time()
        
        self.validate_input(data)
        
        # Process in chunks for better performance
        chunk_size = 100
        processed_chunks = []
        
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            await asyncio.sleep(0.001)  # Simulate async processing
            processed_chunk = self.enhanced_process_list(chunk)
            processed_chunks.extend(processed_chunk)
        
        processing_time = time.time() - start_time
        
        return ProcessingResult(
            value=processed_chunks,
            processing_time=processing_time,
            metadata={
                "processor": "ListProcessor",
                "input_size": str(len(data)),
                "output_size": str(len(processed_chunks))
            }
        )

class ProcessingFactory:
    """Factory pattern for creating processors."""
    
    @staticmethod
    def create_processor(processor_type: str, **kwargs) -> ProcessorInterface:
        """Create processor based on type."""
        if processor_type == "math":
            return MathProcessor(**kwargs)
        elif processor_type == "list":
            return ListProcessor(**kwargs)
        else:
            raise ValueError(f"Unknown processor type: {processor_type}")

@contextmanager
def processing_context(processor_name: str):
    """Context manager for processing operations."""
    logger.info(f"Starting {processor_name} processing context")
    try:
        yield
    except Exception as e:
        logger.error(f"Error in {processor_name} context: {e}")
        raise
    finally:
        logger.info(f"Completed {processor_name} processing context")

async def comprehensive_processing_pipeline(data: Dict[str, Union[int, float, List]]) -> Dict[str, ProcessingResult]:
    """Complete processing pipeline demonstrating all patterns."""
    results = {}
    
    with processing_context("comprehensive_pipeline"):
        # Process numerical data
        if "numbers" in data:
            math_processor = ProcessingFactory.create_processor("math", operation_mode="safe")
            for i, num in enumerate(data["numbers"]):
                result = await math_processor.process_async(num)
                results[f"math_{i}"] = result
        
        # Process list data
        if "lists" in data:
            list_processor = ProcessingFactory.create_processor("list")
            for i, lst in enumerate(data["lists"]):
                result = await list_processor.process_async(lst)
                results[f"list_{i}"] = result
    
    return results

# Test function to trigger Layer 5b with logging
def simple_logging_test():
    """Simple function to test LLM logging."""
    print("Testing LLM logging functionality")

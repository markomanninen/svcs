"""
Comprehensive Python demo file for testing all 5 layers of SVCS analysis.
This file contains various Python patterns and constructs.
"""

import logging
from typing import List, Dict, Optional, Union
import asyncio
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DataPoint:
    """Represents a data point with metadata."""
    value: float
    timestamp: str
    metadata: Dict[str, str] = None

class ProcessorInterface(ABC):
    """Abstract interface for data processors."""
    
    @abstractmethod
    def process(self, data: List[DataPoint]) -> Dict[str, float]:
        """Process data points and return summary statistics."""
        pass

class DataProcessor(ProcessorInterface):
    """Modern data processor with comprehensive functionality."""
    
    def __init__(self, config: Optional[Dict[str, str]] = None):
        self.config = config or {}
        self.processed_count = 0
        logger.info("DataProcessor initialized")
    
    def process(self, data: List[DataPoint]) -> Dict[str, float]:
        """Process data points with error handling and logging."""
        try:
            if not data:
                raise ValueError("No data provided")
            
            # Modern list comprehension approach
            values = [point.value for point in data if point.value is not None]
            
            if not values:
                logger.warning("No valid values found")
                return {}
            
            # Calculate statistics
            result = {
                'mean': sum(values) / len(values),
                'max': max(values),
                'min': min(values),
                'count': len(values)
            }
            
            self.processed_count += len(values)
            logger.info(f"Processed {len(values)} data points")
            
            return result
            
        except (ValueError, TypeError) as e:
            logger.error(f"Processing error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

def modern_function(numbers: List[int]) -> Dict[str, Union[int, float]]:
    """Modern function with type hints and comprehensive logic."""
    if not numbers:
        return {'error': 'Empty input'}
    
    # Use functional programming approaches
    filtered_numbers = [n for n in numbers if isinstance(n, int) and n > 0]
    
    if not filtered_numbers:
        return {'error': 'No valid numbers'}
    
    return {
        'sum': sum(filtered_numbers),
        'average': sum(filtered_numbers) / len(filtered_numbers),
        'squares': [n ** 2 for n in filtered_numbers[:5]]  # Limit to first 5
    }

async def process_async(data: List[str]) -> List[str]:
    """Async function for concurrent processing."""
    async def process_item(item: str) -> str:
        await asyncio.sleep(0.01)  # Simulate async work
        return item.upper().strip()
    
    tasks = [process_item(item) for item in data]
    return await asyncio.gather(*tasks)

def process_numbers(data):
    """Process a list of numbers with comprehensive error handling."""
    try:
        if not data:
            logging.error("Empty data provided")
            return []
        
        # Modern approach with list comprehension and built-in functions
        result = [abs(x) for x in data if isinstance(x, (int, float))]
        
        return {
            'processed': result,
            'max_value': max(result) if result else 0,
            'summary': f"Processed {len(result)} valid numbers"
        }
        
    except Exception as e:
        logging.error(f"Error processing numbers: {e}")
        return []

# Demonstration of various Python constructs for layer testing
class ConfigManager:
    """Configuration manager with various patterns."""
    
    def __init__(self):
        self._config = {}
        self._observers = []
    
    def set_config(self, key: str, value: str) -> None:
        """Set configuration with observer pattern."""
        old_value = self._config.get(key)
        self._config[key] = value
        
        # Notify observers
        for observer in self._observers:
            observer.on_config_changed(key, old_value, value)
    
    def get_config(self, key: str, default: str = None) -> Optional[str]:
        """Get configuration value with default."""
        return self._config.get(key, default)

# Factory pattern example
def create_processor(processor_type: str = "standard") -> ProcessorInterface:
    """Factory function for creating processors."""
    if processor_type == "standard":
        return DataProcessor()
    else:
        raise ValueError(f"Unknown processor type: {processor_type}")

# Context manager example
class ResourceManager:
    """Context manager for resource handling."""
    
    def __init__(self, resource_name: str):
        self.resource_name = resource_name
        self.resource = None
    
    def __enter__(self):
        logger.info(f"Acquiring resource: {self.resource_name}")
        self.resource = f"resource_{self.resource_name}"
        return self.resource
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info(f"Releasing resource: {self.resource_name}")
        self.resource = None

if __name__ == "__main__":
    # Demo usage
    processor = create_processor()
    
    sample_data = [
        DataPoint(1.5, "2024-01-01"),
        DataPoint(2.3, "2024-01-02"),
        DataPoint(0.8, "2024-01-03")
    ]
    
    result = processor.process(sample_data)
    print(f"Processing result: {result}")
    
    # Test modern function
    numbers_result = modern_function([1, 2, 3, 4, 5])
    print(f"Numbers result: {numbers_result}")

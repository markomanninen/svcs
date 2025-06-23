#!/usr/bin/env python3
"""
Test file for end-to-end workflow validation.
"""

import json
import asyncio
from typing import List, Dict, Optional

class WorkflowTester:
    """A class to test the workflow."""
    
    def __init__(self, name: str, version: str = "1.0"):
        self.name = name
        self.version = version
        self._initialized = True
    
    def basic_method(self) -> str:
        """A basic method."""
        return f"Workflow test: {self.name} v{self.version}"
    
    @property
    def status(self) -> Dict[str, bool]:
        """Get the current status."""
        return {"initialized": self._initialized, "ready": True}

async def async_workflow_function(data: List[Dict]) -> Optional[str]:
    """An async function for testing."""
    if not data:
        return None
    
    # Simulate async work
    await asyncio.sleep(0.1)
    
    # Process data with comprehension
    processed = [item["value"] for item in data if "value" in item]
    
    return json.dumps({"processed": processed, "count": len(processed)})

def utility_function(x: int, y: int = 10) -> int:
    """A utility function with default parameters."""
    try:
        result = x * y
        if result > 100:
            raise ValueError("Result too large")
        return result
    except ValueError as e:
        print(f"Error: {e}")
        return 0
    finally:
        print("Calculation completed")

# Module-level variable
WORKFLOW_CONFIG = {
    "enabled": True,
    "max_retries": 3,
    "timeout": 30
}

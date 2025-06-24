# SVCS Base Parser
# Abstract base class for all language parsers

from abc import ABC, abstractmethod
from typing import Dict, Set, List, Any, Optional

class BaseParser(ABC):
    """Abstract base parser for all languages."""
    
    def __init__(self):
        self.supported_extensions = set()
        self.language_name = ""
    
    @abstractmethod
    def parse_code(self, source_code: str) -> tuple:
        """
        Parse source code and return (nodes, dependencies).
        
        Args:
            source_code: Source code to parse
            
        Returns:
            Tuple of (nodes_dict, dependencies_set)
        """
        pass
    
    @abstractmethod
    def get_node_details(self, node) -> Dict[str, Any]:
        """Extract detailed information from a parsed node."""
        pass
    
    def supports_file(self, filename: str) -> bool:
        """Check if this parser supports the given file."""
        return any(filename.endswith(ext) for ext in self.supported_extensions)
    
    def get_language_name(self) -> str:
        """Get the name of the language this parser handles."""
        return self.language_name

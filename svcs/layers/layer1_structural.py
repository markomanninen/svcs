# SVCS Layer 1: Structural Analysis
# File-level structural changes

from typing import List, Dict, Any
from ..parsers import BaseParser

class StructuralAnalyzer:
    """Layer 1: Structural Analysis - File and module level changes."""
    
    def __init__(self):
        self.layer_name = "Layer 1: Structural"
        self.layer_description = "File and module structure analysis"
    
    def analyze(self, filepath: str, before_content: str, after_content: str, 
                nodes_before: dict, nodes_after: dict, 
                deps_before: set, deps_after: set) -> List[Dict[str, Any]]:
        """Analyze structural changes between before and after content."""
        events = []
        
        # File existence changes
        before_empty = not before_content or before_content.strip() == ""
        after_empty = not after_content or after_content.strip() == ""
        
        if before_empty and not after_empty:
            events.append({
                "event_type": "file_added",
                "node_id": f"file:{filepath}",
                "location": filepath,
                "details": "New file created",
                "layer": "1",
                "layer_description": self.layer_description
            })
        elif not before_empty and after_empty:
            events.append({
                "event_type": "file_removed",
                "node_id": f"file:{filepath}",
                "location": filepath,
                "details": "File deleted",
                "layer": "1",
                "layer_description": self.layer_description
            })
        
        # Dependency changes
        added_deps = deps_after - deps_before
        removed_deps = deps_before - deps_after
        
        if added_deps:
            events.append({
                "event_type": "dependency_added",
                "node_id": f"module:{filepath}",
                "location": filepath,
                "details": f"Added dependencies: {', '.join(sorted(added_deps))}",
                "layer": "1",
                "layer_description": self.layer_description
            })
        
        if removed_deps:
            events.append({
                "event_type": "dependency_removed",
                "node_id": f"module:{filepath}",
                "location": filepath,
                "details": f"Removed dependencies: {', '.join(sorted(removed_deps))}",
                "layer": "1",
                "layer_description": self.layer_description
            })
        
        # Node addition/removal
        all_node_ids = set(nodes_before.keys()) | set(nodes_after.keys())
        
        for node_id in all_node_ids:
            if node_id not in nodes_before:
                events.append({
                    "event_type": "node_added",
                    "node_id": node_id,
                    "location": filepath,
                    "details": f"New {node_id.split(':')[0]} added",
                    "layer": "1",
                    "layer_description": self.layer_description
                })
            elif node_id not in nodes_after:
                events.append({
                    "event_type": "node_removed",
                    "node_id": node_id,
                    "location": filepath,
                    "details": f"{node_id.split(':')[0]} removed",
                    "layer": "1",
                    "layer_description": self.layer_description
                })
        
        return events

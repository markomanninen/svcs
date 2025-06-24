# SVCS Layer 2: Syntactic Analysis
# Syntax-level changes in code structure

from typing import List, Dict, Any

class SyntacticAnalyzer:
    """Layer 2: Syntactic Analysis - Syntax and signature changes."""
    
    def __init__(self):
        self.layer_name = "Layer 2: Syntactic"
        self.layer_description = "Syntax and signature analysis"
    
    def analyze(self, filepath: str, nodes_before: dict, nodes_after: dict) -> List[Dict[str, Any]]:
        """Analyze syntactic changes between before and after nodes."""
        events = []
        
        # Analyze nodes that exist in both versions
        common_nodes = set(nodes_before.keys()) & set(nodes_after.keys())
        
        for node_id in common_nodes:
            before = nodes_before[node_id]
            after = nodes_after[node_id]
            
            # Skip if no actual change
            if before.get("source") == after.get("source"):
                continue
            
            base_event = {
                "node_id": node_id,
                "location": filepath,
                "layer": "2",
                "layer_description": self.layer_description
            }
            
            # Signature changes
            sig_before = before.get("signature")
            sig_after = after.get("signature")
            if sig_before and sig_after and sig_before != sig_after:
                events.append({
                    **base_event,
                    "event_type": "signature_changed",
                    "details": f"Signature changed from {sig_before} to {sig_after}"
                })
            
            # Decorator changes
            decorators_before = before.get("decorators", set())
            decorators_after = after.get("decorators", set())
            if decorators_before != decorators_after:
                added = decorators_after - decorators_before
                removed = decorators_before - decorators_after
                
                if added:
                    events.append({
                        **base_event,
                        "event_type": "decorator_added",
                        "details": f"Added decorators: {', '.join(sorted(added))}"
                    })
                
                if removed:
                    events.append({
                        **base_event,
                        "event_type": "decorator_removed",
                        "details": f"Removed decorators: {', '.join(sorted(removed))}"
                    })
            
            # Async/sync conversion
            async_before = before.get("is_async", False)
            async_after = after.get("is_async", False)
            if async_before != async_after:
                if async_after:
                    events.append({
                        **base_event,
                        "event_type": "function_made_async",
                        "details": "Function converted to async"
                    })
                else:
                    events.append({
                        **base_event,
                        "event_type": "function_made_sync",
                        "details": "Function converted from async to sync"
                    })
            
            # Inheritance changes (for classes)
            if node_id.startswith("class:"):
                bases_before = before.get("base_classes", set())
                bases_after = after.get("base_classes", set())
                if bases_before != bases_after:
                    events.append({
                        **base_event,
                        "event_type": "inheritance_changed",
                        "details": f"Base classes changed from {bases_before} to {bases_after}"
                    })
            
            # Parameter defaults
            defaults_before = before.get("has_defaults", False)
            defaults_after = after.get("has_defaults", False)
            if defaults_before != defaults_after:
                if defaults_after:
                    events.append({
                        **base_event,
                        "event_type": "default_parameters_added",
                        "details": "Function now has default parameter values"
                    })
                else:
                    events.append({
                        **base_event,
                        "event_type": "default_parameters_removed",
                        "details": "Function no longer has default parameter values"
                    })
        
        return events

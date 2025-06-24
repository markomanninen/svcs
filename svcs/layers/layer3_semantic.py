# SVCS Layer 3: Semantic Analysis
# Semantic meaning and logic changes

from typing import List, Dict, Any

class SemanticAnalyzer:
    """Layer 3: Semantic Analysis - Logic and meaning changes."""
    
    def __init__(self):
        self.layer_name = "Layer 3: Semantic"
        self.layer_description = "Logic and semantic meaning analysis"
    
    def analyze(self, filepath: str, nodes_before: dict, nodes_after: dict) -> List[Dict[str, Any]]:
        """Analyze semantic changes between before and after nodes."""
        events = []
        
        # Analyze nodes that exist in both versions
        common_nodes = set(nodes_before.keys()) & set(nodes_after.keys())
        
        for node_id in common_nodes:
            before = nodes_before[node_id]
            after = nodes_after[node_id]
            
            # Check if there are any semantic changes worth analyzing
            has_semantic_changes = (
                before.get("source") != after.get("source") or
                before.get("calls", set()) != after.get("calls", set()) or
                before.get("returns", 0) != after.get("returns", 0) or
                before.get("yields", 0) != after.get("yields", 0) or
                before.get("exception_handlers", set()) != after.get("exception_handlers", set()) or
                before.get("exception_handling", {}) != after.get("exception_handling", {}) or
                before.get("global_statements", set()) != after.get("global_statements", set()) or
                before.get("nonlocal_statements", set()) != after.get("nonlocal_statements", set()) or
                before.get("lambdas", 0) != after.get("lambdas", 0) or
                before.get("is_generator", False) != after.get("is_generator", False) or
                before.get("is_async", False) != after.get("is_async", False) or
                before.get("comprehensions", {}) != after.get("comprehensions", {})
            )
            
            # Skip if no semantic changes detected
            if not has_semantic_changes:
                continue
            
            base_event = {
                "node_id": node_id,
                "location": filepath,
                "layer": "3",
                "layer_description": self.layer_description
            }
            
            # Control flow changes
            flow_before = before.get("control_flow", {})
            flow_after = after.get("control_flow", {})
            if flow_before != flow_after:
                changes = []
                for key in set(flow_before) | set(flow_after):
                    b, a = flow_before.get(key, 0), flow_after.get(key, 0)
                    if b != a:
                        changes.append(f"{key} count changed from {b} to {a}")
                if changes:
                    events.append({
                        **base_event,
                        "event_type": "control_flow_changed",
                        "details": "; ".join(changes)
                    })
            
            # Return/yield pattern changes
            returns_before = before.get("return_statements", 0)
            returns_after = after.get("return_statements", 0)
            yields_before = before.get("yield_statements", 0)
            yields_after = after.get("yield_statements", 0)
            
            if yields_before == 0 and yields_after > 0:
                events.append({
                    **base_event,
                    "event_type": "function_made_generator",
                    "details": f"Function converted to generator with {yields_after} yield statements"
                })
            elif yields_before > 0 and yields_after == 0:
                events.append({
                    **base_event,
                    "event_type": "generator_made_function",
                    "details": "Generator converted to regular function"
                })
            elif yields_before != yields_after:
                events.append({
                    **base_event,
                    "event_type": "yield_pattern_changed",
                    "details": f"Yield statements changed from {yields_before} to {yields_after}"
                })
            
            if returns_before != returns_after:
                events.append({
                    **base_event,
                    "event_type": "return_pattern_changed",
                    "details": f"Return statements changed from {returns_before} to {returns_after}"
                })
            
            # Exception handling changes
            except_before = before.get("exception_handlers", set())
            except_after = after.get("exception_handlers", set())
            
            # Also check PHP/JS specific exception handling info
            exception_handling_before = before.get("exception_handling", {})
            exception_handling_after = after.get("exception_handling", {})
            
            has_exception_before = len(except_before) > 0 or exception_handling_before.get("has_try_catch", False)
            has_exception_after = len(except_after) > 0 or exception_handling_after.get("has_try_catch", False)
            
            if except_before != except_after or exception_handling_before != exception_handling_after:
                added = except_after - except_before
                removed = except_before - except_after
                
                # Get catch types for PHP/JS
                catch_types_before = exception_handling_before.get("catch_types", set())
                catch_types_after = exception_handling_after.get("catch_types", set())
                
                # Combine all exception types for comprehensive analysis
                all_added = added.union(catch_types_after - catch_types_before)
                all_removed = removed.union(catch_types_before - catch_types_after)
                
                # Generate appropriate events
                if not has_exception_before and has_exception_after:
                    events.append({
                        **base_event,
                        "event_type": "exception_handling_added",
                        "details": f"Exception handling added" + 
                                  (f" for: {', '.join(sorted(all_added))}" if all_added else "")
                    })
                    events.append({
                        **base_event,
                        "event_type": "error_handling_introduced",
                        "details": f"Error handling introduced" +
                                  (f" for: {', '.join(sorted(all_added))}" if all_added else "")
                    })
                elif has_exception_before and not has_exception_after:
                    events.append({
                        **base_event,
                        "event_type": "exception_handling_removed",
                        "details": "Exception handling completely removed"
                    })
                    events.append({
                        **base_event,
                        "event_type": "error_handling_removed",
                        "details": "Error handling completely removed"
                    })
                elif all_added or all_removed:
                    # Changes to existing exception handling
                    events.append({
                        **base_event,
                        "event_type": "exception_handling_changed",
                        "details": (f"Exception handling changed" +
                                  (f", added: {', '.join(sorted(all_added))}" if all_added else "") +
                                  (f", removed: {', '.join(sorted(all_removed))}" if all_removed else ""))
                    })
                else:
                    if added:
                        events.append({
                            **base_event,
                            "event_type": "exception_handling_added",
                            "details": f"Now handles: {', '.join(sorted(added))}"
                        })
                    if removed:
                        events.append({
                            **base_event,
                            "event_type": "exception_handling_removed",
                            "details": f"No longer handles: {', '.join(sorted(removed))}"
                        })
            
            # Function call changes
            calls_before = before.get("calls", set())
            calls_after = after.get("calls", set())
            if calls_before != calls_after:
                added = calls_after - calls_before
                removed = calls_before - calls_after
                
                if added:
                    events.append({
                        **base_event,
                        "event_type": "internal_call_added",
                        "details": f"Now calls: {', '.join(sorted(added))}"
                    })
                if removed:
                    events.append({
                        **base_event,
                        "event_type": "internal_call_removed",
                        "details": f"No longer calls: {', '.join(sorted(removed))}"
                    })
            
            # Comprehension usage changes
            comp_before = before.get("comprehensions", {})
            comp_after = after.get("comprehensions", {})
            if comp_before != comp_after:
                changes = []
                for comp_type in ["list", "dict", "set", "generator"]:
                    b, a = comp_before.get(comp_type, 0), comp_after.get(comp_type, 0)
                    if b != a:
                        changes.append(f"{comp_type} comprehensions: {b}→{a}")
                if changes:
                    events.append({
                        **base_event,
                        "event_type": "comprehension_usage_changed",
                        "details": "; ".join(changes)
                    })
            
            # Lambda usage changes
            lambda_before = before.get("lambda_functions", 0)
            lambda_after = after.get("lambda_functions", 0)
            if lambda_before != lambda_after:
                events.append({
                    **base_event,
                    "event_type": "lambda_usage_changed",
                    "details": f"Lambda functions changed from {lambda_before} to {lambda_after}"
                })
            
            # Scope changes
            global_before = before.get("global_statements", set())
            global_after = after.get("global_statements", set())
            if global_before != global_after:
                events.append({
                    **base_event,
                    "event_type": "global_scope_changed",
                    "details": f"Global statements changed: {global_before} → {global_after}"
                })
            
            nonlocal_before = before.get("nonlocal_statements", set())
            nonlocal_after = after.get("nonlocal_statements", set())
            if nonlocal_before != nonlocal_after:
                events.append({
                    **base_event,
                    "event_type": "nonlocal_scope_changed",
                    "details": f"Nonlocal statements changed: {nonlocal_before} → {nonlocal_after}"
                })
        
        return events

# SVCS Layer 4: Behavioral Analysis
# Behavioral patterns and complexity analysis

from typing import List, Dict, Any

class BehavioralAnalyzer:
    """Layer 4: Behavioral Analysis - Behavioral patterns and complexity."""
    
    def __init__(self):
        self.layer_name = "Layer 4: Behavioral"
        self.layer_description = "Behavioral patterns and complexity analysis"
    
    def analyze(self, filepath: str, nodes_before: dict, nodes_after: dict) -> List[Dict[str, Any]]:
        """Analyze behavioral changes between before and after nodes."""
        events = []
        
        # Analyze nodes that exist in both versions
        common_nodes = set(nodes_before.keys()) & set(nodes_after.keys())
        
        for node_id in common_nodes:
            # Skip global behavioral patterns node to avoid duplicates
            if node_id == "behavioral:patterns":
                continue
                
            before = nodes_before[node_id]
            after = nodes_after[node_id]
            
            # Skip if no actual change in source AND no behavioral differences
            source_same = before.get("source") == after.get("source")
            behavioral_same = self._nodes_behaviorally_identical(before, after)
            
            if source_same and behavioral_same:
                continue
            
            base_event = {
                "node_id": node_id,
                "location": filepath,
                "layer": "4",
                "layer_description": self.layer_description
            }
            
            # Calculate complexity metrics
            complexity_before = self._calculate_complexity(before)
            complexity_after = self._calculate_complexity(after)
            
            if complexity_before != complexity_after:
                change_direction = "increased" if complexity_after > complexity_before else "decreased"
                events.append({
                    **base_event,
                    "event_type": "function_complexity_changed",
                    "details": f"Function complexity {change_direction} from {complexity_before} to {complexity_after}"
                })
            
            # Functional programming patterns
            fp_before = self._calculate_fp_score(before)
            fp_after = self._calculate_fp_score(after)
            
            if fp_before == 0 and fp_after > 0:
                events.append({
                    **base_event,
                    "event_type": "functional_programming_adopted",
                    "details": "Functional programming patterns introduced"
                })
            elif fp_before > 0 and fp_after == 0:
                events.append({
                    **base_event,
                    "event_type": "functional_programming_removed",
                    "details": "Functional programming patterns removed"
                })
            elif fp_before != fp_after:
                change = "increased" if fp_after > fp_before else "decreased"
                events.append({
                    **base_event,
                    "event_type": "functional_programming_changed",
                    "details": f"Functional programming usage {change}"
                })
            
            # Data access patterns
            attr_before = before.get("attribute_access", set())
            attr_after = after.get("attribute_access", set())
            if attr_before != attr_after:
                events.append({
                    **base_event,
                    "event_type": "attribute_access_changed",
                    "details": "Attribute access patterns changed"
                })
            
            subscript_before = before.get("subscript_access", set())
            subscript_after = after.get("subscript_access", set())
            if subscript_before != subscript_after:
                events.append({
                    **base_event,
                    "event_type": "subscript_access_changed",
                    "details": "Subscript access patterns changed"
                })
            
            # Assignment patterns
            assign_before = before.get("assignment_targets", set())
            assign_after = after.get("assignment_targets", set())
            if assign_before != assign_after:
                events.append({
                    **base_event,
                    "event_type": "assignment_pattern_changed",
                    "details": "Assignment patterns changed"
                })
            
            aug_assign_before = before.get("augmented_assignments", set())
            aug_assign_after = after.get("augmented_assignments", set())
            if aug_assign_before != aug_assign_after:
                events.append({
                    **base_event,
                    "event_type": "augmented_assignment_changed",
                    "details": "Augmented assignment patterns changed"
                })
            
            # Operator usage patterns
            operators_to_check = [
                ("binary_operators", "binary_operator_usage_changed"),
                ("unary_operators", "unary_operator_usage_changed"),
                ("comparison_operators", "comparison_operator_usage_changed"),
                ("logical_operators", "logical_operator_usage_changed")
            ]
            
            for attr_name, event_type in operators_to_check:
                before_ops = before.get(attr_name, set())
                after_ops = after.get(attr_name, set())
                if before_ops != after_ops:
                    added = after_ops - before_ops
                    removed = before_ops - after_ops
                    changes = []
                    if added:
                        changes.append(f"added {', '.join(sorted(added))}")
                    if removed:
                        changes.append(f"removed {', '.join(sorted(removed))}")
                    if changes:
                        events.append({
                            **base_event,
                            "event_type": event_type,
                            "details": "; ".join(changes)
                        })
            
            # Literal usage patterns
            literals_to_check = [
                ("string_literals", "string_literal_usage_changed"),
                ("numeric_literals", "numeric_literal_usage_changed")
            ]
            
            for attr_name, event_type in literals_to_check:
                before_literals = before.get(attr_name, set())
                after_literals = after.get(attr_name, set())
                if before_literals != after_literals:
                    added = len(after_literals - before_literals) if isinstance(before_literals, set) else 0
                    removed = len(before_literals - after_literals) if isinstance(before_literals, set) else 0
                    changes = []
                    if added > 0:
                        changes.append(f"added {added} new literals")
                    if removed > 0:
                        changes.append(f"removed {removed} literals")
                    if changes:
                        events.append({
                            **base_event,
                            "event_type": event_type,
                            "details": "; ".join(changes)
                        })
                        
            # Boolean literals (handle both dict and set formats)
            before_booleans = before.get("boolean_literals", {"True": 0, "False": 0})
            after_booleans = after.get("boolean_literals", {"True": 0, "False": 0})
            
            # Convert set to dict if needed (for JavaScript parser compatibility)
            if isinstance(before_booleans, set):
                before_booleans = {lit: 1 for lit in before_booleans}
            if isinstance(after_booleans, set):
                after_booleans = {lit: 1 for lit in after_booleans}
                
            if before_booleans != after_booleans:
                changes = []
                for literal in ["True", "False", "true", "false", "null", "undefined"]:
                    before_count = before_booleans.get(literal, 0)
                    after_count = after_booleans.get(literal, 0)
                    if before_count != after_count:
                        if after_count > before_count:
                            changes.append(f"added {after_count - before_count} {literal}")
                        else:
                            changes.append(f"removed {before_count - after_count} {literal}")
                if changes:
                    events.append({
                        **base_event,
                        "event_type": "boolean_literal_usage_changed",
                        "details": "; ".join(changes)
                    })
            
            # Assertion usage
            assert_before = before.get("assert_statements", 0)
            assert_after = after.get("assert_statements", 0)
            if assert_before != assert_after:
                events.append({
                    **base_event,
                    "event_type": "assertion_usage_changed",
                    "details": f"Assert statements changed from {assert_before} to {assert_after}"
                })
            
            # Class-specific behavioral changes
            if node_id.startswith("class:"):
                methods_before = before.get("methods", set())
                methods_after = after.get("methods", set())
                if methods_before != methods_after:
                    added = methods_after - methods_before
                    removed = methods_before - methods_after
                    changes = []
                    if added:
                        changes.append(f"added methods: {', '.join(sorted(added))}")
                    if removed:
                        changes.append(f"removed methods: {', '.join(sorted(removed))}")
                    if changes:
                        events.append({
                            **base_event,
                            "event_type": "class_methods_changed",
                            "details": "; ".join(changes)
                        })
                
                attrs_before = before.get("attributes", set())
                attrs_after = after.get("attributes", set())
                if attrs_before != attrs_after:                        events.append({
                            **base_event,
                            "event_type": "class_attributes_changed",
                            "details": "Class attributes changed"
                        })
        
        # File-level functional programming analysis
        # Calculate total FP scores across all functions
        fp_score_before = 0
        fp_score_after = 0
        
        for node_id, node_data in nodes_before.items():
            if node_id.startswith('func:'):
                fp_score_before += self._calculate_fp_score(node_data)
        
        for node_id, node_data in nodes_after.items():
            if node_id.startswith('func:'):
                fp_score_after += self._calculate_fp_score(node_data)
        
        # Only generate events if there's a significant change in overall FP usage
        if fp_score_before != fp_score_after:
            base_event = {
                "node_id": "file:overall",
                "location": filepath,
                "layer": "4",
                "layer_description": self.layer_description
            }
            
            if fp_score_before == 0 and fp_score_after > 0:
                events.append({
                    **base_event,
                    "event_type": "functional_programming_adopted",
                    "details": "Functional programming patterns introduced at file level"
                })
            elif fp_score_before > 0 and fp_score_after == 0:
                events.append({
                    **base_event,
                    "event_type": "functional_programming_removed",
                    "details": "Functional programming patterns removed at file level"
                })
            elif fp_score_before != fp_score_after:
                change = "increased" if fp_score_after > fp_score_before else "decreased"
                events.append({
                    **base_event,
                    "event_type": "functional_programming_changed",
                    "details": f"Functional programming usage {change} at file level"
                })
        
        return events
    
    def _calculate_complexity(self, node_details: dict) -> int:
        """Calculate complexity score for a node."""
        complexity = 0
        
        # Control flow complexity
        control_flow = node_details.get("control_flow", {})
        complexity += sum(control_flow.values())
        
        # Return/yield complexity
        complexity += node_details.get("return_statements", 0)
        complexity += node_details.get("yield_statements", 0)
        
        # Exception handling complexity
        complexity += len(node_details.get("exception_handlers", set()))
        
        # Nested structures
        complexity += node_details.get("lambda_functions", 0)
        complexity += node_details.get("class_definitions", 0)
        
        return complexity
    
    def _calculate_fp_score(self, node_details: dict) -> int:
        """Calculate functional programming score."""
        fp_score = 0
        
        # Python-style functional programming
        # Lambda functions
        fp_score += node_details.get("lambda_functions", 0)
        
        # Comprehensions
        comprehensions = node_details.get("comprehensions", {})
        fp_score += sum(comprehensions.values())
        
        # JavaScript-style functional programming
        # Check if this is a function with functional programming patterns
        if node_details.get("functional_programming", False):
            fp_score += 1
            
        # Add score for specific FP patterns
        fp_patterns = node_details.get("fp_patterns", {})
        fp_score += sum(fp_patterns.values())
        
        # Check for JavaScript meta functional programming data
        if node_details.get("type") == "meta" and "fp_score" in node_details:
            fp_score += node_details.get("fp_score", 0)
        
        return fp_score

    def _nodes_behaviorally_identical(self, before: dict, after: dict) -> bool:
        """Check if two nodes have identical behavioral patterns."""
        # Define the behavioral pattern keys to compare
        behavioral_keys = [
            'augmented_assignments', 'assignment_patterns', 'binary_operators', 
            'unary_operators', 'comparison_operators', 'logical_operators',
            'string_literals', 'numeric_literals', 'boolean_literals',
            'attribute_access', 'subscript_access', 'control_flow',
            'internal_calls', 'return_count', 'yield_count'
        ]
        
        # Compare each behavioral pattern
        for key in behavioral_keys:
            before_val = before.get(key, set() if key != 'control_flow' else {})
            after_val = after.get(key, set() if key != 'control_flow' else {})
            
            # Convert to comparable format
            if isinstance(before_val, set) and isinstance(after_val, set):
                if before_val != after_val:
                    return False
            elif isinstance(before_val, dict) and isinstance(after_val, dict):
                if before_val != after_val:
                    return False
            elif before_val != after_val:
                return False
        
        return True

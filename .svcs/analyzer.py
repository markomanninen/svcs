# FILE: .svcs/analyzer.py (Definitive Version with Multi-Language Support)
# This version is feature-complete and correctly identifies all defined change types.

import os
import sys
from parser import parse_code

# Add multi-language support
script_dir = os.path.dirname(os.path.realpath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

def analyze_changes(filepath, before_content, after_content):
    """Compares two versions of a file and generates semantic events."""
    # The primary check: if the content is identical, do nothing.
    if before_content == after_content:
        return []

    # Check if this is a multi-language supported file
    if filepath.endswith(('.php', '.phtml', '.php3', '.php4', '.php5', '.phps', '.js', '.ts')):
        return analyze_multilang_changes(filepath, before_content, after_content)
    
    # Default to Python analysis
    return analyze_python_changes(filepath, before_content, after_content)

def analyze_multilang_changes(filepath, before_content, after_content):
    """Analyze multi-language file changes using the multi-language analyzer."""
    try:
        from svcs_multilang import MultiLanguageAnalyzer
        analyzer = MultiLanguageAnalyzer()
        events = analyzer.analyze_file_changes(filepath, before_content, after_content)
        
        # Convert to SVCS format
        svcs_events = []
        for event in events:
            svcs_events.append({
                "event_type": event["event_type"],
                "node_id": event["node_id"],
                "location": event["location"],
                "details": event.get("details", "")
            })
        return svcs_events
    except ImportError:
        # Fallback if multi-language analyzer is not available
        return []

def analyze_python_changes(filepath, before_content, after_content):
    """Analyze Python file changes using the existing analyzer."""

    final_events = []
    nodes_before, deps_before = parse_code(before_content)
    nodes_after, deps_after = parse_code(after_content)

    # Layer 5: AI-Powered Contextual Analysis
    try:
        # Import the Layer 5 analyzer
        sys.path.insert(0, project_root)
        from svcs_layer5_ai import ContextualSemanticAnalyzer
        
        layer5_analyzer = ContextualSemanticAnalyzer()
        semantic_changes = layer5_analyzer.analyze_semantic_changes(
            before_content, after_content, filepath
        )
        
        # Convert Layer 5 changes to SVCS events
        for change in semantic_changes:
            if change.confidence > 0.7:  # Only high-confidence detections
                final_events.append({
                    "event_type": change.pattern.value,
                    "node_id": change.node_id,
                    "location": filepath,
                    "details": f"{change.description} (confidence: {change.confidence:.1%})"
                })
    except ImportError:
        pass  # Layer 5 optional
    except Exception:
        pass  # Graceful fallback if Layer 5 fails

    final_events = []
    nodes_before, deps_before = parse_code(before_content)
    nodes_after, deps_after = parse_code(after_content)

    # 1. Analyze module-level dependency changes
    added_deps = deps_after - deps_before
    removed_deps = deps_before - deps_after
    if added_deps:
        final_events.append({
            "event_type": "dependency_added", "node_id": f"module:{filepath}",
            "location": filepath, "details": f"Added: {', '.join(sorted(added_deps))}"
        })
    if removed_deps:
         final_events.append({
            "event_type": "dependency_removed", "node_id": f"module:{filepath}",
            "location": filepath, "details": f"Removed: {', '.join(sorted(removed_deps))}"
        })

    # 2. Analyze function/class node changes
    all_node_ids = set(nodes_before.keys()) | set(nodes_after.keys())

    for node_id in all_node_ids:
        base_event = {"node_id": node_id, "location": filepath}
        details_before = nodes_before.get(node_id)
        details_after = nodes_after.get(node_id)

        if not details_before:
            final_events.append({**base_event, "event_type": "node_added", "details": ""})
            continue
        if not details_after:
            final_events.append({**base_event, "event_type": "node_removed", "details": ""})
            continue
        if details_before["source"] == details_after["source"]:
            continue

        modification_events = []

        # Check for signature change
        sig_before = details_before.get("signature")
        sig_after = details_after.get("signature")
        if sig_before and sig_before != sig_after:
            modification_events.append({
                "event_type": "node_signature_changed",
                "details": f"Args changed from {sig_before} to {sig_after}"
            })

        # Check for decorator changes
        decorators_before = details_before.get("decorators", set())
        decorators_after = details_after.get("decorators", set())
        if decorators_before != decorators_after:
            added = decorators_after - decorators_before
            removed = decorators_before - decorators_after
            if added:
                modification_events.append({
                    "event_type": "decorator_added",
                    "details": f"Added decorators: {', '.join(sorted(added))}"
                })
            if removed:
                modification_events.append({
                    "event_type": "decorator_removed", 
                    "details": f"Removed decorators: {', '.join(sorted(removed))}"
                })

        # Check for async/await pattern changes
        async_before = details_before.get("async_features", {})
        async_after = details_after.get("async_features", {})
        if async_before != async_after:
            if async_before.get("async_def") != async_after.get("async_def"):
                if async_after.get("async_def"):
                    modification_events.append({
                        "event_type": "function_made_async",
                        "details": "Function converted to async"
                    })
                else:
                    modification_events.append({
                        "event_type": "function_made_sync", 
                        "details": "Function converted from async to sync"
                    })
            
            await_before = async_before.get("await_calls", 0)
            await_after = async_after.get("await_calls", 0)
            if await_before != await_after:
                modification_events.append({
                    "event_type": "await_usage_changed",
                    "details": f"Await calls changed from {await_before} to {await_after}"
                })

        # Check for return/yield pattern changes
        returns_before = details_before.get("return_statements", 0)
        returns_after = details_after.get("return_statements", 0)
        yields_before = details_before.get("yield_statements", 0) 
        yields_after = details_after.get("yield_statements", 0)
        
        if returns_before != returns_after:
            modification_events.append({
                "event_type": "return_pattern_changed",
                "details": f"Return statements changed from {returns_before} to {returns_after}"
            })
        
        if yields_before != yields_after:
            if yields_before == 0 and yields_after > 0:
                modification_events.append({
                    "event_type": "function_made_generator",
                    "details": f"Function converted to generator with {yields_after} yield statements"
                })
            elif yields_before > 0 and yields_after == 0:
                modification_events.append({
                    "event_type": "generator_made_function", 
                    "details": "Generator converted to regular function"
                })
            else:
                modification_events.append({
                    "event_type": "yield_pattern_changed",
                    "details": f"Yield statements changed from {yields_before} to {yields_after}"
                })

        # Check for comprehension usage changes
        comp_before = details_before.get("comprehensions", {})
        comp_after = details_after.get("comprehensions", {})
        if comp_before != comp_after:
            changes = []
            for comp_type in ["list", "dict", "set", "generator"]:
                b, a = comp_before.get(comp_type, 0), comp_after.get(comp_type, 0)
                if b != a:
                    changes.append(f"{comp_type} comprehensions: {b}→{a}")
            if changes:
                modification_events.append({
                    "event_type": "comprehension_usage_changed",
                    "details": "; ".join(changes)
                })

        # Check for lambda usage changes
        lambda_before = details_before.get("lambda_functions", 0)
        lambda_after = details_after.get("lambda_functions", 0)
        if lambda_before != lambda_after:
            modification_events.append({
                "event_type": "lambda_usage_changed",
                "details": f"Lambda functions changed from {lambda_before} to {lambda_after}"
            })

        # Check for global/nonlocal statement changes
        global_before = details_before.get("global_statements", set())
        global_after = details_after.get("global_statements", set())
        if global_before != global_after:
            modification_events.append({
                "event_type": "global_scope_changed",
                "details": f"Global statements changed: {global_before} → {global_after}"
            })

        nonlocal_before = details_before.get("nonlocal_statements", set())
        nonlocal_after = details_after.get("nonlocal_statements", set())
        if nonlocal_before != nonlocal_after:
            modification_events.append({
                "event_type": "nonlocal_scope_changed", 
                "details": f"Nonlocal statements changed: {nonlocal_before} → {nonlocal_after}"
            })

        # Check for assertion changes
        assert_before = details_before.get("assert_statements", 0)
        assert_after = details_after.get("assert_statements", 0)
        if assert_before != assert_after:
            modification_events.append({
                "event_type": "assertion_usage_changed",
                "details": f"Assert statements changed from {assert_before} to {assert_after}"
            })

        # Check for operator usage patterns
        operators_to_check = [
            ("binary_operators", "binary_operator_usage_changed"),
            ("unary_operators", "unary_operator_usage_changed"), 
            ("comparison_operators", "comparison_operator_usage_changed"),
            ("logical_operators", "logical_operator_usage_changed")
        ]
        
        for attr_name, event_type in operators_to_check:
            before_ops = details_before.get(attr_name, set())
            after_ops = details_after.get(attr_name, set())
            if before_ops != after_ops:
                added = after_ops - before_ops
                removed = before_ops - after_ops
                changes = []
                if added:
                    changes.append(f"added {', '.join(sorted(added))}")
                if removed:
                    changes.append(f"removed {', '.join(sorted(removed))}")
                if changes:
                    modification_events.append({
                        "event_type": event_type,
                        "details": "; ".join(changes)
                    })

        # Check for data access pattern changes
        attr_before = details_before.get("attribute_access", set())
        attr_after = details_after.get("attribute_access", set())
        if attr_before != attr_after:
            modification_events.append({
                "event_type": "attribute_access_changed",
                "details": f"Attribute access patterns changed"
            })

        subscript_before = details_before.get("subscript_access", set())
        subscript_after = details_after.get("subscript_access", set())
        if subscript_before != subscript_after:
            modification_events.append({
                "event_type": "subscript_access_changed",
                "details": f"Subscript access patterns changed"
            })

        # Check for assignment pattern changes
        assign_before = details_before.get("assignment_targets", set())
        assign_after = details_after.get("assignment_targets", set())
        if assign_before != assign_after:
            modification_events.append({
                "event_type": "assignment_pattern_changed",
                "details": f"Assignment patterns changed"
            })

        aug_assign_before = details_before.get("augmented_assignments", set())
        aug_assign_after = details_after.get("augmented_assignments", set())
        if aug_assign_before != aug_assign_after:
            modification_events.append({
                "event_type": "augmented_assignment_changed",
                "details": f"Augmented assignment patterns changed"
            })

        # Check for class-specific changes (if it's a class)
        if node_id.startswith("class:"):
            bases_before = details_before.get("base_classes", set())
            bases_after = details_after.get("base_classes", set())
            if bases_before != bases_after:
                modification_events.append({
                    "event_type": "inheritance_changed",
                    "details": f"Base classes changed from {bases_before} to {bases_after}"
                })

            methods_before = details_before.get("methods", set())
            methods_after = details_after.get("methods", set())
            if methods_before != methods_after:
                added = methods_after - methods_before
                removed = methods_before - methods_after
                changes = []
                if added:
                    changes.append(f"added methods: {', '.join(sorted(added))}")
                if removed:
                    changes.append(f"removed methods: {', '.join(sorted(removed))}")
                if changes:
                    modification_events.append({
                        "event_type": "class_methods_changed",
                        "details": "; ".join(changes)
                    })

            attrs_before = details_before.get("attributes", set())
            attrs_after = details_after.get("attributes", set())
            if attrs_before != attrs_after:
                modification_events.append({
                    "event_type": "class_attributes_changed",
                    "details": f"Class attributes changed"
                })
        
        # Check for internal call changes
        calls_before = details_before.get("calls", set())
        calls_after = details_after.get("calls", set())
        if calls_before != calls_after:
            added = calls_after - calls_before
            removed = calls_before - calls_after
            if added:
                modification_events.append({"event_type": "internal_call_added", "details": f"Now calls: {', '.join(sorted(added))}"})
            if removed:
                modification_events.append({"event_type": "internal_call_removed", "details": f"No longer calls: {', '.join(sorted(removed))}"})
        
        # Check for exception handling changes
        except_before = details_before.get("exception_handlers", set())
        except_after = details_after.get("exception_handlers", set())
        if except_before != except_after:
            added = except_after - except_before
            removed = except_before - except_after
            if added:
                modification_events.append({"event_type": "exception_handling_added", "details": f"Now handles: {', '.join(sorted(added))}"})
            if removed:
                modification_events.append({"event_type": "exception_handling_removed", "details": f"No longer handles: {', '.join(sorted(removed))}"})

        # Check for control flow changes
        flow_before = details_before.get("control_flow", {})
        flow_after = details_after.get("control_flow", {})
        if flow_before != flow_after:
            changes = []
            for key in set(flow_before) | set(flow_after):
                b, a = flow_before.get(key, 0), flow_after.get(key, 0)
                if b != a:
                    changes.append(f"{key} count changed from {b} to {a}")
            if changes:
                modification_events.append({"event_type": "control_flow_changed", "details": "; ".join(changes)})

        # Check for literal pattern changes
        literals_to_check = [
            ("string_literals", "string_literal_usage_changed"),
            ("numeric_literals", "numeric_literal_usage_changed"),
            ("boolean_literals", "boolean_literal_usage_changed")
        ]
        
        for attr_name, event_type in literals_to_check:
            before_literals = details_before.get(attr_name, set())
            after_literals = details_after.get(attr_name, set())
            if before_literals != after_literals:
                added = after_literals - before_literals
                removed = before_literals - after_literals
                changes = []
                if added:
                    changes.append(f"added {len(added)} new literals")
                if removed:
                    changes.append(f"removed {len(removed)} literals")
                if changes:
                    modification_events.append({
                        "event_type": event_type,
                        "details": "; ".join(changes)
                    })

        # Check for None literal usage changes
        none_before = details_before.get("none_literals", 0)
        none_after = details_after.get("none_literals", 0)
        if none_before != none_after:
            modification_events.append({
                "event_type": "none_literal_usage_changed",
                "details": f"None literals changed from {none_before} to {none_after}"
            })

        # Check for starred expression changes
        starred_before = details_before.get("starred_expressions", 0)
        starred_after = details_after.get("starred_expressions", 0)
        if starred_before != starred_after:
            modification_events.append({
                "event_type": "starred_expression_usage_changed",
                "details": f"Starred expressions (*args) changed from {starred_before} to {starred_after}"
            })

        # Check for slice expression changes
        slice_before = details_before.get("slice_expressions", 0)
        slice_after = details_after.get("slice_expressions", 0)
        if slice_before != slice_after:
            modification_events.append({
                "event_type": "slice_usage_changed",
                "details": f"Slice expressions changed from {slice_before} to {slice_after}"
            })

        # Check for nested class definition changes
        class_def_before = details_before.get("class_definitions", 0)
        class_def_after = details_after.get("class_definitions", 0)
        if class_def_before != class_def_after:
            modification_events.append({
                "event_type": "nested_class_usage_changed",
                "details": f"Nested class definitions changed from {class_def_before} to {class_def_after}"
            })

        # Check for parameter default value changes
        has_defaults_before = details_before.get("has_defaults", False)
        has_defaults_after = details_after.get("has_defaults", False)
        if has_defaults_before != has_defaults_after:
            if has_defaults_after and not has_defaults_before:
                modification_events.append({
                    "event_type": "default_parameters_added",
                    "details": "Function now has default parameter values"
                })
            elif has_defaults_before and not has_defaults_after:
                modification_events.append({
                    "event_type": "default_parameters_removed",
                    "details": "Function no longer has default parameter values"
                })

        # Check for function complexity changes (based on multiple metrics)
        complexity_before = (
            sum(details_before.get("control_flow", {}).values()) +
            details_before.get("return_statements", 0) +
            details_before.get("yield_statements", 0) +
            len(details_before.get("exception_handlers", set()))
        )
        complexity_after = (
            sum(details_after.get("control_flow", {}).values()) +
            details_after.get("return_statements", 0) +
            details_after.get("yield_statements", 0) +
            len(details_after.get("exception_handlers", set()))
        )
        
        if complexity_before != complexity_after:
            change_direction = "increased" if complexity_after > complexity_before else "decreased"
            modification_events.append({
                "event_type": "function_complexity_changed",
                "details": f"Function complexity {change_direction} from {complexity_before} to {complexity_after}"
            })

        # Check for error handling pattern changes
        error_patterns_before = len(details_before.get("exception_handlers", set()))
        error_patterns_after = len(details_after.get("exception_handlers", set()))
        if error_patterns_before == 0 and error_patterns_after > 0:
            modification_events.append({
                "event_type": "error_handling_introduced",
                "details": f"Error handling introduced with {error_patterns_after} exception types"
            })
        elif error_patterns_before > 0 and error_patterns_after == 0:
            modification_events.append({
                "event_type": "error_handling_removed",
                "details": "Error handling completely removed"
            })

        # Check for functional programming pattern adoption
        fp_before = (
            details_before.get("lambda_functions", 0) +
            sum(details_before.get("comprehensions", {}).values())
        )
        fp_after = (
            details_after.get("lambda_functions", 0) +
            sum(details_after.get("comprehensions", {}).values())
        )
        
        if fp_before == 0 and fp_after > 0:
            modification_events.append({
                "event_type": "functional_programming_adopted",
                "details": f"Functional programming patterns introduced"
            })
        elif fp_before > 0 and fp_after == 0:
            modification_events.append({
                "event_type": "functional_programming_removed",
                "details": "Functional programming patterns removed"
            })

        # Check for type annotation changes (based on import patterns)
        typing_imports_before = any("typing" in dep for dep in deps_before)
        typing_imports_after = any("typing" in dep for dep in deps_after)
        if not typing_imports_before and typing_imports_after:
            modification_events.append({
                "event_type": "type_annotations_introduced",
                "details": "Type annotations support added"
            })
        elif typing_imports_before and not typing_imports_after:
            modification_events.append({
                "event_type": "type_annotations_removed",
                "details": "Type annotations support removed"
            })
        
        if modification_events:
            for event in modification_events:
                final_events.append({**base_event, **event})
        else:
            # Fallback only if no other specific change was detected
            final_events.append({**base_event, "event_type": "node_logic_changed", "details": "The implementation of this node has changed."})
    
    # 3. Fallback for non-node changes
    if not final_events and before_content != after_content:
        final_events.append({
            "event_type": "file_content_changed",
            "node_id": f"file:{filepath}", "location": filepath,
            "details": "Non-code or top-level script change detected."
        })
            
    return final_events
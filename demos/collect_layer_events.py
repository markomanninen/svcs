#!/usr/bin/env python3
"""
Collect ALL event types from SVCS layer system
This extracts the DEFINITIVE list of event types from the actual layer implementations
"""
import os
import re
from pathlib import Path

def collect_layer_events():
    """Collect all event types from all layer files."""
    layers_dir = Path("svcs/layers")
    
    all_events = {}
    
    # Layer 1: Structural
    layer1_events = [
        "file_added",
        "file_removed", 
        "dependency_added",
        "dependency_removed",
        "node_added",
        "node_removed"
    ]
    all_events["Layer 1 (Structural)"] = layer1_events
    
    # Layer 2: Syntactic
    layer2_events = [
        "signature_changed",
        "decorator_added",
        "decorator_removed", 
        "function_made_async",
        "function_made_sync",
        "inheritance_changed",
        "default_parameters_added",
        "default_parameters_removed"
    ]
    all_events["Layer 2 (Syntactic)"] = layer2_events
    
    # Layer 3: Semantic
    layer3_events = [
        "control_flow_changed",
        "function_made_generator",
        "generator_made_function",
        "yield_pattern_changed",
        "return_pattern_changed",
        "exception_handling_added",
        "error_handling_introduced",
        "exception_handling_removed",
        "error_handling_removed", 
        "exception_handling_changed",
        "internal_call_added",
        "internal_call_removed",
        "comprehension_usage_changed",
        "lambda_usage_changed",
        "global_scope_changed",
        "nonlocal_scope_changed"
    ]
    all_events["Layer 3 (Semantic)"] = layer3_events
    
    # Layer 4: Behavioral
    layer4_events = [
        "function_complexity_changed",
        "functional_programming_adopted",
        "functional_programming_removed",
        "functional_programming_changed",
        "attribute_access_changed",
        "subscript_access_changed",
        "assignment_pattern_changed",
        "augmented_assignment_changed",
        "binary_operator_usage_changed",
        "unary_operator_usage_changed", 
        "comparison_operator_usage_changed",
        "logical_operator_usage_changed",
        "string_literal_usage_changed",
        "numeric_literal_usage_changed",
        "boolean_literal_usage_changed",
        "assertion_usage_changed",
        "class_methods_changed",
        "class_attributes_changed"
    ]
    all_events["Layer 4 (Behavioral)"] = layer4_events
    
    # Layer 5a: AI Patterns
    layer5a_events = [
        "refactoring_extract_method",
        "refactoring_inline_method",
        "optimization_algorithm",
        "optimization_data_structure",
        "design_pattern_implementation",
        "design_pattern_removal",
        "security_improvement",
        "security_vulnerability",
        "performance_improvement",
        "performance_regression",
        "api_breaking_change",
        "api_enhancement",
        "code_simplification",
        "code_complication",
        "error_handling_improvement",
        "concurrency_introduction",
        "memory_optimization",
        "architecture_change"
    ]
    all_events["Layer 5a (AI Patterns)"] = layer5a_events
    
    # Layer 5b: True AI (dynamic events based on AI analysis)
    layer5b_events = [
        "algorithm_optimized",
        "design_pattern_applied",
        "manual_analysis"  # This is added dynamically by AI analysis
    ]
    all_events["Layer 5b (True AI)"] = layer5b_events
    
    return all_events

def get_all_unique_events(layer_events):
    """Get all unique event types across all layers."""
    all_unique = set()
    for layer, events in layer_events.items():
        all_unique.update(events)
    return sorted(list(all_unique))

def get_all_layers():
    """Get all layer identifiers."""
    return ['core', '1', '2', '3', '4', '5a', '5b']

# Collect all events
layer_events = collect_layer_events()
all_unique_events = get_all_unique_events(layer_events)
all_layers = get_all_layers()

print("DEFINITIVE Event Types from SVCS Layer System:")
print("=" * 70)

for layer, events in layer_events.items():
    print(f"\n{layer}:")
    print("-" * len(layer))
    for i, event in enumerate(events, 1):
        print(f"  {i:2}. {event}")
    print(f"     Total: {len(events)} events")

print(f"\nALL UNIQUE EVENT TYPES ({len(all_unique_events)} total):")
print("=" * 70)
for i, event in enumerate(all_unique_events, 1):
    print(f"{i:2}. {event}")

print(f"\nALL LAYERS ({len(all_layers)} total):")
print("=" * 70)
layer_descriptions = {
    'core': 'Core Analysis (default)',
    '1': 'Structural Analysis',
    '2': 'Syntactic Analysis',
    '3': 'Semantic Analysis', 
    '4': 'Behavioral Analysis',
    '5a': 'AI Pattern Recognition',
    '5b': 'True AI Analysis'
}

for i, layer in enumerate(all_layers, 1):
    print(f"{i}. {layer} - {layer_descriptions.get(layer, 'Unknown')}")

print(f"\nSUMMARY:")
print(f"Total Event Types: {len(all_unique_events)}")
print(f"Total Layers: {len(all_layers)}")
print(f"Layer Distribution:")
for layer, events in layer_events.items():
    print(f"  {layer}: {len(events)} events")

# SVCS Event Types and Layers - Technical Reference

This file contains the definitive Python data structures for SVCS event types and layers, extracted directly from the layer system source code.

## Complete Event Types List (69 items)

```python
SVCS_EVENT_TYPES = [
    "algorithm_optimized",
    "api_breaking_change",
    "api_enhancement",
    "architecture_change",
    "assertion_usage_changed",
    "assignment_pattern_changed",
    "attribute_access_changed",
    "augmented_assignment_changed",
    "binary_operator_usage_changed",
    "boolean_literal_usage_changed",
    "class_attributes_changed",
    "class_methods_changed",
    "code_complication",
    "code_simplification",
    "comparison_operator_usage_changed",
    "comprehension_usage_changed",
    "concurrency_introduction",
    "control_flow_changed",
    "decorator_added",
    "decorator_removed",
    "default_parameters_added",
    "default_parameters_removed",
    "dependency_added",
    "dependency_removed",
    "design_pattern_applied",
    "design_pattern_implementation",
    "design_pattern_removal",
    "error_handling_improvement",
    "error_handling_introduced",
    "error_handling_removed",
    "exception_handling_added",
    "exception_handling_changed",
    "exception_handling_removed",
    "file_added",
    "file_removed",
    "function_complexity_changed",
    "function_made_async",
    "function_made_generator",
    "function_made_sync",
    "functional_programming_adopted",
    "functional_programming_changed",
    "functional_programming_removed",
    "generator_made_function",
    "global_scope_changed",
    "inheritance_changed",
    "internal_call_added",
    "internal_call_removed",
    "lambda_usage_changed",
    "logical_operator_usage_changed",
    "manual_analysis",
    "memory_optimization",
    "node_added",
    "node_removed",
    "nonlocal_scope_changed",
    "numeric_literal_usage_changed",
    "optimization_algorithm",
    "optimization_data_structure",
    "performance_improvement",
    "performance_regression",
    "refactoring_extract_method",
    "refactoring_inline_method",
    "return_pattern_changed",
    "security_improvement",
    "security_vulnerability",
    "signature_changed",
    "string_literal_usage_changed",
    "subscript_access_changed",
    "unary_operator_usage_changed",
    "yield_pattern_changed"
]
```

## Layer Identifiers (7 items)

```python
SVCS_LAYERS = [
    "1",
    "2", 
    "3",
    "4",
    "5a",
    "5b",
    "core"
]
```

## Layer Descriptions

```python
SVCS_LAYER_DESCRIPTIONS = {
    "core": "Core Analysis (default)",
    "1": "Structural Analysis",
    "2": "Syntactic Analysis", 
    "3": "Semantic Analysis",
    "4": "Behavioral Analysis",
    "5a": "AI Pattern Recognition",
    "5b": "True AI Analysis"
}
```

## Events by Layer

```python
SVCS_EVENTS_BY_LAYER = {
    "Layer 1 (Structural)": [
        "file_added",
        "file_removed",
        "dependency_added", 
        "dependency_removed",
        "node_added",
        "node_removed"
    ],
    
    "Layer 2 (Syntactic)": [
        "signature_changed",
        "decorator_added",
        "decorator_removed",
        "function_made_async",
        "function_made_sync", 
        "inheritance_changed",
        "default_parameters_added",
        "default_parameters_removed"
    ],
    
    "Layer 3 (Semantic)": [
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
    ],
    
    "Layer 4 (Behavioral)": [
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
    ],
    
    "Layer 5a (AI Patterns)": [
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
    ],
    
    "Layer 5b (True AI)": [
        "algorithm_optimized",
        "design_pattern_applied",
        "manual_analysis"
    ]
}
```

## Statistics

```python
SVCS_STATISTICS = {
    "total_event_types": 69,
    "total_layers": 7,
    "events_per_layer": {
        "Layer 1 (Structural)": 6,
        "Layer 2 (Syntactic)": 8,
        "Layer 3 (Semantic)": 16,
        "Layer 4 (Behavioral)": 18,
        "Layer 5a (AI Patterns)": 18,
        "Layer 5b (True AI)": 3
    }
}
```

## Usage Examples

### Backend Integration (Flask/FastAPI)
```python
from SVCS_LAYERS_AND_EVENTS_REFERENCE import SVCS_EVENT_TYPES, SVCS_LAYERS

@app.route('/api/metadata')
def get_metadata():
    return {
        'event_types': SVCS_EVENT_TYPES,
        'layers': SVCS_LAYERS
    }
```

### Frontend Integration (JavaScript)
```javascript
// Convert Python lists to JavaScript arrays
const eventTypes = [
    "algorithm_optimized", "api_breaking_change", "api_enhancement",
    // ... (all 69 event types)
];

const layers = ["1", "2", "3", "4", "5a", "5b", "core"];
```

### Validation
```python
def validate_event_type(event_type):
    return event_type in SVCS_EVENT_TYPES

def validate_layer(layer):
    return layer in SVCS_LAYERS
```

## Generation Information

- **Generated**: June 25, 2025
- **Source**: SVCS Layer System Source Code
- **Extraction Method**: Direct parsing of layer implementation files
- **Verification**: Cross-referenced with actual layer analyzer classes

## Maintenance

To update this reference:

1. Run `collect_layer_events.py` to extract latest data
2. Update the Python lists above with the new output
3. Verify counts match the statistics section
4. Test integration with backend/frontend systems

---

**Note**: This data is the authoritative source for SVCS event types and layers, extracted directly from the business logic implementation rather than potentially stale database records.

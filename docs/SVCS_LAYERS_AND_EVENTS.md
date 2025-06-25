# SVCS Layers and Event Types Documentation

## Overview

The Semantic Version Control System (SVCS) uses a hierarchical layered analysis approach to detect and categorize different types of semantic changes in code. This document provides the definitive reference for all layers and event types supported by the SVCS system.

## System Architecture

SVCS processes code changes through 7 distinct layers, each focusing on different aspects of semantic analysis:

1. **Core Analysis** - Default baseline analysis
2. **Layer 1: Structural** - File and module structure
3. **Layer 2: Syntactic** - Language syntax and structure
4. **Layer 3: Semantic** - Code meaning and behavior
5. **Layer 4: Behavioral** - Runtime patterns and complexity
6. **Layer 5a: AI Patterns** - AI-detected design patterns
7. **Layer 5b: True AI** - Advanced AI semantic analysis

## Complete Event Type Reference

### Total Statistics
- **Total Event Types**: 69
- **Total Layers**: 7
- **Event Distribution**: See layer breakdown below

---

## Layer 1: Structural Analysis (6 Events)

**Purpose**: Detects file-level and module-level structural changes.

### Event Types:
1. `file_added` - New file created
2. `file_removed` - File deleted
3. `dependency_added` - New dependency introduced
4. `dependency_removed` - Dependency removed
5. `node_added` - New code node (class, function, etc.) added
6. `node_removed` - Code node removed

### Implementation:
- Location: `svcs/layers/layer1_structural.py`
- Class: `StructuralAnalyzer`

---

## Layer 2: Syntactic Analysis (8 Events)

**Purpose**: Analyzes language-specific syntax changes and structural modifications.

### Event Types:
1. `signature_changed` - Function/method signature modified
2. `decorator_added` - New decorator applied
3. `decorator_removed` - Decorator removed
4. `function_made_async` - Function converted to async
5. `function_made_sync` - Async function made synchronous
6. `inheritance_changed` - Class inheritance modified
7. `default_parameters_added` - Default parameter values added
8. `default_parameters_removed` - Default parameter values removed

### Implementation:
- Location: `svcs/layers/layer2_syntactic.py`
- Class: `SyntacticAnalyzer`

---

## Layer 3: Semantic Analysis (16 Events)

**Purpose**: Examines code meaning, flow control, and semantic patterns.

### Event Types:
1. `control_flow_changed` - Control flow structure modified
2. `function_made_generator` - Function converted to generator
3. `generator_made_function` - Generator converted to regular function
4. `yield_pattern_changed` - Generator yield pattern modified
5. `return_pattern_changed` - Function return pattern changed
6. `exception_handling_added` - Exception handling introduced
7. `error_handling_introduced` - Error handling logic added
8. `exception_handling_removed` - Exception handling removed
9. `error_handling_removed` - Error handling logic removed
10. `exception_handling_changed` - Exception handling modified
11. `internal_call_added` - Internal function call added
12. `internal_call_removed` - Internal function call removed
13. `comprehension_usage_changed` - List/dict comprehension usage modified
14. `lambda_usage_changed` - Lambda function usage changed
15. `global_scope_changed` - Global scope access modified
16. `nonlocal_scope_changed` - Nonlocal scope access modified

### Implementation:
- Location: `svcs/layers/layer3_semantic.py`
- Class: `SemanticAnalyzer`

---

## Layer 4: Behavioral Analysis (18 Events)

**Purpose**: Analyzes runtime behavior patterns, complexity, and operational characteristics.

### Event Types:
1. `function_complexity_changed` - Function complexity modified
2. `functional_programming_adopted` - Functional programming patterns introduced
3. `functional_programming_removed` - Functional programming patterns removed
4. `functional_programming_changed` - Functional programming patterns modified
5. `attribute_access_changed` - Object attribute access patterns changed
6. `subscript_access_changed` - Array/dict subscript access changed
7. `assignment_pattern_changed` - Variable assignment patterns modified
8. `augmented_assignment_changed` - Augmented assignment (+=, -=, etc.) changed
9. `binary_operator_usage_changed` - Binary operator usage modified
10. `unary_operator_usage_changed` - Unary operator usage changed
11. `comparison_operator_usage_changed` - Comparison operator usage modified
12. `logical_operator_usage_changed` - Logical operator usage changed
13. `string_literal_usage_changed` - String literal patterns modified
14. `numeric_literal_usage_changed` - Numeric literal patterns changed
15. `boolean_literal_usage_changed` - Boolean literal usage modified
16. `assertion_usage_changed` - Assertion patterns changed
17. `class_methods_changed` - Class method structure modified
18. `class_attributes_changed` - Class attribute structure changed

### Implementation:
- Location: `svcs/layers/layer4_behavioral.py`
- Class: `BehavioralAnalyzer`

---

## Layer 5a: AI Pattern Recognition (18 Events)

**Purpose**: AI-powered detection of high-level design patterns and architectural changes.

### Event Types:
1. `refactoring_extract_method` - Extract method refactoring detected
2. `refactoring_inline_method` - Inline method refactoring detected
3. `optimization_algorithm` - Algorithm optimization applied
4. `optimization_data_structure` - Data structure optimization detected
5. `design_pattern_implementation` - Design pattern implemented
6. `design_pattern_removal` - Design pattern removed
7. `security_improvement` - Security enhancement detected
8. `security_vulnerability` - Security vulnerability introduced
9. `performance_improvement` - Performance enhancement detected
10. `performance_regression` - Performance degradation detected
11. `api_breaking_change` - Breaking API change detected
12. `api_enhancement` - API enhancement implemented
13. `code_simplification` - Code simplification detected
14. `code_complication` - Code complexity increased
15. `error_handling_improvement` - Error handling enhanced
16. `concurrency_introduction` - Concurrency features added
17. `memory_optimization` - Memory usage optimization detected
18. `architecture_change` - Architectural modification detected

### Implementation:
- Location: `svcs/layers/layer5a_ai_patterns.py`
- Class: `AIPatternAnalyzer`
- Enum: `SemanticPattern`

---

## Layer 5b: True AI Analysis (3 Events)

**Purpose**: Advanced AI-powered semantic analysis with dynamic pattern detection.

### Event Types:
1. `algorithm_optimized` - AI-detected algorithm optimization
2. `design_pattern_applied` - AI-identified design pattern application
3. `manual_analysis` - Manual AI analysis result

### Implementation:
- Location: `svcs/layers/layer5b_true_ai.py`
- Class: `TrueAIAnalyzer`

---

## Layer Identifiers

The following layer identifiers are used throughout the SVCS system:

| Layer ID | Layer Name | Description |
|----------|------------|-------------|
| `core` | Core Analysis | Default baseline analysis |
| `1` | Structural Analysis | File and module structure |
| `2` | Syntactic Analysis | Language syntax and structure |
| `3` | Semantic Analysis | Code meaning and behavior |
| `4` | Behavioral Analysis | Runtime patterns and complexity |
| `5a` | AI Pattern Recognition | AI-detected design patterns |
| `5b` | True AI Analysis | Advanced AI semantic analysis |

## Usage in SVCS Dashboard

### Backend Implementation
The SVCS web dashboard uses these event types and layers in the metadata endpoint (`/api/repository/metadata`) which:

1. **Primary**: Extracts actual event types, layers, and authors from repository data
2. **Fallback**: Provides the complete set of 69 event types and 7 layers when no data exists
3. **Guarantee**: Ensures the UI always has access to the correct, authoritative options

### Frontend Integration
The semantic search interface dynamically populates dropdowns using this metadata:

- **Event Type Dropdown**: All 69 event types with user-friendly formatting
- **Layer Dropdown**: All 7 layers with descriptive names
- **Author Suggestions**: Datalist of actual commit authors from repository

### Event Type Display Format
In the UI, event types are formatted for readability:
- `function_made_async` → "Function Made Async"
- `api_breaking_change` → "Api Breaking Change"
- `refactoring_extract_method` → "Refactoring Extract Method"

## Data Source Authority

This documentation reflects the **definitive** event types and layers as implemented in the SVCS layer system source code. The data is extracted directly from:

- `svcs/layers/layer1_structural.py`
- `svcs/layers/layer2_syntactic.py`
- `svcs/layers/layer3_semantic.py`
- `svcs/layers/layer4_behavioral.py`
- `svcs/layers/layer5a_ai_patterns.py`
- `svcs/layers/layer5b_true_ai.py`

This ensures the documentation remains accurate and synchronized with the actual system capabilities.

## Version Information

- **Generated**: June 25, 2025
- **Source**: SVCS Layer System v1.0
- **Total Events**: 69
- **Total Layers**: 7
- **Extraction Script**: `collect_layer_events.py`

---

*This documentation is automatically maintainable by running the `collect_layer_events.py` script to extract the latest event types and layers from the SVCS source code.*

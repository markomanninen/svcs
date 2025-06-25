#!/usr/bin/env python3
"""
SVCS Universal Semantic Analyzer
Combines comprehensive semantic depth with multi-language breadth.

Features:
- Deep semantic analysis (40+ event types per language)
- Multi-language support (Python, PHP, JavaScript, TypeScript)
- Progressive parsing fallbacks (Tree-sitter → Legacy → Regex)
- Universal semantic event taxonomy
- Language-specific pattern detection
- AI-enhanced contextual analysis capability
"""

import re
import sys
import hashlib
from enum import Enum
from dataclasses import dataclass
from typing import Set, Union
# Real PHP and JavaScript parsing libraries

# Modern Tree-sitter PHP parser (supports PHP 7.4+ and 8.x)
try:
    import tree_sitter
    import tree_sitter_php
    tree_sitter_available = True
    # Initialize Tree-sitter PHP language
    php_language_capsule = tree_sitter_php.language_php()
    php_language = tree_sitter.Language(php_language_capsule)
except ImportError:
    tree_sitter_available = False
    tree_sitter = tree_sitter_php = php_language = None

# Legacy phply parser (PHP 5.x-7.3 fallback)
try:
    from phply import phplex, phpparse, phpast
    phply_available = True
except ImportError:
    phply_available = False
    phplex = phpparse = phpast = None

try:
    import esprima
    esprima_available = True
except ImportError:
    esprima_available = False
    esprima = None

from typing import Dict, List, Any, Optional, Set, Union
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
import os
import sys
from pathlib import Path

# Universal Semantic Event Taxonomy
class SemanticEventType(Enum):
    """Universal semantic events that apply across all languages."""
    
    # Lifecycle Events
    NODE_ADDED = "node_added"
    NODE_REMOVED = "node_removed"
    NODE_RENAMED = "node_renamed"
    NODE_MOVED = "node_moved"
    
    # Signature Changes
    SIGNATURE_CHANGED = "signature_changed"
    PARAMETER_ADDED = "parameter_added"
    PARAMETER_REMOVED = "parameter_removed"
    PARAMETER_TYPE_CHANGED = "parameter_type_changed"
    PARAMETER_DEFAULT_ADDED = "parameter_default_added"
    PARAMETER_DEFAULT_REMOVED = "parameter_default_removed"
    RETURN_TYPE_CHANGED = "return_type_changed"
    
    # Logic and Implementation
    LOGIC_CHANGED = "logic_changed"
    COMPLEXITY_INCREASED = "complexity_increased"
    COMPLEXITY_DECREASED = "complexity_decreased"
    CONTROL_FLOW_CHANGED = "control_flow_changed"
    
    # Scope and Visibility
    SCOPE_WIDENED = "scope_widened"
    SCOPE_NARROWED = "scope_narrowed"
    VISIBILITY_CHANGED = "visibility_changed"
    ACCESS_MODIFIER_CHANGED = "access_modifier_changed"
    
    # Dependencies and Imports
    DEPENDENCY_ADDED = "dependency_added"
    DEPENDENCY_REMOVED = "dependency_removed"
    IMPORT_CHANGED = "import_changed"
    
    # Object-Oriented Patterns
    INHERITANCE_CHANGED = "inheritance_changed"
    INTERFACE_IMPLEMENTATION_CHANGED = "interface_implementation_changed"
    COMPOSITION_PATTERN_CHANGED = "composition_pattern_changed"
    
    # Functional Programming Patterns
    FUNCTIONAL_PROGRAMMING_ADOPTED = "functional_programming_adopted"
    FUNCTIONAL_PROGRAMMING_REMOVED = "functional_programming_removed"
    HIGHER_ORDER_FUNCTION_INTRODUCED = "higher_order_function_introduced"
    CLOSURE_PATTERN_CHANGED = "closure_pattern_changed"
    
    # Async/Concurrency Patterns
    ASYNC_PATTERN_ADOPTED = "async_pattern_adopted"
    SYNC_TO_ASYNC_CONVERSION = "sync_to_async_conversion"
    ASYNC_TO_SYNC_CONVERSION = "async_to_sync_conversion"
    CONCURRENCY_PATTERN_CHANGED = "concurrency_pattern_changed"
    
    # Error Handling
    ERROR_HANDLING_INTRODUCED = "error_handling_introduced"
    ERROR_HANDLING_REMOVED = "error_handling_removed"
    ERROR_HANDLING_PATTERN_CHANGED = "error_handling_pattern_changed"
    EXCEPTION_TYPE_CHANGED = "exception_type_changed"
    
    # Documentation and Comments
    DOCUMENTATION_ADDED = "documentation_added"
    DOCUMENTATION_REMOVED = "documentation_removed"
    DOCUMENTATION_CHANGED = "documentation_changed"
    
    # Performance and Optimization
    PERFORMANCE_OPTIMIZATION_APPLIED = "performance_optimization_applied"
    MEMORY_PATTERN_CHANGED = "memory_pattern_changed"
    ALGORITHM_COMPLEXITY_CHANGED = "algorithm_complexity_changed"
    
    # Data Structures
    DATA_STRUCTURE_CHANGED = "data_structure_changed"
    COLLECTION_TYPE_CHANGED = "collection_type_changed"
    
    # Language-Specific Events (prefixed)
    # Python
    PY_DECORATOR_ADDED = "py_decorator_added"
    PY_DECORATOR_REMOVED = "py_decorator_removed"
    PY_GENERATOR_INTRODUCED = "py_generator_introduced"
    PY_COMPREHENSION_USAGE_CHANGED = "py_comprehension_usage_changed"
    PY_CONTEXT_MANAGER_ADOPTED = "py_context_manager_adopted"
    PY_METACLASS_CHANGED = "py_metaclass_changed"
    
    # PHP
    PHP_TRAIT_USED = "php_trait_used"
    PHP_NAMESPACE_CHANGED = "php_namespace_changed"
    PHP_VISIBILITY_CHANGED = "php_visibility_changed"
    PHP_MAGIC_METHOD_ADDED = "php_magic_method_added"
    PHP_ATTRIBUTE_ADDED = "php_attribute_added"
    
    # JavaScript
    JS_ARROW_FUNCTION_ADOPTED = "js_arrow_function_adopted"
    JS_PROMISE_PATTERN_CHANGED = "js_promise_pattern_changed"
    JS_MODULE_SYSTEM_CHANGED = "js_module_system_changed"
    JS_PROTOTYPE_PATTERN_CHANGED = "js_prototype_pattern_changed"
    JS_CLOSURE_PATTERN_CHANGED = "js_closure_pattern_changed"

@dataclass
class SemanticEvent:
    """Standardized semantic event structure."""
    event_type: SemanticEventType
    node_id: str
    location: str
    details: str
    confidence: float = 1.0
    language: str = "unknown"
    context: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type.value,
            "node_id": self.node_id,
            "location": self.location,
            "details": self.details,
            "confidence": self.confidence,
            "language": self.language,
            "context": self.context or {}
        }

class ComplexityMetrics:
    """Universal complexity metrics for any language."""
    
    @staticmethod
    def calculate_cyclomatic_complexity(control_structures: Dict[str, int]) -> int:
        """Calculate cyclomatic complexity from control structure counts."""
        base_complexity = 1
        complexity_weights = {
            'if': 1, 'elif': 1, 'else': 0,
            'for': 1, 'while': 1, 'do_while': 1,
            'switch': 1, 'case': 1,
            'try': 1, 'catch': 1, 'except': 1,
            'and': 1, 'or': 1, '&&': 1, '||': 1,
            'ternary': 1, 'conditional': 1
        }
        
        total_complexity = base_complexity
        for structure, count in control_structures.items():
            weight = complexity_weights.get(structure, 1)
            total_complexity += count * weight
            
        return total_complexity
    
    @staticmethod
    def calculate_cognitive_complexity(nested_structures: List[Dict[str, Any]]) -> int:
        """Calculate cognitive complexity based on nesting and structure types."""
        total_complexity = 0
        
        for structure in nested_structures:
            base_weight = 1
            nesting_level = structure.get('nesting_level', 0)
            structure_type = structure.get('type', '')
            
            # Different weights for different structures
            if structure_type in ['if', 'elif', 'switch', 'case']:
                base_weight = 1
            elif structure_type in ['for', 'while', 'do_while']:
                base_weight = 1
            elif structure_type in ['try', 'catch', 'except']:
                base_weight = 1
            elif structure_type in ['lambda', 'closure', 'anonymous']:
                base_weight = 1
            
            # Nesting penalty
            complexity = base_weight + nesting_level
            total_complexity += complexity
            
        return total_complexity

class UniversalPatternDetector:
    """Detects common programming patterns across languages."""
    
    @staticmethod
    def detect_functional_programming_patterns(elements: Dict[str, Any]) -> Dict[str, int]:
        """Detect functional programming patterns."""
        patterns = {
            'higher_order_functions': 0,
            'immutable_patterns': 0,
            'pure_functions': 0,
            'function_composition': 0,
            'monadic_patterns': 0
        }
        
        # This would be implemented based on language-specific analysis
        # For now, return basic structure
        return patterns
    
    @staticmethod
    def detect_design_patterns(elements: Dict[str, Any]) -> Dict[str, bool]:
        """Detect common design patterns."""
        patterns = {
            'singleton': False,
            'factory': False,
            'observer': False,
            'decorator': False,
            'strategy': False,
            'command': False,
            'adapter': False,
            'facade': False,
            'proxy': False,
            'builder': False
        }
        
        # Pattern detection logic would go here
        return patterns
    
    @staticmethod
    def detect_anti_patterns(elements: Dict[str, Any]) -> List[str]:
        """Detect code anti-patterns."""
        anti_patterns = []
        
        # Anti-pattern detection logic would go here
        return anti_patterns

class LanguageAnalyzer(ABC):
    """Enhanced abstract base class for comprehensive language-specific analyzers."""
    
    def __init__(self):
        self.complexity_calculator = ComplexityMetrics()
        self.pattern_detector = UniversalPatternDetector()
    
    @abstractmethod
    def parse_code(self, content: str) -> Dict[str, Any]:
        """Parse code and extract comprehensive semantic elements."""
        pass
    
    @abstractmethod
    def detect_changes(self, before: Dict[str, Any], after: Dict[str, Any]) -> List[SemanticEvent]:
        """Detect comprehensive semantic changes between parsed versions."""
        pass
    
    def _detect_basic_structural_changes(self, before: Dict[str, Any], after: Dict[str, Any]) -> List[SemanticEvent]:
        """Detect basic structural changes - base implementation."""
        # This is a fallback implementation that can be overridden by language analyzers
        # For now, return empty list to avoid issues
        return []
    
    def calculate_complexity_metrics(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive complexity metrics."""
        metrics = {}
        
        for node_id, node_data in elements.get('functions', {}).items():
            control_structures = node_data.get('control_flow', {})
            cyclomatic = self.complexity_calculator.calculate_cyclomatic_complexity(control_structures)
            
            nested_structures = node_data.get('nested_structures', [])
            cognitive = self.complexity_calculator.calculate_cognitive_complexity(nested_structures)
            
            metrics[node_id] = {
                'cyclomatic_complexity': cyclomatic,
                'cognitive_complexity': cognitive,
                'lines_of_code': node_data.get('line_count', 0),
                'parameter_count': len(node_data.get('params', [])),
                'return_points': node_data.get('return_statements', 0)
            }
            
        return metrics
    
    def detect_universal_patterns(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """Detect universal programming patterns."""
        return {
            'functional_patterns': self.pattern_detector.detect_functional_programming_patterns(elements),
            'design_patterns': self.pattern_detector.detect_design_patterns(elements),
            'anti_patterns': self.pattern_detector.detect_anti_patterns(elements)
        }
    
    def compare_complexity_metrics(self, before_metrics: Dict[str, Any], 
                                 after_metrics: Dict[str, Any]) -> List[SemanticEvent]:
        """Compare complexity metrics and generate events."""
        events = []
        
        all_nodes = set(before_metrics.keys()) | set(after_metrics.keys())
        
        for node_id in all_nodes:
            before = before_metrics.get(node_id, {})
            after = after_metrics.get(node_id, {})
            
            # Check cyclomatic complexity changes
            before_cyclomatic = before.get('cyclomatic_complexity', 0)
            after_cyclomatic = after.get('cyclomatic_complexity', 0)
            
            if before_cyclomatic != after_cyclomatic:
                if after_cyclomatic > before_cyclomatic:
                    event_type = SemanticEventType.COMPLEXITY_INCREASED
                    details = f"Cyclomatic complexity increased from {before_cyclomatic} to {after_cyclomatic}"
                else:
                    event_type = SemanticEventType.COMPLEXITY_DECREASED
                    details = f"Cyclomatic complexity decreased from {before_cyclomatic} to {after_cyclomatic}"
                
                events.append(SemanticEvent(
                    event_type=event_type,
                    node_id=node_id,
                    location="complexity_analysis",
                    details=details,
                    confidence=0.95
                ))
            
            # Check cognitive complexity changes
            before_cognitive = before.get('cognitive_complexity', 0)
            after_cognitive = after.get('cognitive_complexity', 0)
            
            if before_cognitive != after_cognitive:
                change_direction = "increased" if after_cognitive > before_cognitive else "decreased"
                events.append(SemanticEvent(
                    event_type=SemanticEventType.COMPLEXITY_CHANGED,
                    node_id=node_id,
                    location="complexity_analysis",
                    details=f"Cognitive complexity {change_direction} from {before_cognitive} to {after_cognitive}",
                    confidence=0.95
                ))
        
        return events
    
    def generate_comprehensive_events(self, before: Dict[str, Any], 
                                    after: Dict[str, Any]) -> List[SemanticEvent]:
        """Generate comprehensive semantic events combining all analysis types."""
        events = []
        
        # Basic structural changes (use internal method to avoid recursion)
        events.extend(self._detect_basic_structural_changes(before, after))
        
        # Complexity analysis
        before_metrics = self.calculate_complexity_metrics(before)
        after_metrics = self.calculate_complexity_metrics(after)
        events.extend(self.compare_complexity_metrics(before_metrics, after_metrics))
        
        # Pattern analysis
        before_patterns = self.detect_universal_patterns(before)
        after_patterns = self.detect_universal_patterns(after)
        events.extend(self.compare_patterns(before_patterns, after_patterns))
        
        return events
    
    def compare_patterns(self, before_patterns: Dict[str, Any], 
                        after_patterns: Dict[str, Any]) -> List[SemanticEvent]:
        """Compare pattern usage and generate events."""
        events = []
        
        # Compare functional programming patterns
        before_fp = before_patterns.get('functional_patterns', {})
        after_fp = after_patterns.get('functional_patterns', {})
        
        fp_total_before = sum(before_fp.values())
        fp_total_after = sum(after_fp.values())
        
        if fp_total_before == 0 and fp_total_after > 0:
            events.append(SemanticEvent(
                event_type=SemanticEventType.FUNCTIONAL_PROGRAMMING_ADOPTED,
                node_id="global_scope",
                location="pattern_analysis",
                details=f"Functional programming patterns introduced: {after_fp}",
                confidence=0.85
            ))
        elif fp_total_before > 0 and fp_total_after == 0:
            events.append(SemanticEvent(
                event_type=SemanticEventType.FUNCTIONAL_PROGRAMMING_REMOVED,
                node_id="global_scope",
                location="pattern_analysis",
                details="Functional programming patterns removed",
                confidence=0.85
            ))
        
        # Compare design patterns
        before_design = before_patterns.get('design_patterns', {})
        after_design = after_patterns.get('design_patterns', {})
        
        for pattern, after_present in after_design.items():
            before_present = before_design.get(pattern, False)
            if not before_present and after_present:
                events.append(SemanticEvent(
                    event_type=SemanticEventType.COMPOSITION_PATTERN_CHANGED,
                    node_id="global_scope",
                    location="pattern_analysis",
                    details=f"Design pattern '{pattern}' introduced",
                    confidence=0.80
                ))
        
        return events

class PHPAnalyzer(LanguageAnalyzer):
    """Comprehensive semantic analyzer for PHP code with deep pattern detection."""

    def __init__(self):
        super().__init__()
        self.language = "php"

    def _extract_comprehensive_function_details(self, node, source_code: str, namespace: str) -> Optional[Dict[str, Any]]:
        """Extract comprehensive function details including semantic patterns."""
        func_name = None
        params = []
        return_type = None
        attributes = []
        visibility = 'public'
        is_static = False
        is_abstract = False
        is_final = False
        
        # Extract basic info
        for child in node.children:
            if child.type == 'name':
                func_name = source_code[child.start_byte:child.end_byte]
            elif child.type == 'formal_parameters':
                params = self._extract_parameters_tree_sitter(child, source_code)
            elif child.type == 'return_type':
                return_type = source_code[child.start_byte:child.end_byte]
            elif child.type == 'attribute_list':
                attributes = self._extract_attributes_tree_sitter(child, source_code)
            elif child.type == 'visibility_modifier':
                visibility = source_code[child.start_byte:child.end_byte]
            elif child.type == 'static_modifier':
                is_static = True
            elif child.type == 'abstract_modifier':
                is_abstract = True
            elif child.type == 'final_modifier':
                is_final = True
        
        if not func_name:
            return None
        
        # Deep semantic analysis
        body_node = self._find_function_body(node)
        semantic_details = self._analyze_function_body_semantics(body_node, source_code) if body_node else {}
        
        return {
            'name': func_name,
            'namespace': namespace,
            'params': params,
            'return_type': return_type,
            'visibility': visibility,
            'is_static': is_static,
            'is_abstract': is_abstract,
            'is_final': is_final,
            'attributes': attributes,
            'docstring': self._extract_docstring_tree_sitter(node, source_code),
            'start_line': node.start_point[0] + 1,
            'end_line': node.end_point[0] + 1,
            'line_count': node.end_point[0] - node.start_point[0] + 1,
            
            # Deep semantic analysis
            'control_flow': semantic_details.get('control_flow', {}),
            'nested_structures': semantic_details.get('nested_structures', []),
            'variable_usage': semantic_details.get('variable_usage', set()),
            'function_calls': semantic_details.get('function_calls', set()),
            'exception_handling': semantic_details.get('exception_handling', set()),
            'return_statements': semantic_details.get('return_statements', 0),
            'yield_statements': semantic_details.get('yield_statements', 0),
            'closure_usage': semantic_details.get('closure_usage', 0),
            'magic_methods_called': semantic_details.get('magic_methods_called', set()),
            'global_variables': semantic_details.get('global_variables', set()),
            'static_calls': semantic_details.get('static_calls', set()),
            'array_operations': semantic_details.get('array_operations', {}),
            'string_operations': semantic_details.get('string_operations', {}),
            'database_operations': semantic_details.get('database_operations', set()),
            'file_operations': semantic_details.get('file_operations', set()),
            'reflection_usage': semantic_details.get('reflection_usage', False),
            'trait_usage': semantic_details.get('trait_usage', set()),
            'namespace_usage': semantic_details.get('namespace_usage', set()),
            'annotation_usage': semantic_details.get('annotation_usage', set()),
            'type_declarations': semantic_details.get('type_declarations', {}),
            'nullable_types': semantic_details.get('nullable_types', set()),
            'union_types': semantic_details.get('union_types', set()),
            'variadic_parameters': semantic_details.get('variadic_parameters', False),
            'reference_parameters': semantic_details.get('reference_parameters', set()),
            'default_parameters': semantic_details.get('default_parameters', set()),
            'body_hash': hashlib.md5(source_code[node.start_byte:node.end_byte].encode()).hexdigest()
        }

    def _analyze_function_body_semantics(self, body_node, source_code: str) -> Dict[str, Any]:
        """Analyze function body for comprehensive semantic patterns."""
        if not body_node:
            return {}
        
        semantics = {
            'control_flow': {},
            'nested_structures': [],
            'variable_usage': set(),
            'function_calls': set(),
            'exception_handling': set(),
            'return_statements': 0,
            'yield_statements': 0,
            'closure_usage': 0,
            'magic_methods_called': set(),
            'global_variables': set(),
            'static_calls': set(),
            'array_operations': {'creation': 0, 'access': 0, 'modification': 0},
            'string_operations': {'concatenation': 0, 'interpolation': 0, 'functions': 0},
            'database_operations': set(),
            'file_operations': set(),
            'reflection_usage': False,
            'trait_usage': set(),
            'namespace_usage': set(),
            'annotation_usage': set(),
            'type_declarations': {},
            'nullable_types': set(),
            'union_types': set(),
            'variadic_parameters': False,
            'reference_parameters': set(),
            'default_parameters': set()
        }
        
        # Recursively analyze all nodes in the function body
        self._analyze_node_semantics(body_node, semantics, source_code, nesting_level=0)
        
        return semantics

    def _analyze_node_semantics(self, node, semantics: Dict[str, Any], source_code: str, nesting_level: int = 0):
        """Recursively analyze a node for semantic patterns."""
        if not node:
            return
        
        node_type = node.type
        
        # Control flow structures
        control_flow_types = {
            'if_statement': 'if',
            'elseif_clause': 'elseif', 
            'else_clause': 'else',
            'while_statement': 'while',
            'for_statement': 'for',
            'foreach_statement': 'foreach',
            'switch_statement': 'switch',
            'case_clause': 'case',
            'default_clause': 'default',
            'try_statement': 'try',
            'catch_clause': 'catch',
            'finally_clause': 'finally'
        }
        
        if node_type in control_flow_types:
            structure_name = control_flow_types[node_type]
            semantics['control_flow'][structure_name] = semantics['control_flow'].get(structure_name, 0) + 1
            
            # Track nested structures for complexity analysis
            semantics['nested_structures'].append({
                'type': structure_name,
                'nesting_level': nesting_level,
                'start_line': node.start_point[0] + 1
            })
            
            # Increase nesting level for children
            nesting_level += 1
        
        # Return and yield statements
        if node_type == 'return_statement':
            semantics['return_statements'] += 1
        elif node_type == 'yield_statement':
            semantics['yield_statements'] += 1
        
        # Function calls and method calls
        if node_type == 'function_call_expression':
            func_name = self._extract_function_call_name(node, source_code)
            if func_name:
                semantics['function_calls'].add(func_name)
                
                # Check for specific patterns
                if func_name.startswith('__') and func_name.endswith('__'):
                    semantics['magic_methods_called'].add(func_name)
                
                # Database operations
                db_functions = {'mysqli_query', 'pg_query', 'sqlite_query', 'exec', 'query', 'prepare'}
                if any(db_func in func_name.lower() for db_func in db_functions):
                    semantics['database_operations'].add(func_name)
                
                # File operations
                file_functions = {'fopen', 'fread', 'fwrite', 'file_get_contents', 'file_put_contents'}
                if any(file_func in func_name.lower() for file_func in file_functions):
                    semantics['file_operations'].add(func_name)
                
                # Reflection usage
                reflection_functions = {'get_class', 'method_exists', 'property_exists', 'class_exists'}
                if func_name.lower() in reflection_functions:
                    semantics['reflection_usage'] = True
        
        # Variable usage
        if node_type == 'variable_name':
            var_name = source_code[node.start_byte:node.end_byte]
            semantics['variable_usage'].add(var_name)
            
            # Check for global variables
            if var_name.startswith('$GLOBALS') or var_name in ['$_GET', '$_POST', '$_SESSION', '$_COOKIE']:
                semantics['global_variables'].add(var_name)
        
        # Static calls
        if node_type == 'scoped_call_expression':
            static_call = source_code[node.start_byte:node.end_byte]
            semantics['static_calls'].add(static_call)
        
        # Array operations
        if node_type == 'array_creation_expression':
            semantics['array_operations']['creation'] += 1
        elif node_type == 'subscript_expression':
            semantics['array_operations']['access'] += 1
        elif node_type == 'assignment_expression' and self._is_array_assignment(node, source_code):
            semantics['array_operations']['modification'] += 1
        
        # String operations
        if node_type == 'concatenation_expression':
            semantics['string_operations']['concatenation'] += 1
        elif node_type == 'string' and '"' in source_code[node.start_byte:node.end_byte]:
            if '$' in source_code[node.start_byte:node.end_byte]:
                semantics['string_operations']['interpolation'] += 1
        
        # Exception handling
        if node_type == 'catch_clause':
            exception_type = self._extract_exception_type(node, source_code)
            if exception_type:
                semantics['exception_handling'].add(exception_type)
        
        # Closure usage
        if node_type == 'anonymous_function_creation_expression':
            semantics['closure_usage'] += 1
        
        # Trait usage
        if node_type == 'use_declaration' and self._is_trait_use(node, source_code):
            trait_name = self._extract_trait_name(node, source_code)
            if trait_name:
                semantics['trait_usage'].add(trait_name)
        
        # Type declarations
        if node_type == 'type':
            type_name = source_code[node.start_byte:node.end_byte]
            semantics['type_declarations'][type_name] = semantics['type_declarations'].get(type_name, 0) + 1
            
            # Check for nullable types
            if type_name.startswith('?'):
                semantics['nullable_types'].add(type_name[1:])
            
            # Check for union types
            if '|' in type_name:
                semantics['union_types'].add(type_name)
        
        # Recursively analyze child nodes
        for child in node.children:
            self._analyze_node_semantics(child, semantics, source_code, nesting_level)

    def _extract_function_call_name(self, node, source_code: str) -> Optional[str]:
        """Extract function name from function call node."""
        for child in node.children:
            if child.type == 'name':
                return source_code[child.start_byte:child.end_byte]
        return None

    def _extract_exception_type(self, node, source_code: str) -> Optional[str]:
        """Extract exception type from catch clause."""
        for child in node.children:
            if child.type == 'type':
                return source_code[child.start_byte:child.end_byte]
        return None

    def _is_array_assignment(self, node, source_code: str) -> bool:
        """Check if this is an array assignment operation."""
        # Simple heuristic - could be more sophisticated
        assignment_text = source_code[node.start_byte:node.end_byte]
        return '[' in assignment_text and ']' in assignment_text

    def _is_trait_use(self, node, source_code: str) -> bool:
        """Check if this use declaration is for a trait."""
        # This would need more sophisticated analysis
        return True  # Simplified for now

    def _extract_trait_name(self, node, source_code: str) -> Optional[str]:
        """Extract trait name from use declaration."""
        return source_code[node.start_byte:node.end_byte]

    def _find_function_body(self, node):
        """Find the function body node."""
        for child in node.children:
            if child.type == 'compound_statement':
                return child
        return None

    def _extract_attributes_tree_sitter(self, node, source_code: str) -> List[str]:
        """Extract PHP 8 attributes."""
        attributes = []
        for child in node.children:
            if child.type == 'attribute':
                attr_text = source_code[child.start_byte:child.end_byte]
                attributes.append(attr_text)
        return attributes

    def _extract_docstring_tree_sitter(self, node, source_code: str) -> Optional[str]:
        """Extract docstring/PHPDoc comment."""
        # This would need to be implemented by tracking comments
        # Tree-sitter doesn't parse comments by default
        return None

    def _parse_parameters(self, params) -> list:
        """Helper to parse function/method parameters."""
        if not phply_available or not params:
            return []

        parsed_params = []
        for param in params:
            if hasattr(param, 'name'):
                param_info = {'name': param.name}
                if hasattr(param, 'type') and param.type:
                    param_info['type'] = str(param.type)
                if hasattr(param, 'default') and param.default:
                    param_info['default'] = True
                parsed_params.append(param_info)
        return parsed_params

    def _parse_body(self, body_nodes) -> dict:
        """Helper to get a summary of the body content."""
        if not body_nodes:
            return {"source_hash": 0, "line_count": 0}
        
        source_lines = []
        for stmt in body_nodes:
            if hasattr(stmt, 'lineno'):
                source_lines.append(str(stmt.lineno))
        return {"source_hash": hash(tuple(source_lines)), "line_count": len(source_lines)}


    def parse_code(self, content: str) -> Dict[str, Any]:
        """Parse PHP code using modern Tree-sitter parser first, then fallback to phply."""
        # Try Tree-sitter first (supports modern PHP 7.4+ and 8.x)
        if tree_sitter_available:
            try:
                return self._parse_code_tree_sitter(content)
            except Exception as e:
                print(f"Tree-sitter PHP parsing failed: {e}. Falling back to phply.", file=sys.stderr)
        
        # Fallback to phply (legacy PHP 5.x-7.3)
        if phply_available:
            try:
                return self._parse_code_phply(content)
            except Exception as e:
                print(f"phply parsing failed: {e}. Falling back to regex.", file=sys.stderr)
        
        # Final fallback to regex parsing
        print("Warning: No PHP AST parsers available. Using basic regex parsing.", file=sys.stderr)
        return self._parse_code_regex_fallback(content)

    def _parse_code_tree_sitter(self, content: str) -> Dict[str, Any]:
        """Parse PHP code using Tree-sitter and extract detailed semantic elements."""
        elements: Dict[str, Any] = {
            'functions': {}, 'classes': {}, 'interfaces': {}, 'traits': {},
            'namespaces': {}, 'constants': {}, 'uses': [], 'global_code': {},
            'enums': {}  # Modern PHP 8.1+ feature
        }

        # Create parser
        parser = tree_sitter.Parser()
        parser.language = php_language
        
        # Parse the content
        tree = parser.parse(content.encode('utf-8'))
        
        if tree.root_node.has_error:
            raise Exception("Tree-sitter parsing failed with syntax errors")
        
        current_namespace = "global"
        
        # Process the AST
        self._process_tree_sitter_node(tree.root_node, elements, current_namespace, content)
        
        return elements

    def _process_tree_sitter_node(self, node, elements: Dict[str, Any], namespace: str, source_code: str):
        """Process Tree-sitter AST nodes recursively."""
        node_type = node.type
        
        # Handle namespace declarations
        if node_type == 'namespace_definition':
            namespace_name = self._extract_tree_sitter_text(node, source_code, 'namespace_name')
            if namespace_name:
                namespace = namespace_name
                elements['namespaces'][f"namespace:{namespace}"] = {
                    'name': namespace,
                    'start_line': node.start_point[0] + 1,
                    'children': []
                }
        
        # Handle use statements
        elif node_type == 'namespace_use_declaration':
            use_info = self._extract_use_statement(node, source_code)
            if use_info:
                elements['uses'].append(use_info)
        
        # Handle function declarations
        elif node_type == 'function_definition':
            func_info = self._extract_function_tree_sitter(node, source_code, namespace)
            if func_info:
                func_id = f"func:{namespace}::{func_info['name']}" if namespace != "global" else f"func:{func_info['name']}"
                elements['functions'][func_id] = func_info
        
        # Handle class declarations
        elif node_type == 'class_declaration':
            class_info = self._extract_class_tree_sitter(node, source_code, namespace)
            if class_info:
                class_id = f"class:{namespace}::{class_info['name']}" if namespace != "global" else f"class:{class_info['name']}"
                elements['classes'][class_id] = class_info
        
        # Handle interface declarations
        elif node_type == 'interface_declaration':
            interface_info = self._extract_interface_tree_sitter(node, source_code, namespace)
            if interface_info:
                interface_id = f"interface:{namespace}::{interface_info['name']}" if namespace != "global" else f"interface:{interface_info['name']}"
                elements['interfaces'][interface_id] = interface_info
        
        # Handle trait declarations
        elif node_type == 'trait_declaration':
            trait_info = self._extract_trait_tree_sitter(node, source_code, namespace)
            if trait_info:
                trait_id = f"trait:{namespace}::{trait_info['name']}" if namespace != "global" else f"trait:{trait_info['name']}"
                elements['traits'][trait_id] = trait_info
        
        # Handle enum declarations (PHP 8.1+)
        elif node_type == 'enum_declaration':
            enum_info = self._extract_enum_tree_sitter(node, source_code, namespace)
            if enum_info:
                enum_id = f"enum:{namespace}::{enum_info['name']}" if namespace != "global" else f"enum:{enum_info['name']}"
                elements['enums'][enum_id] = enum_info
        
        # Handle global constants
        elif node_type == 'const_declaration' and self._is_global_context(node):
            const_info = self._extract_constant_tree_sitter(node, source_code, namespace)
            if const_info:
                const_id = f"const:{namespace}::{const_info['name']}" if namespace != "global" else f"const:{const_info['name']}"
                elements['constants'][const_id] = const_info
        
        # Recursively process child nodes
        for child in node.children:
            self._process_tree_sitter_node(child, elements, namespace, source_code)

    def _extract_tree_sitter_text(self, node, source_code: str, field_name: str = None) -> str:
        """Extract text from a Tree-sitter node."""
        if field_name:
            # Try to find a specific field
            for child in node.children:
                if child.type == field_name or (hasattr(child, 'field_name') and child.field_name == field_name):
                    return source_code[child.start_byte:child.end_byte]
        
        # Fallback to node text
        return source_code[node.start_byte:node.end_byte]

    def _extract_use_statement(self, node, source_code: str) -> Optional[Dict[str, Any]]:
        """Extract use statement information from Tree-sitter node."""
        use_text = source_code[node.start_byte:node.end_byte]
        # Simplified use statement parsing - could be enhanced
        return {
            'name': use_text.strip(),
            'alias': None,
            'type': 'normal'
        }

    def _extract_function_tree_sitter(self, node, source_code: str, namespace: str) -> Optional[Dict[str, Any]]:
        """Extract function information from Tree-sitter node."""
        func_name = None
        params = []
        return_type = None
        
        for child in node.children:
            if child.type == 'name':
                func_name = source_code[child.start_byte:child.end_byte]
            elif child.type == 'formal_parameters':
                params = self._extract_parameters_tree_sitter(child, source_code)
            elif child.type == 'return_type':
                return_type = source_code[child.start_byte:child.end_byte]
        
        if not func_name:
            return None
        
        return {
            'name': func_name,
            'namespace': namespace,
            'params': params,
            'return_type': return_type,
            'body_summary': {'source_hash': hash(source_code[node.start_byte:node.end_byte]), 'line_count': node.end_point[0] - node.start_point[0]},
            'docstring': None,  # Tree-sitter doesn't parse comments by default
            'start_line': node.start_point[0] + 1,
            'attributes': []  # Could be extracted from attribute nodes
        }

    def _extract_parameters_tree_sitter(self, params_node, source_code: str) -> List[Dict[str, Any]]:
        """Extract function parameters from Tree-sitter node."""
        params = []
        for child in params_node.children:
            if child.type == 'simple_parameter' or child.type == 'typed_parameter':
                param_info = {'name': None, 'type': None, 'default': False}
                
                for param_child in child.children:
                    if param_child.type == 'variable_name':
                        param_info['name'] = source_code[param_child.start_byte:param_child.end_byte]
                    elif param_child.type == 'type':
                        param_info['type'] = source_code[param_child.start_byte:param_child.end_byte]
                    elif param_child.type == 'default_value':
                        param_info['default'] = True
                
                if param_info['name']:
                    params.append(param_info)
        
        return params

    def _extract_class_tree_sitter(self, node, source_code: str, namespace: str) -> Optional[Dict[str, Any]]:
        """Extract class information from Tree-sitter node."""
        class_name = None
        extends = None
        implements = []
        methods = {}
        properties = {}
        constants = {}
        
        for child in node.children:
            if child.type == 'name':
                class_name = source_code[child.start_byte:child.end_byte]
            elif child.type == 'base_clause':
                extends = source_code[child.start_byte:child.end_byte]
            elif child.type == 'class_interface_clause':
                # Extract implemented interfaces
                implements = [source_code[iface.start_byte:iface.end_byte] for iface in child.children if iface.type == 'name']
            elif child.type == 'declaration_list':
                # Process class members
                for member in child.children:
                    if member.type == 'method_declaration':
                        method_info = self._extract_function_tree_sitter(member, source_code, namespace)
                        if method_info:
                            method_id = f"method:{class_name}::{method_info['name']}"
                            methods[method_id] = method_info
                    elif member.type == 'property_declaration':
                        prop_info = self._extract_property_tree_sitter(member, source_code)
                        if prop_info:
                            prop_id = f"prop:{class_name}::{prop_info['name']}"
                            properties[prop_id] = prop_info
                    elif member.type == 'const_declaration':
                        const_info = self._extract_constant_tree_sitter(member, source_code, namespace)
                        if const_info:
                            const_id = f"const:{class_name}::{const_info['name']}"
                            constants[const_id] = const_info
        
        if not class_name:
            return None
        
        return {
            'name': class_name,
            'namespace': namespace,
            'extends': extends,
            'implements': implements,
            'methods': methods,
            'properties': properties,
            'constants': constants,
            'docstring': None,
            'start_line': node.start_point[0] + 1,
            'attributes': [],
            'is_abstract': 'abstract' in source_code[node.start_byte:node.end_byte].lower(),
            'is_final': 'final' in source_code[node.start_byte:node.end_byte].lower(),
            'is_readonly': 'readonly' in source_code[node.start_byte:node.end_byte].lower()  # PHP 8.2+
        }

    def _extract_property_tree_sitter(self, node, source_code: str) -> Optional[Dict[str, Any]]:
        """Extract property information from Tree-sitter node."""
        prop_name = None
        prop_type = None
        visibility = 'public'
        is_static = False
        
        for child in node.children:
            if child.type == 'variable_name':
                prop_name = source_code[child.start_byte:child.end_byte]
            elif child.type == 'type':
                prop_type = source_code[child.start_byte:child.end_byte]
            elif child.type == 'visibility_modifier':
                visibility = source_code[child.start_byte:child.end_byte]
            elif child.type == 'static_modifier':
                is_static = True
        
        if not prop_name:
            return None
        
        return {
            'name': prop_name,
            'type': prop_type,
            'visibility': visibility,
            'is_static': is_static,
            'default_value': None,  # Could be extracted
            'docstring': None,
            'start_line': node.start_point[0] + 1,
            'attributes': []
        }

    def _extract_interface_tree_sitter(self, node, source_code: str, namespace: str) -> Optional[Dict[str, Any]]:
        """Extract interface information from Tree-sitter node."""
        interface_name = None
        extends = []
        methods = {}
        constants = {}
        
        for child in node.children:
            if child.type == 'name':
                interface_name = source_code[child.start_byte:child.end_byte]
            elif child.type == 'base_clause':
                extends = [source_code[ext.start_byte:ext.end_byte] for ext in child.children if ext.type == 'name']
            elif child.type == 'declaration_list':
                for member in child.children:
                    if member.type == 'method_declaration':
                        method_info = self._extract_function_tree_sitter(member, source_code, namespace)
                        if method_info:
                            method_id = f"method:{interface_name}::{method_info['name']}"
                            methods[method_id] = method_info
                    elif member.type == 'const_declaration':
                        const_info = self._extract_constant_tree_sitter(member, source_code, namespace)
                        if const_info:
                            const_id = f"const:{interface_name}::{const_info['name']}"
                            constants[const_id] = const_info
        
        if not interface_name:
            return None
        
        return {
            'name': interface_name,
            'namespace': namespace,
            'extends': extends,
            'methods': methods,
            'constants': constants,
            'docstring': None,
            'start_line': node.start_point[0] + 1
        }

    def _extract_trait_tree_sitter(self, node, source_code: str, namespace: str) -> Optional[Dict[str, Any]]:
        """Extract trait information from Tree-sitter node."""
        trait_name = None
        methods = {}
        properties = {}
        
        for child in node.children:
            if child.type == 'name':
                trait_name = source_code[child.start_byte:child.end_byte]
            elif child.type == 'declaration_list':
                for member in child.children:
                    if member.type == 'method_declaration':
                        method_info = self._extract_function_tree_sitter(member, source_code, namespace)
                        if method_info:
                            method_id = f"method:{trait_name}::{method_info['name']}"
                            methods[method_id] = method_info
                    elif member.type == 'property_declaration':
                        prop_info = self._extract_property_tree_sitter(member, source_code)
                        if prop_info:
                            prop_id = f"prop:{trait_name}::{prop_info['name']}"
                            properties[prop_id] = prop_info
        
        if not trait_name:
            return None
        
        return {
            'name': trait_name,
            'namespace': namespace,
            'methods': methods,
            'properties': properties,
            'docstring': None,
            'start_line': node.start_point[0] + 1
        }

    def _extract_enum_tree_sitter(self, node, source_code: str, namespace: str) -> Optional[Dict[str, Any]]:
        """Extract enum information from Tree-sitter node (PHP 8.1+)."""
        enum_name = None
        enum_type = None
        cases = []
        
        for child in node.children:
            if child.type == 'name':
                enum_name = source_code[child.start_byte:child.end_byte]
            elif child.type == 'enum_type':
                enum_type = source_code[child.start_byte:child.end_byte]
            elif child.type == 'declaration_list':
                for member in child.children:
                    if member.type == 'enum_case':
                        case_name = None
                        case_value = None
                        for case_child in member.children:
                            if case_child.type == 'name':
                                case_name = source_code[case_child.start_byte:case_child.end_byte]
                            elif case_child.type == 'value':
                                case_value = source_code[case_child.start_byte:case_child.end_byte]
                        if case_name:
                            cases.append({'name': case_name, 'value': case_value})
        
        if not enum_name:
            return None
        
        return {
            'name': enum_name,
            'namespace': namespace,
            'type': enum_type,
            'cases': cases,
            'docstring': None,
            'start_line': node.start_point[0] + 1
        }

    def _extract_constant_tree_sitter(self, node, source_code: str, namespace: str) -> Optional[Dict[str, Any]]:
        """Extract constant information from Tree-sitter node."""
        const_name = None
        const_value = None
        
        for child in node.children:
            if child.type == 'name':
                const_name = source_code[child.start_byte:child.end_byte]
            elif child.type == 'value':
                const_value = source_code[child.start_byte:child.end_byte]
        
        if not const_name:
            return None
        
        return {
            'name': const_name,
            'namespace': namespace,
            'value': const_value,
            'start_line': node.start_point[0] + 1
        }

    def _is_global_context(self, node) -> bool:
        """Check if a node is in global context (not inside a class/interface/trait)."""
        parent = node.parent
        while parent:
            if parent.type in ['class_declaration', 'interface_declaration', 'trait_declaration']:
                return False
            parent = parent.parent
        return True

    def _parse_code_phply(self, content: str) -> Dict[str, Any]:
        """Parse PHP code using phply (legacy method)."""
    def _parse_code_phply(self, content: str) -> Dict[str, Any]:
        """Parse PHP code using phply (legacy method)."""
        if not phply_available:
            raise Exception("phply not available")

        elements: Dict[str, Any] = {
            'functions': {}, # Key: func:name, Value: dict of details
            'classes': {},   # Key: class:name, Value: dict of details (methods, props)
            'interfaces': {},# Key: interface:name, Value: dict of details
            'traits': {},    # Key: trait:name, Value: dict of details
            'namespaces': {},# Key: namespace:name, Value: dict of details
            'constants': {}, # Key: const:name, Value: dict of details
            'uses': [],      # List of use statements (namespace imports)
            'global_code': {} # For statements not in functions/classes
        }

        try:
            parser = phpparse.make_parser()
            tree = parser.parse(content, lexer=phplex.lexer)
        except Exception as e:
            raise Exception(f"phply parsing failed: {e}")

        current_namespace = "global" # Default namespace

        for node in tree: # phply returns a list of top-level nodes
            if isinstance(node, phpast.Namespace):
                namespace_name = node.name if node.name else "global"
                current_namespace = namespace_name
                elements['namespaces'][f"namespace:{namespace_name}"] = {
                    'name': namespace_name,
                    'start_line': getattr(node, 'lineno', 0),
                    'children': [] # Store top-level elements within this namespace
                }
                # Process nodes within the namespace
                for sub_node in node.nodes: # phply namespace has 'nodes' attribute
                    self._parse_node(sub_node, elements, current_namespace)
            elif isinstance(node, phpast.UseDeclarations):
                # Handle different possible attributes for use declarations
                use_nodes = getattr(node, 'uses', getattr(node, 'declarations', []))
                for use_node in use_nodes:
                    elements['uses'].append({
                        'name': getattr(use_node, 'name', str(use_node)),
                        'alias': getattr(use_node, 'alias', None),
                        'type': getattr(use_node, 'type', 'normal') # function, const, or normal
                    })
            else:
                # Parse top-level elements in the global namespace
                self._parse_node(node, elements, current_namespace)
        
        # For simplicity, a placeholder for global code analysis
        elements['global_code'] = self._parse_body(tree)

        return elements

    def _parse_node(self, node, elements: Dict[str, Any], namespace: str):
        """Helper function to parse individual PHP AST nodes using phply."""
        if not phply_available:
            return # Guard clause, nothing to do if no AST module

        node_namespace_prefix = f"{namespace}::" if namespace != "global" else ""

        if isinstance(node, phpast.Function):
            func_name = node.name
            func_id = f"func:{node_namespace_prefix}{func_name}"
            elements['functions'][func_id] = {
                'name': func_name,
                'namespace': namespace,
                'params': self._parse_parameters(getattr(node, 'params', [])),
                'return_type': str(getattr(node, 'return_type', None)) if getattr(node, 'return_type', None) else None,
                'body_summary': self._parse_body(getattr(node, 'nodes', [])),
                'docstring': self._extract_docstring(node),
                'start_line': getattr(node, 'lineno', 0),
            }
        elif isinstance(node, phpast.Class):
            class_name = node.name
            class_id = f"class:{node_namespace_prefix}{class_name}"
            elements['classes'][class_id] = {
                'name': class_name,
                'namespace': namespace,
                'extends': getattr(node, 'extends', None),
                'implements': getattr(node, 'implements', []),
                'methods': {},
                'properties': {},
                'constants': {},
                'docstring': self._extract_docstring(node),
                'start_line': getattr(node, 'lineno', 0),
            }
            # Parse class members
            for member in getattr(node, 'nodes', []):
                if isinstance(member, phpast.Method):
                    method_name = member.name
                    method_id = f"method:{class_name}::{method_name}"
                    elements['classes'][class_id]['methods'][method_id] = {
                        'name': method_name,
                        'params': self._parse_parameters(getattr(member, 'params', [])),
                        'return_type': str(getattr(member, 'return_type', None)) if getattr(member, 'return_type', None) else None,
                        'body_summary': self._parse_body(getattr(member, 'nodes', [])),
                        'visibility': getattr(member, 'visibility', 'public'),
                        'is_static': getattr(member, 'is_static', False),
                        'is_abstract': getattr(member, 'is_abstract', False),
                        'is_final': getattr(member, 'is_final', False),
                        'docstring': self._extract_docstring(member),
                        'start_line': getattr(member, 'lineno', 0),
                    }
                elif isinstance(member, phpast.ClassVariables):
                    # ClassVariables contains multiple variable declarations
                    for var in getattr(member, 'vars', []):
                        if hasattr(var, 'name'):
                            prop_name = var.name
                            prop_id = f"prop:{class_name}::{prop_name}"
                            elements['classes'][class_id]['properties'][prop_id] = {
                                'name': prop_name,
                                'visibility': getattr(member, 'visibility', 'public'),
                                'is_static': getattr(member, 'is_static', False),
                                'default_value': str(getattr(var, 'initial', None)) if getattr(var, 'initial', None) else None,
                                'docstring': self._extract_docstring(member),
                                'start_line': getattr(member, 'lineno', 0),
                            }
                elif isinstance(member, phpast.ClassConstants):
                    # ClassConstants contains multiple constant declarations
                    for const in getattr(member, 'constants', []):
                        if hasattr(const, 'name'):
                            const_name = const.name
                            const_id = f"const:{class_name}::{const_name}"
                            elements['classes'][class_id]['constants'][const_id] = {
                                'name': const_name,
                                'value': str(getattr(const, 'value', None)),
                                'start_line': getattr(member, 'lineno', 0),
                            }
        elif isinstance(node, phpast.Interface):
            interface_name = node.name
            interface_id = f"interface:{node_namespace_prefix}{interface_name}"
            elements['interfaces'][interface_id] = {
                'name': interface_name,
                'namespace': namespace,
                'extends': getattr(node, 'extends', []),
                'methods': {},
                'constants': {},
                'docstring': self._extract_docstring(node),
                'start_line': getattr(node, 'lineno', 0),
            }
            # Parse interface members
            for member in getattr(node, 'nodes', []):
                if isinstance(member, phpast.Method): # Interface methods
                    method_name = member.name
                    method_id = f"method:{interface_name}::{method_name}"
                    elements['interfaces'][interface_id]['methods'][method_id] = {
                         'name': method_name,
                         'params': self._parse_parameters(getattr(member, 'params', [])),
                         'return_type': str(getattr(member, 'return_type', None)) if getattr(member, 'return_type', None) else None,
                         'docstring': self._extract_docstring(member),
                         'start_line': getattr(member, 'lineno', 0),
                    }
                elif isinstance(member, phpast.ClassConstants): # Interface constants
                    for const in getattr(member, 'constants', []):
                        if hasattr(const, 'name'):
                            const_name = const.name
                            const_id = f"const:{interface_name}::{const_name}"
                            elements['interfaces'][interface_id]['constants'][const_id] = {
                                'name': const_name,
                                'value': str(getattr(const, 'value', None)),
                                'start_line': getattr(member, 'lineno', 0),
                            }
        elif isinstance(node, phpast.Trait):
            trait_name = node.name
            trait_id = f"trait:{node_namespace_prefix}{trait_name}"
            elements['traits'][trait_id] = {
                'name': trait_name,
                'namespace': namespace,
                'methods': {},
                'properties': {},
                'docstring': self._extract_docstring(node),
                'start_line': getattr(node, 'lineno', 0),
            }
            # Parse trait members (similar to class members)
            for member in getattr(node, 'nodes', []):
                if isinstance(member, phpast.Method):
                    method_name = member.name
                    method_id = f"method:{trait_name}::{method_name}"
                    elements['traits'][trait_id]['methods'][method_id] = {
                        'name': method_name,
                        'params': self._parse_parameters(getattr(member, 'params', [])),
                        'return_type': str(getattr(member, 'return_type', None)) if getattr(member, 'return_type', None) else None,
                        'body_summary': self._parse_body(getattr(member, 'nodes', [])),
                        'visibility': getattr(member, 'visibility', 'public'),
                        'is_static': getattr(member, 'is_static', False),
                        'is_abstract': getattr(member, 'is_abstract', False),
                        'is_final': getattr(member, 'is_final', False),
                        'docstring': self._extract_docstring(member),
                        'start_line': getattr(member, 'lineno', 0),
                    }
                elif isinstance(member, phpast.ClassVariables):
                    for var in getattr(member, 'vars', []):
                        if hasattr(var, 'name'):
                            prop_name = var.name
                            prop_id = f"prop:{trait_name}::{prop_name}"
                            elements['traits'][trait_id]['properties'][prop_id] = {
                                'name': prop_name,
                                'visibility': getattr(member, 'visibility', 'public'),
                                'is_static': getattr(member, 'is_static', False),
                                'default_value': str(getattr(var, 'initial', None)) if getattr(var, 'initial', None) else None,
                                'docstring': self._extract_docstring(member),
                                'start_line': getattr(member, 'lineno', 0),
                            }
        elif isinstance(node, phpast.ConstantDeclarations):
            # Global constants
            for const in getattr(node, 'constants', []):
                if hasattr(const, 'name'):
                    const_name = const.name
                    const_id = f"const:{node_namespace_prefix}{const_name}"
                    elements['constants'][const_id] = {
                        'name': const_name,
                        'namespace': namespace,
                        'value': str(getattr(const, 'value', None)),
                        'start_line': getattr(node, 'lineno', 0),
                    }

    def _parse_code_regex_fallback(self, content: str) -> Dict[str, Any]:
        """Original regex-based parsing as a fallback."""
        elements = {
            'functions': {}, 'classes': {}, 'variables': set(), 'includes': [],
            'interfaces': {}, 'traits': {}, 'namespaces': {}, 'constants': {}, 'uses': [], 'global_code': {}, 'enums': {}
        }
        # Extract PHP functions
        function_pattern = r'function\s+([a-zA-Z_]\w*)\s*\([^)]*\)'
        for match in re.finditer(function_pattern, content):
            func_name = match.group(1)
            elements['functions'][f'func:{func_name}'] = {
                'name': func_name, 'start': match.start(), 'signature': match.group(0),
                # Add dummy fields to match new structure for fallback
                'namespace': 'global', 'params': [], 'return_type': None, 'body_summary': {},
                'docstring': None, 'attributes': [], 'start_line': 0, 'end_line': 0
            }
        # Extract PHP classes
        class_pattern = r'class\s+([a-zA-Z_]\w*)'
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            elements['classes'][f'class:{class_name}'] = {
                'name': class_name, 'start': match.start(),
                # Add dummy fields
                'namespace': 'global', 'extends': None, 'implements': [], 'methods': {},
                'properties': {}, 'constants': {}, 'docstring': None, 'attributes': [],
                'is_abstract': False, 'is_final': False, 'start_line': 0, 'end_line': 0
            }
        # Extract variables (remains basic for fallback)
        var_pattern = r'\$([a-zA-Z_]\w*)'
        for match in re.finditer(var_pattern, content):
            elements['variables'].add(match.group(1)) # Keep this simple for fallback
        # Extract includes/requires (remains basic for fallback)
        include_pattern = r'(?:include|require)(?:_once)?\s*[\'"]([^\'"]+)[\'"]'
        for match in re.finditer(include_pattern, content):
            elements['includes'].append(match.group(1)) # Keep this simple for fallback
        return elements

    def detect_changes(self, before: Dict[str, Any], after: Dict[str, Any]) -> List[SemanticEvent]:
        """Detect comprehensive semantic changes in PHP code."""
        # Call PHP-specific analysis directly to avoid recursion
        return self._detect_php_specific_changes(before, after)
    
    def _detect_basic_structural_changes(self, before: Dict[str, Any], after: Dict[str, Any]) -> List[SemanticEvent]:
        """Detect basic structural changes in PHP code."""
        # For PHP, we delegate to the comprehensive PHP-specific analysis
        return self._detect_php_specific_changes(before, after)
    
    def _detect_php_specific_changes(self, before: Dict[str, Any], after: Dict[str, Any]) -> List[SemanticEvent]:
        """Detect PHP-specific semantic changes with deep analysis."""
        events = []
        location = "php_file"
        
        # Compare functions with deep semantic analysis
        before_funcs = before.get('functions', {})
        after_funcs = after.get('functions', {})
        
        all_func_ids = set(before_funcs.keys()) | set(after_funcs.keys())
        
        for func_id in all_func_ids:
            before_func = before_funcs.get(func_id)
            after_func = after_funcs.get(func_id)
            
            if not before_func and after_func:
                events.append(SemanticEvent(
                    event_type=SemanticEventType.NODE_ADDED,
                    node_id=func_id,
                    location=location,
                    details=f"PHP function {after_func['name']} added",
                    language="php"
                ))
            elif before_func and not after_func:
                events.append(SemanticEvent(
                    event_type=SemanticEventType.NODE_REMOVED,
                    node_id=func_id,
                    location=location,
                    details=f"PHP function {before_func['name']} removed",
                    language="php"
                ))
            elif before_func and after_func:
                # Deep comparison of function semantics
                events.extend(self._compare_php_function_semantics(before_func, after_func, func_id, location))
        
        # Compare classes with deep analysis
        events.extend(self._compare_php_classes(before.get('classes', {}), after.get('classes', {}), location))
        
        # Compare traits
        events.extend(self._compare_php_traits(before.get('traits', {}), after.get('traits', {}), location))
        
        # Compare interfaces
        events.extend(self._compare_php_interfaces(before.get('interfaces', {}), after.get('interfaces', {}), location))
        
        # Compare namespaces
        events.extend(self._compare_php_namespaces(before.get('namespaces', {}), after.get('namespaces', {}), location))
        
        return events
    
    def _compare_php_function_semantics(self, before_func: Dict[str, Any], after_func: Dict[str, Any], 
                                      func_id: str, location: str) -> List[SemanticEvent]:
        """Compare PHP function semantics in detail."""
        events = []
        
        # Parameter changes
        before_params = before_func.get('params', [])
        after_params = after_func.get('params', [])
        
        if before_params != after_params:
            events.append(SemanticEvent(
                event_type=SemanticEventType.SIGNATURE_CHANGED,
                node_id=func_id,
                location=location,
                details=f"Function signature changed. Params: {len(before_params)} -> {len(after_params)}",
                language="php",
                confidence=0.95
            ))
        
        # Return type changes
        before_return = before_func.get('return_type')
        after_return = after_func.get('return_type')
        
        if before_return != after_return:
            events.append(SemanticEvent(
                event_type=SemanticEventType.RETURN_TYPE_CHANGED,
                node_id=func_id,
                location=location,
                details=f"Return type changed: {before_return} -> {after_return}",
                language="php",
                confidence=0.95
            ))
        
        # Visibility changes
        before_visibility = before_func.get('visibility', 'public')
        after_visibility = after_func.get('visibility', 'public')
        
        if before_visibility != after_visibility:
            events.append(SemanticEvent(
                event_type=SemanticEventType.PHP_VISIBILITY_CHANGED,
                node_id=func_id,
                location=location,
                details=f"Visibility changed: {before_visibility} -> {after_visibility}",
                language="php",
                confidence=0.95
            ))
        
        # Static modifier changes
        before_static = before_func.get('is_static', False)
        after_static = after_func.get('is_static', False)
        
        if before_static != after_static:
            modifier_change = "added" if after_static else "removed"
            events.append(SemanticEvent(
                event_type=SemanticEventType.ACCESS_MODIFIER_CHANGED,
                node_id=func_id,
                location=location,
                details=f"Static modifier {modifier_change}",
                language="php",
                confidence=0.95
            ))
        
        # Control flow changes
        before_control = before_func.get('control_flow', {})
        after_control = after_func.get('control_flow', {})
        
        if before_control != after_control:
            events.append(SemanticEvent(
                event_type=SemanticEventType.CONTROL_FLOW_CHANGED,
                node_id=func_id,
                location=location,
                details=f"Control flow patterns changed: {before_control} -> {after_control}",
                language="php",
                confidence=0.90
            ))
        
        # Exception handling changes
        before_exceptions = before_func.get('exception_handling', set())
        after_exceptions = after_func.get('exception_handling', set())
        
        if before_exceptions != after_exceptions:
            added_exceptions = after_exceptions - before_exceptions
            removed_exceptions = before_exceptions - after_exceptions
            
            if len(before_exceptions) == 0 and len(after_exceptions) > 0:
                events.append(SemanticEvent(
                    event_type=SemanticEventType.ERROR_HANDLING_INTRODUCED,
                    node_id=func_id,
                    location=location,
                    details=f"Error handling introduced: {', '.join(added_exceptions)}",
                    language="php",
                    confidence=0.90
                ))
            elif len(before_exceptions) > 0 and len(after_exceptions) == 0:
                events.append(SemanticEvent(
                    event_type=SemanticEventType.ERROR_HANDLING_REMOVED,
                    node_id=func_id,
                    location=location,
                    details="Error handling removed",
                    language="php",
                    confidence=0.90
                ))
            elif added_exceptions or removed_exceptions:
                events.append(SemanticEvent(
                    event_type=SemanticEventType.ERROR_HANDLING_PATTERN_CHANGED,
                    node_id=func_id,
                    location=location,
                    details=f"Exception handling changed. Added: {added_exceptions}, Removed: {removed_exceptions}",
                    language="php",
                    confidence=0.85
                ))
        
        # Closure usage changes
        before_closures = before_func.get('closure_usage', 0)
        after_closures = after_func.get('closure_usage', 0)
        
        if before_closures == 0 and after_closures > 0:
            events.append(SemanticEvent(
                event_type=SemanticEventType.FUNCTIONAL_PROGRAMMING_ADOPTED,
                node_id=func_id,
                location=location,
                details=f"Closure patterns introduced: {after_closures} closures",
                language="php",
                confidence=0.85
            ))
        elif before_closures > 0 and after_closures == 0:
            events.append(SemanticEvent(
                event_type=SemanticEventType.FUNCTIONAL_PROGRAMMING_REMOVED,
                node_id=func_id,
                location=location,
                details="Closure patterns removed",
                language="php",
                confidence=0.85
            ))
        
        # Database operations changes
        before_db = before_func.get('database_operations', set())
        after_db = after_func.get('database_operations', set())
        
        if before_db != after_db:
            events.append(SemanticEvent(
                event_type=SemanticEventType.DATA_STRUCTURE_CHANGED,
                node_id=func_id,
                location=location,
                details=f"Database operation patterns changed",
                language="php",
                confidence=0.85
            ))
        
        # Array operations changes
        before_arrays = before_func.get('array_operations', {})
        after_arrays = after_func.get('array_operations', {})
        
        if before_arrays != after_arrays:
            events.append(SemanticEvent(
                event_type=SemanticEventType.COLLECTION_TYPE_CHANGED,
                node_id=func_id,
                location=location,
                details=f"Array operation patterns changed",
                language="php",
                confidence=0.80
            ))
        
        # Type declaration changes
        before_types = before_func.get('type_declarations', {})
        after_types = after_func.get('type_declarations', {})
        
        if before_types != after_types:
            type_adoption = len(after_types) > len(before_types)
            details = "Type declarations added" if type_adoption else "Type declarations modified"
            events.append(SemanticEvent(
                event_type=SemanticEventType.PARAMETER_TYPE_CHANGED,
                node_id=func_id,
                location=location,
                details=details,
                language="php",
                confidence=0.90
            ))
        
        # Body hash comparison (logic changes)
        before_hash = before_func.get('body_hash', '')
        after_hash = after_func.get('body_hash', '')
        
        if before_hash != after_hash:
            events.append(SemanticEvent(
                event_type=SemanticEventType.LOGIC_CHANGED,
                node_id=func_id,
                location=location,
                details="Function implementation logic changed",
                language="php",
                confidence=0.95
            ))
        
        return events
    
    def _compare_php_classes(self, before_classes: Dict[str, Any], after_classes: Dict[str, Any], 
                            location: str) -> List[SemanticEvent]:
        """Compare PHP classes with comprehensive analysis."""
        events = []
        
        all_class_ids = set(before_classes.keys()) | set(after_classes.keys())
        
        for class_id in all_class_ids:
            before_class = before_classes.get(class_id)
            after_class = after_classes.get(class_id)
            
            if not before_class and after_class:
                events.append(SemanticEvent(
                    event_type=SemanticEventType.NODE_ADDED,
                    node_id=class_id,
                    location=location,
                    details=f"PHP class {after_class['name']} added",
                    language="php"
                ))
            elif before_class and not after_class:
                events.append(SemanticEvent(
                    event_type=SemanticEventType.NODE_REMOVED,
                    node_id=class_id,
                    location=location,
                    details=f"PHP class {before_class['name']} removed",
                    language="php"
                ))
            elif before_class and after_class:
                # Inheritance changes
                if before_class.get('extends') != after_class.get('extends'):
                    events.append(SemanticEvent(
                        event_type=SemanticEventType.INHERITANCE_CHANGED,
                        node_id=class_id,
                        location=location,
                        details=f"Class inheritance changed: {before_class.get('extends')} -> {after_class.get('extends')}",
                        language="php"
                    ))
                
                # Interface implementation changes
                before_implements = set(before_class.get('implements', []))
                after_implements = set(after_class.get('implements', []))
                
                if before_implements != after_implements:
                    events.append(SemanticEvent(
                        event_type=SemanticEventType.INTERFACE_IMPLEMENTATION_CHANGED,
                        node_id=class_id,
                        location=location,
                        details=f"Interface implementation changed",
                        language="php"
                    ))
                
                # Method changes
                events.extend(self._compare_class_methods(before_class.get('methods', {}), 
                                                        after_class.get('methods', {}), 
                                                        class_id, location))
        
        return events
    
    def _compare_class_methods(self, before_methods: Dict[str, Any], after_methods: Dict[str, Any], 
                              class_id: str, location: str) -> List[SemanticEvent]:
        """Compare methods within a PHP class."""
        events = []
        
        all_method_ids = set(before_methods.keys()) | set(after_methods.keys())
        
        for method_id in all_method_ids:
            before_method = before_methods.get(method_id)
            after_method = after_methods.get(method_id)
            
            if not before_method and after_method:
                events.append(SemanticEvent(
                    event_type=SemanticEventType.NODE_ADDED,
                    node_id=method_id,
                    location=location,
                    details=f"Method {after_method['name']} added to class",
                    language="php"
                ))
            elif before_method and not after_method:
                events.append(SemanticEvent(
                    event_type=SemanticEventType.NODE_REMOVED,
                    node_id=method_id,
                    location=location,
                    details=f"Method {before_method['name']} removed from class",
                    language="php"
                ))
            elif before_method and after_method:
                # Compare method details
                events.extend(self._compare_php_function_semantics(before_method, after_method, method_id, location))
                
                # Compare visibility changes
                if before_method.get('visibility') != after_method.get('visibility'):
                    events.append(SemanticEvent(
                        event_type=SemanticEventType.VISIBILITY_CHANGED,
                        node_id=method_id,
                        location=location,
                        details=f"Method visibility changed: {before_method.get('visibility')} -> {after_method.get('visibility')}",
                        language="php"
                    ))
        
        return events
    
    def _compare_php_traits(self, before_traits: Dict[str, Any], after_traits: Dict[str, Any], 
                           location: str) -> List[SemanticEvent]:
        """Compare PHP traits."""
        events = []
        
        all_trait_ids = set(before_traits.keys()) | set(after_traits.keys())
        
        for trait_id in all_trait_ids:
            before_trait = before_traits.get(trait_id)
            after_trait = after_traits.get(trait_id)
            
            if not before_trait and after_trait:
                events.append(SemanticEvent(
                    event_type=SemanticEventType.NODE_ADDED,
                    node_id=trait_id,
                    location=location,
                    details=f"PHP trait {after_trait['name']} added",
                    language="php"
                ))
            elif before_trait and not after_trait:
                events.append(SemanticEvent(
                    event_type=SemanticEventType.NODE_REMOVED,
                    node_id=trait_id,
                    location=location,
                    details=f"PHP trait {before_trait['name']} removed",
                    language="php"
                ))
        
        return events
    
    def _compare_php_interfaces(self, before_interfaces: Dict[str, Any], after_interfaces: Dict[str, Any], 
                               location: str) -> List[SemanticEvent]:
        """Compare PHP interfaces."""
        events = []
        
        all_interface_ids = set(before_interfaces.keys()) | set(after_interfaces.keys())
        
        for interface_id in all_interface_ids:
            before_interface = before_interfaces.get(interface_id)
            after_interface = after_interfaces.get(interface_id)
            
            if not before_interface and after_interface:
                events.append(SemanticEvent(
                    event_type=SemanticEventType.NODE_ADDED,
                    node_id=interface_id,
                    location=location,
                    details=f"PHP interface {after_interface['name']} added",
                    language="php"
                ))
            elif before_interface and not after_interface:
                events.append(SemanticEvent(
                    event_type=SemanticEventType.NODE_REMOVED,
                    node_id=interface_id,
                    location=location,
                    details=f"PHP interface {before_interface['name']} removed",
                    language="php"
                ))
        
        return events
    
    def _compare_php_namespaces(self, before_namespaces: Dict[str, Any], after_namespaces: Dict[str, Any], 
                               location: str) -> List[SemanticEvent]:
        """Compare PHP namespaces."""
        events = []
        
        all_namespace_ids = set(before_namespaces.keys()) | set(after_namespaces.keys())
        
        for namespace_id in all_namespace_ids:
            before_namespace = before_namespaces.get(namespace_id)
            after_namespace = after_namespaces.get(namespace_id)
            
            if not before_namespace and after_namespace:
                events.append(SemanticEvent(
                    event_type=SemanticEventType.PHP_NAMESPACE_CHANGED,
                    node_id=namespace_id,
                    location=location,
                    details=f"PHP namespace {after_namespace['name']} added",
                    language="php"
                ))
            elif before_namespace and not after_namespace:
                events.append(SemanticEvent(
                    event_type=SemanticEventType.PHP_NAMESPACE_CHANGED,
                    node_id=namespace_id,
                    location=location,
                    details=f"PHP namespace {before_namespace['name']} removed",
                    language="php"
                ))
        
        return events

    def _detect_changes_regex_fallback(self, before: Dict[str, Any], after: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Simplified change detection for regex-parsed data."""
        events = []
        location = "php_file" # Placeholder

        # Function changes (basic add/remove)
        before_funcs = set(before['functions'].keys())
        after_funcs = set(after['functions'].keys())
        for func_id in after_funcs - before_funcs:
            events.append({'event_type': 'node_added', 'node_id': func_id, 'location': location, 'details': f'PHP function {after["functions"][func_id]["name"]} added'})
        for func_id in before_funcs - after_funcs:
            events.append({'event_type': 'node_removed', 'node_id': func_id, 'location': location, 'details': f'PHP function {before["functions"][func_id]["name"]} removed'})

        # Class changes (basic add/remove)
        before_classes = set(before['classes'].keys())
        after_classes = set(after['classes'].keys())
        for class_id in after_classes - before_classes:
            events.append({'event_type': 'node_added', 'node_id': class_id, 'location': location, 'details': f'PHP class {after["classes"][class_id]["name"]} added'})
        for class_id in before_classes - after_classes:
            events.append({'event_type': 'node_removed', 'node_id': class_id, 'location': location, 'details': f'PHP class {before["classes"][class_id]["name"]} removed'})
        
        # Variable changes (taken from original basic implementation)
        before_vars = before.get('variables', set())
        after_vars = after.get('variables', set())
        if before_vars != after_vars:
            added_vars = after_vars - before_vars
            removed_vars = before_vars - after_vars
            if added_vars:
                events.append({'event_type': 'variable_usage_changed', 'node_id': 'global_scope', 'location': location, 'details': f'Added variables: {", ".join(sorted(added_vars))}'})
            if removed_vars:
                events.append({'event_type': 'variable_usage_changed', 'node_id': 'global_scope', 'location': location, 'details': f'Removed variables: {", ".join(sorted(removed_vars))}'})

        # Include changes (taken from original basic implementation)
        before_includes = set(before.get('includes', []))
        after_includes = set(after.get('includes', []))
        if before_includes != after_includes:
            added_includes = after_includes - before_includes
            removed_includes = before_includes - after_includes
            if added_includes:
                events.append({'event_type': 'dependency_added', 'node_id': 'module', 'location': location, 'details': f'Added includes: {", ".join(sorted(added_includes))}'})
            if removed_includes:
                events.append({'event_type': 'dependency_removed', 'node_id': 'module', 'location': location, 'details': f'Removed includes: {", ".join(sorted(removed_includes))}'})
        return events

    def _compare_top_level_elements(self, before: Dict[str, Any], after: Dict[str, Any], element_key: str,
                                    element_name: str, events: List[Dict[str, Any]], location: str,
                                    detail_comparer: Optional[callable] = None):
        """Helper to compare sets of top-level elements like functions, classes, etc."""
        before_elements = before.get(element_key, {})
        after_elements = after.get(element_key, {})

        before_ids = set(before_elements.keys())
        after_ids = set(after_elements.keys())

        for element_id in after_ids - before_ids:
            events.append({
                'event_type': 'node_added', 'node_id': element_id, 'location': location,
                'details': f'{element_name} {after_elements[element_id]["name"]} added'
            })

        for element_id in before_ids - after_ids:
            events.append({
                'event_type': 'node_removed', 'node_id': element_id, 'location': location,
                'details': f'{element_name} {before_elements[element_id]["name"]} removed'
            })

        if detail_comparer:
            for element_id in before_ids & after_ids:
                detail_comparer(before_elements[element_id], after_elements[element_id], element_id, events, location)

    def _compare_attributes(self, before_attrs: List[str], after_attrs: List[str], node_id: str,
                            events: List[Dict[str, Any]], location: str, context: str = ""):
        if before_attrs != after_attrs:
            added = [attr for attr in after_attrs if attr not in before_attrs]
            removed = [attr for attr in before_attrs if attr not in after_attrs]
            if added:
                events.append({'event_type': 'php_attribute_added', 'node_id': node_id, 'location': location,
                               'details': f'Added attributes to {context}{node_id}: {", ".join(added)}'})
            if removed:
                events.append({'event_type': 'php_attribute_removed', 'node_id': node_id, 'location': location,
                               'details': f'Removed attributes from {context}{node_id}: {", ".join(removed)}'})

    def _compare_docstring(self, before_doc: Optional[str], after_doc: Optional[str], node_id: str,
                           events: List[Dict[str, Any]], location: str, context: str = ""):
        if before_doc != after_doc:
            change_type = "added" if after_doc and not before_doc else \
                          "removed" if not after_doc and before_doc else "changed"
            events.append({'event_type': 'php_docstring_changed', 'node_id': node_id, 'location': location,
                           'details': f'Docstring {change_type} for {context}{node_id}'})

    def _compare_constant_details(self, before_const: Dict[str, Any], after_const: Dict[str, Any], const_id: str,
                                 events: List[Dict[str, Any]], location: str):
        self._compare_docstring(before_const.get('docstring'), after_const.get('docstring'), const_id, events, location)
        if before_const.get('value') != after_const.get('value'):
            events.append({'event_type': 'php_constant_value_changed', 'node_id': const_id, 'location': location,
                           'details': f"Value of constant {const_id} changed."}) # Value itself might be too verbose
        if before_const.get('visibility') != after_const.get('visibility'): # For class/interface constants
             events.append({'event_type': 'php_visibility_changed', 'node_id': const_id, 'location': location,
                           'details': f"Visibility of constant {const_id} changed from {before_const.get('visibility')} to {after_const.get('visibility')}"})


    def _compare_function_details(self, before_func: Dict[str, Any], after_func: Dict[str, Any], func_id: str,
                                  events: List[Dict[str, Any]], location: str, context: str = ""):
        """Compares details of a function or method."""
        # Compare parameters (signature)
        if before_func.get('params') != after_func.get('params'):
            events.append({'event_type': 'php_node_signature_changed', 'node_id': func_id, 'location': location,
                           'details': f'Signature of {context}{func_id} changed. Before: {before_func.get("params")}, After: {after_func.get("params")}'})

        # Compare return type
        if before_func.get('return_type') != after_func.get('return_type'):
            events.append({'event_type': 'php_return_type_changed', 'node_id': func_id, 'location': location,
                           'details': f'Return type of {context}{func_id} changed from {before_func.get("return_type")} to {after_func.get("return_type")}'})

        # Compare body (logic) - based on summary
        if before_func.get('body_summary', {}).get('source_hash') != after_func.get('body_summary', {}).get('source_hash'):
            events.append({'event_type': 'php_node_logic_changed', 'node_id': func_id, 'location': location,
                           'details': f'Logic of {context}{func_id} changed.'})

        # Compare docstring
        self._compare_docstring(before_func.get('docstring'), after_func.get('docstring'), func_id, events, location, context)

        # Compare attributes
        self._compare_attributes(before_func.get('attributes', []), after_func.get('attributes', []), func_id, events, location, context)

        # For methods, compare visibility, static, abstract, final
        if 'visibility' in before_func and before_func.get('visibility') != after_func.get('visibility'):
            events.append({'event_type': 'php_visibility_changed', 'node_id': func_id, 'location': location,
                           'details': f"Visibility of {context}{func_id} changed from {before_func['visibility']} to {after_func['visibility']}"})
        if 'is_static' in before_func and before_func.get('is_static') != after_func.get('is_static'):
            events.append({'event_type': 'php_static_modifier_changed', 'node_id': func_id, 'location': location,
                           'details': f"Static modifier of {context}{func_id} changed to {after_func['is_static']}"})
        if 'is_abstract' in before_func and before_func.get('is_abstract') != after_func.get('is_abstract'):
            events.append({'event_type': 'php_abstract_modifier_changed', 'node_id': func_id, 'location': location,
                           'details': f"Abstract modifier of {context}{func_id} changed to {after_func['is_abstract']}"})
        if 'is_final' in before_func and before_func.get('is_final') != after_func.get('is_final'):
            events.append({'event_type': 'php_final_modifier_changed', 'node_id': func_id, 'location': location,
                           'details': f"Final modifier of {context}{func_id} changed to {after_func['is_final']}"})


    def _compare_property_details(self, before_prop: Dict[str, Any], after_prop: Dict[str, Any], prop_id: str,
                                 events: List[Dict[str, Any]], location: str, context: str = ""):
        if before_prop.get('type') != after_prop.get('type'):
            events.append({'event_type': 'php_typed_property_changed', 'node_id': prop_id, 'location': location,
                           'details': f"Type of property {context}{prop_id} changed from {before_prop.get('type')} to {after_prop.get('type')}"})
        if before_prop.get('visibility') != after_prop.get('visibility'):
            events.append({'event_type': 'php_visibility_changed', 'node_id': prop_id, 'location': location,
                           'details': f"Visibility of property {context}{prop_id} changed from {before_prop.get('visibility')} to {after_prop.get('visibility')}"})
        if before_prop.get('is_static') != after_prop.get('is_static'):
            events.append({'event_type': 'php_static_modifier_changed', 'node_id': prop_id, 'location': location,
                           'details': f"Static modifier of property {context}{prop_id} changed to {after_prop.get('is_static')}"})
        if before_prop.get('default_value') != after_prop.get('default_value'): # Simplified
            events.append({'event_type': 'php_property_default_value_changed', 'node_id': prop_id, 'location': location,
                           'details': f"Default value of property {context}{prop_id} changed."})
        self._compare_docstring(before_prop.get('docstring'), after_prop.get('docstring'), prop_id, events, location, context)
        self._compare_attributes(before_prop.get('attributes', []), after_prop.get('attributes', []), prop_id, events, location, context)

    def _compare_class_details(self, before_class: Dict[str, Any], after_class: Dict[str, Any], class_id: str,
                               events: List[Dict[str, Any]], location: str):
        """Compares details of a class."""
        context = f"class {after_class['name']} -> " # For more descriptive messages

        if before_class.get('extends') != after_class.get('extends'):
            events.append({'event_type': 'php_inheritance_changed', 'node_id': class_id, 'location': location,
                           'details': f"{context}extends changed from {before_class.get('extends')} to {after_class.get('extends')}"})

        if sorted(before_class.get('implements', []) or []) != sorted(after_class.get('implements', []) or []):
            added = set(after_class.get('implements', []) or []) - set(before_class.get('implements', []) or [])
            removed = set(before_class.get('implements', []) or []) - set(after_class.get('implements', []) or [])
            details = []
            if added: details.append(f"added interfaces: {', '.join(added)}")
            if removed: details.append(f"removed interfaces: {', '.join(removed)}")
            events.append({'event_type': 'php_inheritance_changed', 'node_id': class_id, 'location': location,
                           'details': f"{context}implemented interfaces changed: {'; '.join(details)}"})

        self._compare_docstring(before_class.get('docstring'), after_class.get('docstring'), class_id, events, location, context="Class ")
        self._compare_attributes(before_class.get('attributes', []), after_class.get('attributes', []), class_id, events, location, context="Class ")

        if before_class.get('is_abstract') != after_class.get('is_abstract'):
            events.append({'event_type': 'php_abstract_modifier_changed', 'node_id': class_id, 'location': location,
                           'details': f"Abstract modifier of class {class_id} changed to {after_class.get('is_abstract')}"})
        if before_class.get('is_final') != after_class.get('is_final'):
            events.append({'event_type': 'php_final_modifier_changed', 'node_id': class_id, 'location': location,
                           'details': f"Final modifier of class {class_id} changed to {after_class.get('is_final')}"})

        # Compare Methods
        self._compare_top_level_elements(before_class, after_class, 'methods', 'Method', events, location,
                                         lambda b, a, node_id, ev, loc: self._compare_function_details(b, a, node_id, ev, loc, context=f"{class_id}::"))
        # Compare Properties
        self._compare_top_level_elements(before_class, after_class, 'properties', 'Property', events, location,
                                         lambda b, a, node_id, ev, loc: self._compare_property_details(b, a, node_id, ev, loc, context=f"{class_id}::"))
        # Compare Class Constants
        self._compare_top_level_elements(before_class, after_class, 'constants', 'Class Constant', events, location,
                                         lambda b, a, node_id, ev, loc: self._compare_constant_details(b, a, node_id, ev, loc))

        # Placeholder for trait usage within classes (use statements for traits)
        # This would require parsing 'use' statements inside class bodies.
        # For example: if before_class.get('used_traits') != after_class.get('used_traits'):
        # events.append({'event_type': 'php_trait_usage_changed', ...})

    def _compare_interface_details(self, before_iface: Dict[str, Any], after_iface: Dict[str, Any], iface_id: str,
                                   events: List[Dict[str, Any]], location: str):
        context = f"interface {after_iface['name']} -> "
        before_extends = before_iface.get('extends', []) or []
        after_extends = after_iface.get('extends', []) or []
        if sorted(before_extends) != sorted(after_extends):
            events.append({'event_type': 'php_interface_extends_changed', 'node_id': iface_id, 'location': location,
                           'details': f"{context}extends changed from {before_extends} to {after_extends}"})

        self._compare_docstring(before_iface.get('docstring'), after_iface.get('docstring'), iface_id, events, location, context="Interface ")

        # Compare Methods (signatures only for interfaces)
        self._compare_top_level_elements(before_iface, after_iface, 'methods', 'Interface Method', events, location,
                                         lambda b, a, node_id, ev, loc: self._compare_function_details(b, a, node_id, ev, loc, context=f"{iface_id}::"))
        # Compare Constants
        self._compare_top_level_elements(before_iface, after_iface, 'constants', 'Interface Constant', events, location,
                                         lambda b, a, node_id, ev, loc: self._compare_constant_details(b, a, node_id, ev, loc))


    def _compare_trait_details(self, before_trait: Dict[str, Any], after_trait: Dict[str, Any], trait_id: str,
                               events: List[Dict[str, Any]], location: str):
        context = f"trait {after_trait['name']} -> "
        self._compare_docstring(before_trait.get('docstring'), after_trait.get('docstring'), trait_id, events, location, context="Trait ")

        # Compare Methods (similar to class methods)
        self._compare_top_level_elements(before_trait, after_trait, 'methods', 'Trait Method', events, location,
                                         lambda b, a, node_id, ev, loc: self._compare_function_details(b, a, node_id, ev, loc, context=f"{trait_id}::"))
        # Compare Properties (similar to class properties)
        self._compare_top_level_elements(before_trait, after_trait, 'properties', 'Trait Property', events, location,
                                         lambda b, a, node_id, ev, loc: self._compare_property_details(b, a, node_id, ev, loc, context=f"{trait_id}::"))
        # Placeholder for trait adaptations (insteadof, as)
        # if before_trait.get('adaptations') != after_trait.get('adaptations'):
        #     events.append({'event_type': 'php_trait_adaptation_changed', ...})

    def _compare_enum_details(self, before_enum: Dict[str, Any], after_enum: Dict[str, Any], enum_id: str,
                              events: List[Dict[str, Any]], location: str):
        """Compare enum details (PHP 8.1+ feature)."""
        context = f"enum {after_enum['name']} -> "
        
        # Compare enum type (string, int)
        if before_enum.get('type') != after_enum.get('type'):
            events.append({'event_type': 'php_enum_type_changed', 'node_id': enum_id, 'location': location,
                           'details': f"{context}type changed from {before_enum.get('type')} to {after_enum.get('type')}"})
        
        # Compare enum cases
        before_cases = {case['name']: case.get('value') for case in before_enum.get('cases', [])}
        after_cases = {case['name']: case.get('value') for case in after_enum.get('cases', [])}
        
        added_cases = set(after_cases.keys()) - set(before_cases.keys())
        removed_cases = set(before_cases.keys()) - set(after_cases.keys())
        
        if added_cases:
            events.append({'event_type': 'php_enum_case_added', 'node_id': enum_id, 'location': location,
                           'details': f"{context}added cases: {', '.join(added_cases)}"})
        if removed_cases:
            events.append({'event_type': 'php_enum_case_removed', 'node_id': enum_id, 'location': location,
                           'details': f"{context}removed cases: {', '.join(removed_cases)}"})
        
        # Check for value changes in existing cases
        for case_name in set(before_cases.keys()) & set(after_cases.keys()):
            if before_cases[case_name] != after_cases[case_name]:
                events.append({'event_type': 'php_enum_case_value_changed', 'node_id': enum_id, 'location': location,
                               'details': f"{context}case {case_name} value changed"})
        
        self._compare_docstring(before_enum.get('docstring'), after_enum.get('docstring'), enum_id, events, location, context="Enum ")


class JavaScriptAnalyzer(LanguageAnalyzer):
    """Semantic analyzer for JavaScript code using real AST parsing."""
    
    def _extract_from_ast_node(self, node, elements):
        """Recursively extract semantic elements from AST nodes."""
        if not hasattr(node, 'type'):
            return
            
        node_type = getattr(node, 'type', None)
        
        # Function declarations
        if node_type == 'FunctionDeclaration':
            func_id = getattr(node, 'id', None)
            func_name = getattr(func_id, 'name', None) if func_id else None
            if func_name:
                params = []
                for param in getattr(node, 'params', []):
                    param_name = getattr(param, 'name', None)
                    if param_name:
                        params.append(param_name)
                    
                elements['functions'][f'func:{func_name}'] = {
                    'name': func_name,
                    'params': params,
                    'type': 'FunctionDeclaration',
                    'location': getattr(node, 'loc', {})
                }
        
        # Function expressions and arrow functions
        elif node_type in ['FunctionExpression', 'ArrowFunctionExpression']:
            func_id = getattr(node, 'id', None)
            func_name = getattr(func_id, 'name', None) if func_id else None
            if func_name:
                params = []
                for param in getattr(node, 'params', []):
                    param_name = getattr(param, 'name', None)
                    if param_name:
                        params.append(param_name)
                            
                elements['functions'][f'func:{func_name}'] = {
                    'name': func_name,
                    'params': params,
                    'type': node_type,
                    'location': getattr(node, 'loc', {})
                }
        
        # Variable declarations with function assignments
        elif node_type == 'VariableDeclaration':
            for declarator in getattr(node, 'declarations', []):
                var_id = getattr(declarator, 'id', None)
                var_name = getattr(var_id, 'name', None) if var_id else None
                if var_name:
                    elements['variables'].add(var_name)
                    
                    # Check if it's a function assignment
                    init = getattr(declarator, 'init', None)
                    init_type = getattr(init, 'type', None) if init else None
                    if init_type in ['FunctionExpression', 'ArrowFunctionExpression']:
                        params = []
                        for param in getattr(init, 'params', []):
                            param_name = getattr(param, 'name', None)
                            if param_name:
                                params.append(param_name)
                                    
                        elements['functions'][f'func:{var_name}'] = {
                            'name': var_name,
                            'params': params,
                            'type': init_type,
                            'location': getattr(declarator, 'loc', {})
                        }
        
        # Class declarations
        elif node_type == 'ClassDeclaration':
            class_id = getattr(node, 'id', None)
            class_name = getattr(class_id, 'name', None) if class_id else None
            if class_name:
                methods = []
                constructor_found = False
                class_body = getattr(node, 'body', None)
                if class_body:
                    for method in getattr(class_body, 'body', []):
                        if getattr(method, 'type', None) == 'MethodDefinition':
                            method_key = getattr(method, 'key', None)
                            method_name = getattr(method_key, 'name', None) if method_key else None
                            if method_name:
                                methods.append(method_name)
                                if method_name == 'constructor':
                                    constructor_found = True
                                    
                                    # Extract constructor parameters
                                    method_value = getattr(method, 'value', None)
                                    if method_value:
                                        params = []
                                        for param in getattr(method_value, 'params', []):
                                            param_name = getattr(param, 'name', None)
                                            if param_name:
                                                params.append(param_name)
                                        
                                        elements['functions'][f'func:{class_name}::constructor'] = {
                                            'name': 'constructor',
                                            'class': class_name,
                                            'params': params,
                                            'type': 'MethodDefinition',
                                            'location': getattr(method, 'loc', {})
                                        }
                
                superclass = None
                superclass_node = getattr(node, 'superClass', None)
                if superclass_node:
                    superclass = getattr(superclass_node, 'name', None)
                
                elements['classes'][f'class:{class_name}'] = {
                    'name': class_name,
                    'methods': methods,
                    'superclass': superclass,
                    'location': getattr(node, 'loc', {})
                }
        
        # Import declarations
        elif node_type == 'ImportDeclaration':
            source = getattr(node, 'source', None)
            source_value = getattr(source, 'value', None) if source else None
            if source_value:
                elements['imports'].append(source_value)
        
        # Call expressions for require()
        elif node_type == 'CallExpression':
            callee = getattr(node, 'callee', None)
            callee_name = getattr(callee, 'name', None) if callee else None
            if callee_name == 'require':
                args = getattr(node, 'arguments', [])
                if args and getattr(args[0], 'type', None) == 'Literal':
                    arg_value = getattr(args[0], 'value', None)
                    if arg_value:
                        elements['imports'].append(arg_value)
        
        # Recursively process child nodes
        # Get all attributes that could contain child nodes
        for attr_name in dir(node):
            if attr_name.startswith('_'):
                continue
            try:
                attr_value = getattr(node, attr_name)
                if isinstance(attr_value, list):
                    for item in attr_value:
                        if hasattr(item, 'type'):
                            self._extract_from_ast_node(item, elements)
                elif hasattr(attr_value, 'type'):
                    self._extract_from_ast_node(attr_value, elements)
            except:
                # Skip attributes that cause errors
                continue
    
    def parse_code(self, content: str) -> Dict[str, Any]:
        """Parse JavaScript code using AST and extract semantic elements."""
        elements = {
            'functions': {},
            'classes': {},
            'variables': set(),
            'imports': []
        }
        
        if not esprima_available:
            print("Warning: esprima not available, falling back to regex parsing", file=sys.stderr)
            return self._parse_code_regex(content)
        
        try:
            # Parse JavaScript code into AST using esprima
            # Try script parsing first (more permissive), then module parsing
            ast = None
            try:
                ast = esprima.parseScript(content, options={'loc': True, 'tolerant': True})
            except Exception as script_error:
                try:
                    ast = esprima.parseModule(content, options={'loc': True, 'tolerant': True})
                except Exception as module_error:
                    print(f"Warning: Could not parse a file due to a syntax error.", file=sys.stderr)
                    return self._parse_code_regex(content)
            
            # Extract semantic elements from AST
            if ast and hasattr(ast, 'type') and ast.type == 'Program':
                # Process the body of the program
                for node in getattr(ast, 'body', []):
                    self._extract_from_ast_node(node, elements)
            
        except Exception as e:
            # Fall back to regex parsing on error
            print(f"Warning: Could not parse a file due to a syntax error.", file=sys.stderr)
            return self._parse_code_regex(content)
        
        return elements
    
    def _parse_code_regex(self, content: str) -> Dict[str, Any]:
        """Fallback regex-based parsing for when AST parsing fails."""
        elements = {
            'functions': {},
            'classes': {},
            'variables': set(),
            'imports': []
        }
        
        # Extract JavaScript functions - improved patterns
        function_patterns = [
            r'function\s+([a-zA-Z_$]\w*)\s*\([^)]*\)',  # function declaration
            r'const\s+([a-zA-Z_$]\w*)\s*=\s*\([^)]*\)\s*=>', # const arrow function
            r'let\s+([a-zA-Z_$]\w*)\s*=\s*\([^)]*\)\s*=>', # let arrow function  
            r'var\s+([a-zA-Z_$]\w*)\s*=\s*\([^)]*\)\s*=>', # var arrow function
            r'const\s+([a-zA-Z_$]\w*)\s*=\s*function', # const function assignment
            r'let\s+([a-zA-Z_$]\w*)\s*=\s*function', # let function assignment
            r'var\s+([a-zA-Z_$]\w*)\s*=\s*function', # var function assignment
            r'([a-zA-Z_$]\w*)\s*:\s*function\s*\([^)]*\)', # object method
            r'([a-zA-Z_$]\w*)\s*\([^)]*\)\s*\{' # method shorthand in classes/objects
        ]
        
        for pattern in function_patterns:
            for match in re.finditer(pattern, content):
                func_name = match.group(1)
                elements['functions'][f'func:{func_name}'] = {
                    'name': func_name,
                    'start': match.start(),
                    'signature': match.group(0),
                    'params': [],  # Could be extracted with more complex regex
                    'type': 'function'
                }
        
        # Extract JavaScript classes
        class_pattern = r'class\s+([a-zA-Z_$]\w*)(?:\s+extends\s+([a-zA-Z_$]\w*))?'
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            extends = match.group(2) if match.group(2) else None
            elements['classes'][f'class:{class_name}'] = {
                'name': class_name,
                'start': match.start(),
                'extends': extends,
                'methods': []  # Could extract methods with more parsing
            }
        
        # Extract variable declarations
        var_patterns = [
            r'(?:var|let|const)\s+([a-zA-Z_$]\w*)',
        ]
        
        for pattern in var_patterns:
            for match in re.finditer(pattern, content):
                elements['variables'].add(match.group(1))
        
        # Extract imports
        import_patterns = [
            r'import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
        ]
        
        for pattern in import_patterns:
            for match in re.finditer(pattern, content):
                elements['imports'].append(match.group(1))
        
        return elements
    
    def detect_changes(self, before: Dict[str, Any], after: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect changes in JavaScript code."""
        events = []
        
        # Function changes
        before_funcs = set(before['functions'].keys())
        after_funcs = set(after['functions'].keys())
        
        # Added functions
        for func_id in after_funcs - before_funcs:
            func_info = after['functions'][func_id]
            events.append({
                'event_type': 'node_added',
                'node_id': func_id,
                'location': 'js_file',
                'details': f'JavaScript function {func_info["name"]} added'
            })
        
        # Removed functions
        for func_id in before_funcs - after_funcs:
            func_info = before['functions'][func_id]
            events.append({
                'event_type': 'node_removed',
                'node_id': func_id,
                'location': 'js_file',
                'details': f'JavaScript function {func_info["name"]} removed'
            })
        
        # Modified functions (check signature/parameters)
        for func_id in before_funcs & after_funcs:
            before_func = before['functions'][func_id]
            after_func = after['functions'][func_id]
            
            # Compare parameters if available
            before_params = before_func.get('params', [])
            after_params = after_func.get('params', [])
            if before_params != after_params:
                events.append({
                    'event_type': 'js_function_signature_changed',
                    'node_id': func_id,
                    'location': 'js_file',
                    'details': f'Function {before_func["name"]} signature changed. Before: {before_params}, After: {after_params}'
                })
            
            # Compare function type (e.g., function declaration vs arrow function)
            before_type = before_func.get('type', 'function')
            after_type = after_func.get('type', 'function')
            if before_type != after_type:
                events.append({
                    'event_type': 'js_function_type_changed',
                    'node_id': func_id,
                    'location': 'js_file',
                    'details': f'Function {before_func["name"]} type changed from {before_type} to {after_type}'
                })
        
        # Class changes
        before_classes = set(before['classes'].keys())
        after_classes = set(after['classes'].keys())
        
        for class_id in after_classes - before_classes:
            class_info = after['classes'][class_id]
            events.append({
                'event_type': 'node_added',
                'node_id': class_id,
                'location': 'js_file',
                'details': f'JavaScript class {class_info["name"]} added'
            })
        
        for class_id in before_classes - after_classes:
            class_info = before['classes'][class_id]
            events.append({
                'event_type': 'node_removed',
                'node_id': class_id,
                'location': 'js_file',
                'details': f'JavaScript class {class_info["name"]} removed'
            })
        
        # Modified classes (check inheritance)
        for class_id in before_classes & after_classes:
            before_class = before['classes'][class_id]
            after_class = after['classes'][class_id]
            
            # Compare inheritance
            before_extends = before_class.get('superclass') or before_class.get('extends')
            after_extends = after_class.get('superclass') or after_class.get('extends')
            if before_extends != after_extends:
                events.append({
                    'event_type': 'js_inheritance_changed',
                    'node_id': class_id,
                    'location': 'js_file',
                    'details': f'Class {before_class["name"]} inheritance changed from {before_extends} to {after_extends}'
                })
            
            # Compare methods if available
            before_methods = set(before_class.get('methods', []))
            after_methods = set(after_class.get('methods', []))
            if before_methods != after_methods:
                added_methods = after_methods - before_methods
                removed_methods = before_methods - after_methods
                if added_methods:
                    events.append({
                        'event_type': 'js_class_method_added',
                        'node_id': class_id,
                        'location': 'js_file',
                        'details': f'Class {before_class["name"]} added methods: {", ".join(added_methods)}'
                    })
                if removed_methods:
                    events.append({
                        'event_type': 'js_class_method_removed',
                        'node_id': class_id,
                        'location': 'js_file',
                        'details': f'Class {before_class["name"]} removed methods: {", ".join(removed_methods)}'
                    })
        
        # Variable changes
        before_vars = before.get('variables', set())
        after_vars = after.get('variables', set())
        if before_vars != after_vars:
            added_vars = after_vars - before_vars
            removed_vars = before_vars - after_vars
            if added_vars:
                events.append({
                    'event_type': 'js_variable_added',
                    'node_id': 'global_scope',
                    'location': 'js_file',
                    'details': f'Added variables: {", ".join(sorted(added_vars))}'
                })
            if removed_vars:
                events.append({
                    'event_type': 'js_variable_removed',
                    'node_id': 'global_scope',
                    'location': 'js_file',
                    'details': f'Removed variables: {", ".join(sorted(removed_vars))}'
                })
        
        # Import changes
        before_imports = set(before.get('imports', []))
        after_imports = set(after.get('imports', []))
        if before_imports != after_imports:
            added_imports = after_imports - before_imports
            removed_imports = before_imports - after_imports
            if added_imports:
                events.append({
                    'event_type': 'js_dependency_added',
                    'node_id': 'module',
                    'location': 'js_file',
                    'details': f'Added imports: {", ".join(sorted(added_imports))}'
                })
            if removed_imports:
                events.append({
                    'event_type': 'js_dependency_removed',
                    'node_id': 'module',
                    'location': 'js_file',
                    'details': f'Removed imports: {", ".join(sorted(removed_imports))}'
                })
        
        return events


class PythonAnalyzer(LanguageAnalyzer):
    """Semantic analyzer for Python code using the existing SVCS Python analyzer."""

    def __init__(self):
        """Initialize the Python analyzer and try to import the existing parser."""
        self.parser_available = False
        self.parse_code_func = None
        
        # Try to import the existing Python parser from .svcs directory
        try:
            # Look for .svcs directory in current working directory or project root
            possible_paths = [
                Path.cwd() / ".svcs",
                Path.cwd().parent / ".svcs",
                Path(__file__).parent / ".svcs"
            ]
            
            for svcs_path in possible_paths:
                if svcs_path.exists() and (svcs_path / "parser.py").exists():
                    sys.path.insert(0, str(svcs_path))
                    try:
                        from parser import parse_code
                        self.parse_code_func = parse_code
                        self.parser_available = True
                        break
                    except ImportError:
                        continue
                        
        except Exception:
            pass  # Graceful fallback if parser is not available

    def parse_code(self, content: str) -> Dict[str, Any]:
        """Parse Python code and extract semantic elements."""
        if not self.parser_available or not self.parse_code_func:
            # Fallback to basic parsing
            return self._parse_basic(content)
        
        try:
            # Use the existing comprehensive parser
            nodes, deps = self.parse_code_func(content)
            return {
                'nodes': nodes,
                'dependencies': deps,
                'content': content
            }
        except Exception:
            # Fallback on error
            return self._parse_basic(content)

    def _parse_basic(self, content: str) -> Dict[str, Any]:
        """Basic fallback parsing using AST."""
        try:
            import ast
            tree = ast.parse(content)
            
            # Extract basic information
            functions = {}
            classes = {}
            imports = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions[f"func:{node.name}"] = {
                        'name': node.name,
                        'lineno': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'source': ast.get_source_segment(content, node) or ""
                    }
                elif isinstance(node, ast.AsyncFunctionDef):
                    functions[f"func:{node.name}"] = {
                        'name': node.name,
                        'lineno': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'async': True,
                        'source': ast.get_source_segment(content, node) or ""
                    }
                elif isinstance(node, ast.ClassDef):
                    classes[f"class:{node.name}"] = {
                        'name': node.name,
                        'lineno': node.lineno,
                        'bases': [ast.get_source_segment(content, base) or str(base) for base in node.bases],
                        'source': ast.get_source_segment(content, node) or ""
                    }
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.add(alias.name)
                    else:  # ImportFrom
                        if node.module:
                            imports.add(node.module)
            
            return {
                'nodes': {**functions, **classes},
                'dependencies': imports,
                'content': content
            }
            
        except Exception:
            return {
                'nodes': {},
                'dependencies': set(),
                'content': content
            }

    def detect_changes(self, before: Dict[str, Any], after: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect semantic changes between two parsed Python code versions."""
        if not self.parser_available:
            return self._detect_basic_changes(before, after)
        
        # Use the comprehensive change detection logic
        return self._detect_comprehensive_changes(before, after)

    def _detect_basic_changes(self, before: Dict[str, Any], after: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Basic change detection fallback."""
        events = []
        
        before_nodes = before.get('nodes', {})
        after_nodes = after.get('nodes', {})
        before_deps = before.get('dependencies', set())
        after_deps = after.get('dependencies', set())
        
        # Check dependency changes
        added_deps = after_deps - before_deps
        removed_deps = before_deps - after_deps
        
        if added_deps:
            events.append({
                'event_type': 'dependency_added',
                'node_id': 'module',
                'location': 'python_file',
                'details': f'Added dependencies: {", ".join(sorted(added_deps))}'
            })
        
        if removed_deps:
            events.append({
                'event_type': 'dependency_removed',
                'node_id': 'module',
                'location': 'python_file',
                'details': f'Removed dependencies: {", ".join(sorted(removed_deps))}'
            })
        
        # Check node changes
        all_node_ids = set(before_nodes.keys()) | set(after_nodes.keys())
        
        for node_id in all_node_ids:
            if node_id not in before_nodes:
                events.append({
                    'event_type': 'node_added',
                    'node_id': node_id,
                    'location': 'python_file',
                    'details': f'Added {node_id}'
                })
            elif node_id not in after_nodes:
                events.append({
                    'event_type': 'node_removed',
                    'node_id': node_id,
                    'location': 'python_file',
                    'details': f'Removed {node_id}'
                })
            elif before_nodes[node_id].get('source') != after_nodes[node_id].get('source'):
                events.append({
                    'event_type': 'node_logic_changed',
                    'node_id': node_id,
                    'location': 'python_file',
                    'details': f'Modified {node_id}'
                })
        
        return events

    def _detect_comprehensive_changes(self, before: Dict[str, Any], after: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Comprehensive change detection using the existing analyzer logic."""
        events = []
        
        before_nodes = before.get('nodes', {})
        after_nodes = after.get('nodes', {})
        before_deps = before.get('dependencies', set())
        after_deps = after.get('dependencies', set())
        
        # Dependency changes
        added_deps = after_deps - before_deps
        removed_deps = before_deps - after_deps
        
        if added_deps:
            events.append({
                'event_type': 'dependency_added',
                'node_id': 'module',
                'location': 'python_file',
                'details': f'Added: {", ".join(sorted(added_deps))}'
            })
        
        if removed_deps:
            events.append({
                'event_type': 'dependency_removed',
                'node_id': 'module',
                'location': 'python_file',
                'details': f'Removed: {", ".join(sorted(removed_deps))}'
            })
        
        # Node-level changes (simplified version of the comprehensive analyzer)
        all_node_ids = set(before_nodes.keys()) | set(after_nodes.keys())
        
        for node_id in all_node_ids:
            details_before = before_nodes.get(node_id)
            details_after = after_nodes.get(node_id)
            
            if not details_before:
                events.append({
                    'event_type': 'node_added',
                    'node_id': node_id,
                    'location': 'python_file',
                    'details': f'Added {node_id}'
                })
                continue
                
            if not details_after:
                events.append({
                    'event_type': 'node_removed',
                    'node_id': node_id,
                    'location': 'python_file',
                    'details': f'Removed {node_id}'
                })
                continue
                
            if details_before.get("source") == details_after.get("source"):
                continue
            
            # Check for specific types of changes
            modification_events = []
            
            # Signature changes
            sig_before = details_before.get("signature")
            sig_after = details_after.get("signature")
            if sig_before and sig_before != sig_after:
                modification_events.append({
                    "event_type": "node_signature_changed",
                    "details": f"Signature changed from {sig_before} to {sig_after}"
                })
            
            # Decorator changes
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
            
            # Async changes
            async_before = details_before.get("async_features", {})
            async_after = details_after.get("async_features", {})
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
            
            # Add events for this node
            if modification_events:
                for event in modification_events:
                    events.append({
                        'node_id': node_id,
                        'location': 'python_file',
                        **event
                    })
            else:
                events.append({
                    'event_type': 'node_logic_changed',
                    'node_id': node_id,
                    'location': 'python_file',
                    'details': 'The implementation of this node has changed.'
                })
        
        return events


class MultiLanguageAnalyzer:
    """Main multi-language analyzer that delegates to language-specific analyzers."""
    
    def __init__(self):
        self.analyzers = {
            # Python files
            '.py': PythonAnalyzer(),
            '.pyx': PythonAnalyzer(),  # Cython files
            '.pyi': PythonAnalyzer(),  # Python stub files
            # PHP files
            '.php': PHPAnalyzer(),
            '.phtml': PHPAnalyzer(),  # HTML-embedded PHP
            '.php3': PHPAnalyzer(),   # PHP 3.x files
            '.php4': PHPAnalyzer(),   # PHP 4.x files
            '.php5': PHPAnalyzer(),   # PHP 5.x files
            '.phps': PHPAnalyzer(),   # PHP source files
            # JavaScript/TypeScript files
            '.js': JavaScriptAnalyzer(),
            '.ts': JavaScriptAnalyzer(),  # TypeScript uses similar patterns
        }
    
    def get_language(self, filepath: str) -> Optional[str]:
        """Determine language from file extension."""
        for ext in self.analyzers.keys():
            if filepath.endswith(ext):
                return ext
        return None
    
    def analyze_file_changes(self, filepath: str, before_content: str, after_content: str) -> List[Dict[str, Any]]:
        """Analyze changes in a file based on its language."""
        language = self.get_language(filepath)
        
        if not language or language not in self.analyzers:
            return []
        
        analyzer = self.analyzers[language]
        
        # Parse both versions
        before_parsed = analyzer.parse_code(before_content)
        after_parsed = analyzer.parse_code(after_content)
        
        # Detect changes
        events = analyzer.detect_changes(before_parsed, after_parsed)
        
        # Convert SemanticEvent objects to dictionaries and add metadata
        result_events = []
        for event in events:
            if isinstance(event, SemanticEvent):
                # Use the built-in to_dict method
                event_dict = event.to_dict()
                event_dict['location'] = filepath  # Override with actual filepath
                if not event_dict['language'] or event_dict['language'] == 'unknown':
                    event_dict['language'] = language.lstrip('.')
                result_events.append(event_dict)
            else:
                # Handle legacy dictionary format
                event['language'] = language.lstrip('.')
                event['location'] = filepath
                result_events.append(event)
        
        return result_events
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported file extensions."""
        return list(self.analyzers.keys())

# Convenience function for backward compatibility
def analyze_multilang_changes(filepath: str, before_content: str, after_content: str) -> List[Dict[str, Any]]:
    """Analyze changes using the multi-language analyzer."""
    analyzer = MultiLanguageAnalyzer()
    return analyzer.analyze_file_changes(filepath, before_content, after_content)

if __name__ == "__main__":
    # Test the multi-language analyzer
    analyzer = MultiLanguageAnalyzer()
    print(f"Supported languages: {analyzer.get_supported_languages()}")
    
    # Display which parsers are available
    print(f"\nAvailable PHP parsers:")
    print(f"  Tree-sitter (modern PHP 7.4+/8.x): {'✓' if tree_sitter_available else '✗'}")
    print(f"  phply (legacy PHP 5.x-7.3): {'✓' if phply_available else '✗'}")
    
    # Test modern PHP features first (if Tree-sitter is available)
    if tree_sitter_available:
        print("\n--- MODERN PHP 8.x ANALYSIS TEST (Tree-sitter) ---")
        
        php_modern_before = '''<?php
namespace App\\Models;

use App\\Traits\\HasTimestamps;

enum Status: string {
    case Active = 'active';
    case Inactive = 'inactive';
}

readonly class User {
    public function __construct(
        private string $name,
        private int $age,
        private Status $status = Status::Active
    ) {}
    
    public function getName(): string {
        return $this->name;
    }
}
?>'''
        
        php_modern_after = '''<?php
namespace App\\Models;

use App\\Traits\\HasTimestamps;
use App\\Enums\\UserRole;

enum Status: string {
    case Active = 'active';
    case Inactive = 'inactive';
    case Pending = 'pending';  // New case
}

#[Table('users')]
readonly class User {
    public function __construct(
        private string $name,
        private int $age,
        private Status $status = Status::Active,
        private UserRole $role = UserRole::User  // New parameter
    ) {}
    
    public function getName(): ?string {  // Made nullable
        return $this->name;
    }
    
    public function getRole(): UserRole {  // New method
        return $this->role;
    }
}
?>'''
        
        print("Analyzing modern PHP 8.x changes:")
        modern_events = analyzer.analyze_file_changes("test_modern.php", php_modern_before, php_modern_after)
        print(f"Modern PHP events detected: {len(modern_events)}")
        for event in modern_events:
            print(f"  - {event['event_type']}: {event['node_id']} - {event['details']}")
    
    # Test PHP
    print("\n--- ADVANCED PHP ANALYSIS TEST ---")

    php_before_advanced = '''<?php
namespace MyProject\\Utils;

use AnotherProject\\Logger;

/**
 * A utility class.
 */
class Utility {
    private $name;
    const VERSION = "1.0";

    public function __construct($name) {
        $this->name = $name;
    }

    /**
     * Greets the user.
     */
    public function greet() {
        return "Hello, " . $this->name;
    }

    protected static function doSomethingInternal() {
        // internal logic
    }
}

interface Processable {
    public function process($data);
}
?>'''
    
    php_after_advanced = '''<?php
namespace MyProject\\Utils;

// Use statement removed: use AnotherProject\\Logger;
use MyProject\\Helpers\\NewLogger; // Added use

/**
 * An enhanced utility class. (Docstring changed)
 */
class Utility implements Processable { // Implements added
    private $name;
    public $description; // Property added
    const VERSION = "1.1"; // Constant value changed
    const AUTHOR = "Jules"; // New constant added

    // Constructor signature changed
    public function __construct($name, $description = "Default") {
        $this->name = $name;
        $this->description = $description;
    }

    /**
     * Greets the user with a title. (Docstring changed)
     */
    // greet signature changed
    public function greet($title) {
        // Logic changed
        return "Hello, " . $title . " " . $this->name . "!";
    }

    // Method removed: doSomethingInternal

    public function process($data) { // Method from interface
        NewLogger::log("Processing data");
        return true;
    }

    public static function newStaticMethod() {} // New method
}

interface Processable { // Unchanged interface
    public function process($data);
}

trait HelperTrait {
    public function help() { return "I am helping!"; }
}
?>'''
    
    print("\nAnalyzing advanced PHP changes (test_advanced.php):")
    advanced_events = analyzer.analyze_file_changes("test_advanced.php", php_before_advanced, php_after_advanced)

    print(f"Advanced PHP events detected: {len(advanced_events)}")
    for event in advanced_events[:10]:  # Show first 10 events
        print(f"  - {event['event_type']}: {event['node_id']} - {event['details']}")
    if len(advanced_events) > 10:
        print(f"  ... and {len(advanced_events) - 10} more events")

    print("\n--- BASIC PHP ANALYSIS TEST (Fallback if phply not found) ---")
    # This test will use the regex fallback if phply is not available
    php_before_basic = '''<?php
function simple_hello() { echo "Hi"; }
class OldClass {}
?>'''
    php_after_basic = '''<?php
function simple_hello_updated() { echo "Hi there"; } // Renamed
class NewClass {} // Renamed
function simple_goodbye() { echo "Bye"; } // Added
?>'''
    basic_events = analyzer.analyze_file_changes("test_basic_fallback.php", php_before_basic, php_after_basic)
    print(f"Basic PHP events detected: {len(basic_events)}")
    for event in basic_events:
        print(f"  - {event['event_type']}: {event['node_id']} - {event['details']}")
    
    # Show which parser was actually used
    if tree_sitter_available:
        print("(Parsed using Tree-sitter - modern parser)")
    elif phply_available:
        print("(Parsed using phply - legacy parser)")
    else:
        print("(Parsed using regex fallback - basic parsing)")

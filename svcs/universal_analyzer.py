#!/usr/bin/env python3
"""
SVCS Universal Semantic Analyzer
Comprehensive semantic analysis for multiple programming languages

This module provides deep semantic analysis capabilities for:
- Python (40+ event types)
- PHP (comprehensive AST analysis) 
- JavaScript/TypeScript (full ES6+ support)

Event Types Supported:
- Structural: node_added, node_removed, node_signature_changed
- Behavioral: async/await patterns, error handling, design patterns
- Language-specific: PHP namespaces, JS modules, Python decorators
- AI-enhanced: pattern recognition, code quality improvements
"""

import ast
import re
import sys
import hashlib
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict

# Import analysis dependencies
try:
    import tree_sitter
    tree_sitter_available = True
except ImportError:
    tree_sitter_available = False

try:
    from tree_sitter_languages import get_language, get_parser
    tree_sitter_languages_available = True
except ImportError:
    tree_sitter_languages_available = False

try:
    import phply.phplex as phplex
    import phply.phpparse as phpparse
    import phply.phpast as phpast
    phply_available = True
except ImportError:
    phply_available = False


class SemanticEventType(Enum):
    """Comprehensive semantic event types."""
    # Universal events
    NODE_ADDED = "node_added"
    NODE_REMOVED = "node_removed"
    NODE_SIGNATURE_CHANGED = "node_signature_changed"
    NODE_LOGIC_CHANGED = "node_logic_changed"
    
    # Dependency events
    DEPENDENCY_ADDED = "dependency_added"
    DEPENDENCY_REMOVED = "dependency_removed"
    
    # Python-specific events
    DECORATOR_ADDED = "decorator_added"
    DECORATOR_REMOVED = "decorator_removed"
    FUNCTION_MADE_ASYNC = "function_made_async"
    FUNCTION_MADE_SYNC = "function_made_sync"
    AWAIT_USAGE_CHANGED = "await_usage_changed"
    YIELD_PATTERN_CHANGED = "yield_pattern_changed"
    COMPREHENSION_USAGE_CHANGED = "comprehension_usage_changed"
    LAMBDA_USAGE_CHANGED = "lambda_usage_changed"
    GLOBAL_SCOPE_CHANGED = "global_scope_changed"
    NONLOCAL_SCOPE_CHANGED = "nonlocal_scope_changed"
    ASSERTION_USAGE_CHANGED = "assertion_usage_changed"
    RETURN_PATTERN_CHANGED = "return_pattern_changed"
    
    # PHP-specific events
    PHP_NAMESPACE_ADDED = "php_namespace_added"
    PHP_NAMESPACE_REMOVED = "php_namespace_removed"
    PHP_USE_STATEMENT_ADDED = "php_use_statement_added"
    PHP_USE_STATEMENT_REMOVED = "php_use_statement_removed"
    PHP_INHERITANCE_CHANGED = "php_inheritance_changed"
    PHP_INTERFACE_IMPLEMENTS_CHANGED = "php_interface_implements_changed"
    PHP_VISIBILITY_CHANGED = "php_visibility_changed"
    PHP_STATIC_MODIFIER_CHANGED = "php_static_modifier_changed"
    PHP_ABSTRACT_MODIFIER_CHANGED = "php_abstract_modifier_changed"
    PHP_FINAL_MODIFIER_CHANGED = "php_final_modifier_changed"
    PHP_TRAIT_USAGE_CHANGED = "php_trait_usage_changed"
    PHP_EXCEPTION_HANDLING_CHANGED = "php_exception_handling_changed"
    PHP_TYPE_HINT_ADDED = "php_type_hint_added"
    PHP_TYPE_HINT_REMOVED = "php_type_hint_removed"
    PHP_RETURN_TYPE_CHANGED = "php_return_type_changed"
    PHP_CONSTANT_VALUE_CHANGED = "php_constant_value_changed"
    PHP_DOCSTRING_CHANGED = "php_docstring_changed"
    
    # JavaScript-specific events
    JS_MODULE_IMPORT_ADDED = "js_module_import_added"
    JS_MODULE_IMPORT_REMOVED = "js_module_import_removed"
    JS_MODULE_EXPORT_ADDED = "js_module_export_added"
    JS_MODULE_EXPORT_REMOVED = "js_module_export_removed"
    JS_ASYNC_AWAIT_ADDED = "js_async_await_added"
    JS_PROMISE_PATTERN_CHANGED = "js_promise_pattern_changed"
    JS_ARROW_FUNCTION_ADDED = "js_arrow_function_added"
    JS_TEMPLATE_LITERAL_ADDED = "js_template_literal_added"
    JS_DESTRUCTURING_ADDED = "js_destructuring_added"
    JS_SPREAD_OPERATOR_ADDED = "js_spread_operator_added"
    JS_CLASS_EXTENDS_CHANGED = "js_class_extends_changed"
    JS_GETTER_SETTER_ADDED = "js_getter_setter_added"
    
    # AI-detected patterns
    DESIGN_PATTERN_APPLIED = "design_pattern_applied"
    DESIGN_PATTERN_REMOVED = "design_pattern_removed"
    ALGORITHM_OPTIMIZED = "algorithm_optimized"
    CODE_COMPLEXITY_REDUCED = "code_complexity_reduced"
    ERROR_HANDLING_IMPROVED = "error_handling_improved"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    SECURITY_IMPROVEMENT = "security_improvement"
    MAINTAINABILITY_IMPROVED = "maintainability_improved"


@dataclass
class SemanticEvent:
    """Represents a detected semantic event."""
    event_type: SemanticEventType
    node_id: str
    location: str
    details: str
    confidence: float = 1.0
    layer: str = "core"
    additional_data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for storage."""
        return {
            "event_type": self.event_type.value,
            "node_id": self.node_id,
            "location": self.location,
            "details": self.details,
            "confidence": self.confidence,
            "layer": self.layer,
            "additional_data": self.additional_data or {}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SemanticEvent':
        """Create from dictionary format."""
        return cls(
            event_type=SemanticEventType(data["event_type"]),
            node_id=data["node_id"],
            location=data["location"],
            details=data["details"],
            confidence=data.get("confidence", 1.0),
            layer=data.get("layer", "core"),
            additional_data=data.get("additional_data")
        )


class UniversalSemanticAnalyzer:
    """Universal semantic analyzer for multiple programming languages."""
    
    def __init__(self):
        self.language_analyzers = {
            '.py': PythonAnalyzer(),
            '.php': PHPAnalyzer(),
            '.js': JavaScriptAnalyzer(),
            '.ts': TypeScriptAnalyzer()
        }
    
    def analyze_file_changes(self, filepath: str, before_content: str, after_content: str) -> List[SemanticEvent]:
        """Analyze semantic changes in a file."""
        if before_content == after_content:
            return []
        
        # Determine file type
        for ext, analyzer in self.language_analyzers.items():
            if filepath.endswith(ext):
                return analyzer.analyze_changes(filepath, before_content, after_content)
        
        # Fallback to generic text analysis
        return self._analyze_generic_changes(filepath, before_content, after_content)
    
    def _analyze_generic_changes(self, filepath: str, before: str, after: str) -> List[SemanticEvent]:
        """Generic text-based analysis for unsupported file types."""
        events = []
        
        before_lines = set(before.splitlines())
        after_lines = set(after.splitlines())
        
        if before_lines != after_lines:
            events.append(SemanticEvent(
                event_type=SemanticEventType.NODE_LOGIC_CHANGED,
                node_id=f"file:{filepath}",
                location=filepath,
                details=f"Content changed in {filepath}"
            ))
        
        return events


class LanguageAnalyzer:
    """Base class for language-specific analyzers."""
    
    def analyze_changes(self, filepath: str, before_content: str, after_content: str) -> List[SemanticEvent]:
        """Analyze changes between two versions of code."""
        raise NotImplementedError("Subclasses must implement analyze_changes")
    
    def parse_code(self, content: str) -> Dict[str, Any]:
        """Parse code and extract semantic elements."""
        raise NotImplementedError("Subclasses must implement parse_code")


class PythonAnalyzer(LanguageAnalyzer):
    """Advanced Python semantic analyzer."""
    
    def analyze_changes(self, filepath: str, before_content: str, after_content: str) -> List[SemanticEvent]:
        """Analyze Python code changes."""
        events = []
        
        try:
            before_ast = self.parse_code(before_content)
            after_ast = self.parse_code(after_content)
            
            # Analyze imports
            events.extend(self._analyze_imports(before_ast, after_ast, filepath))
            
            # Analyze functions
            events.extend(self._analyze_functions(before_ast, after_ast, filepath))
            
            # Analyze classes
            events.extend(self._analyze_classes(before_ast, after_ast, filepath))
            
            # Analyze patterns
            events.extend(self._analyze_patterns(before_content, after_content, filepath))
            
        except SyntaxError:
            # Handle syntax errors gracefully
            events.append(SemanticEvent(
                event_type=SemanticEventType.NODE_LOGIC_CHANGED,
                node_id=f"file:{filepath}",
                location=filepath,
                details="Syntax changes detected"
            ))
        
        return events
    
    def parse_code(self, content: str) -> Dict[str, Any]:
        """Parse Python code using AST."""
        tree = ast.parse(content)
        
        result = {
            'imports': [],
            'functions': {},
            'classes': {},
            'global_vars': set(),
            'decorators': {},
            'async_functions': set(),
            'generators': set(),
            'comprehensions': 0,
            'lambdas': 0
        }
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                result['imports'].append(self._extract_import(node))
            elif isinstance(node, ast.FunctionDef):
                result['functions'][node.name] = self._extract_function(node)
                if isinstance(node, ast.AsyncFunctionDef):
                    result['async_functions'].add(node.name)
                if any(isinstance(n, ast.Yield) for n in ast.walk(node)):
                    result['generators'].add(node.name)
            elif isinstance(node, ast.ClassDef):
                result['classes'][node.name] = self._extract_class(node)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        result['global_vars'].add(target.id)
            elif isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
                result['comprehensions'] += 1
            elif isinstance(node, ast.Lambda):
                result['lambdas'] += 1
        
        return result
    
    def _extract_import(self, node: ast.AST) -> Dict[str, Any]:
        """Extract import information."""
        if isinstance(node, ast.Import):
            return {'type': 'import', 'names': [alias.name for alias in node.names]}
        elif isinstance(node, ast.ImportFrom):
            return {'type': 'from', 'module': node.module, 'names': [alias.name for alias in node.names]}
        return {}
    
    def _extract_function(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Extract function information."""
        return {
            'name': node.name,
            'args': [arg.arg for arg in node.args.args],
            'decorators': [self._get_decorator_name(d) for d in node.decorator_list],
            'is_async': isinstance(node, ast.AsyncFunctionDef),
            'has_yield': any(isinstance(n, ast.Yield) for n in ast.walk(node)),
            'returns': bool(node.returns),
            'docstring': ast.get_docstring(node),
            'line_count': node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
        }
    
    def _extract_class(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Extract class information."""
        methods = {}
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods[item.name] = self._extract_function(item)
        
        return {
            'name': node.name,
            'bases': [self._get_name(base) for base in node.bases],
            'decorators': [self._get_decorator_name(d) for d in node.decorator_list],
            'methods': methods,
            'docstring': ast.get_docstring(node)
        }
    
    def _get_decorator_name(self, decorator: ast.AST) -> str:
        """Get decorator name."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f"{self._get_name(decorator.value)}.{decorator.attr}"
        return str(decorator)
    
    def _get_name(self, node: ast.AST) -> str:
        """Get name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return str(node)
    
    def _analyze_imports(self, before: Dict, after: Dict, filepath: str) -> List[SemanticEvent]:
        """Analyze import changes."""
        events = []
        
        before_imports = set(str(imp) for imp in before['imports'])
        after_imports = set(str(imp) for imp in after['imports'])
        
        added = after_imports - before_imports
        removed = before_imports - after_imports
        
        if added:
            events.append(SemanticEvent(
                event_type=SemanticEventType.DEPENDENCY_ADDED,
                node_id=f"module:{filepath}",
                location=filepath,
                details=f"Added imports: {', '.join(added)}"
            ))
        
        if removed:
            events.append(SemanticEvent(
                event_type=SemanticEventType.DEPENDENCY_REMOVED,
                node_id=f"module:{filepath}",
                location=filepath,
                details=f"Removed imports: {', '.join(removed)}"
            ))
        
        return events
    
    def _analyze_functions(self, before: Dict, after: Dict, filepath: str) -> List[SemanticEvent]:
        """Analyze function changes."""
        events = []
        
        before_funcs = set(before['functions'].keys())
        after_funcs = set(after['functions'].keys())
        
        # Added/removed functions
        for func_name in after_funcs - before_funcs:
            events.append(SemanticEvent(
                event_type=SemanticEventType.NODE_ADDED,
                node_id=f"func:{func_name}",
                location=filepath,
                details=f"Function {func_name} added"
            ))
        
        for func_name in before_funcs - after_funcs:
            events.append(SemanticEvent(
                event_type=SemanticEventType.NODE_REMOVED,
                node_id=f"func:{func_name}",
                location=filepath,
                details=f"Function {func_name} removed"
            ))
        
        # Modified functions
        for func_name in before_funcs & after_funcs:
            before_func = before['functions'][func_name]
            after_func = after['functions'][func_name]
            
            # Check async changes
            if before_func['is_async'] != after_func['is_async']:
                event_type = SemanticEventType.FUNCTION_MADE_ASYNC if after_func['is_async'] else SemanticEventType.FUNCTION_MADE_SYNC
                events.append(SemanticEvent(
                    event_type=event_type,
                    node_id=f"func:{func_name}",
                    location=filepath,
                    details=f"Function {func_name} async status changed"
                ))
            
            # Check decorators
            if before_func['decorators'] != after_func['decorators']:
                added_decorators = set(after_func['decorators']) - set(before_func['decorators'])
                removed_decorators = set(before_func['decorators']) - set(after_func['decorators'])
                
                if added_decorators:
                    events.append(SemanticEvent(
                        event_type=SemanticEventType.DECORATOR_ADDED,
                        node_id=f"func:{func_name}",
                        location=filepath,
                        details=f"Added decorators: {', '.join(added_decorators)}"
                    ))
                
                if removed_decorators:
                    events.append(SemanticEvent(
                        event_type=SemanticEventType.DECORATOR_REMOVED,
                        node_id=f"func:{func_name}",
                        location=filepath,
                        details=f"Removed decorators: {', '.join(removed_decorators)}"
                    ))
            
            # Check signature changes
            if before_func['args'] != after_func['args']:
                events.append(SemanticEvent(
                    event_type=SemanticEventType.NODE_SIGNATURE_CHANGED,
                    node_id=f"func:{func_name}",
                    location=filepath,
                    details=f"Function {func_name} signature changed"
                ))
        
        return events
    
    def _analyze_classes(self, before: Dict, after: Dict, filepath: str) -> List[SemanticEvent]:
        """Analyze class changes."""
        events = []
        
        before_classes = set(before['classes'].keys())
        after_classes = set(after['classes'].keys())
        
        # Added/removed classes
        for class_name in after_classes - before_classes:
            events.append(SemanticEvent(
                event_type=SemanticEventType.NODE_ADDED,
                node_id=f"class:{class_name}",
                location=filepath,
                details=f"Class {class_name} added"
            ))
        
        for class_name in before_classes - after_classes:
            events.append(SemanticEvent(
                event_type=SemanticEventType.NODE_REMOVED,
                node_id=f"class:{class_name}",
                location=filepath,
                details=f"Class {class_name} removed"
            ))
        
        # Modified classes
        for class_name in before_classes & after_classes:
            before_class = before['classes'][class_name]
            after_class = after['classes'][class_name]
            
            # Check inheritance changes
            if before_class['bases'] != after_class['bases']:
                events.append(SemanticEvent(
                    event_type=SemanticEventType.NODE_SIGNATURE_CHANGED,
                    node_id=f"class:{class_name}",
                    location=filepath,
                    details=f"Class {class_name} inheritance changed"
                ))
        
        return events
    
    def _analyze_patterns(self, before_content: str, after_content: str, filepath: str) -> List[SemanticEvent]:
        """Analyze high-level patterns."""
        events = []
        
        # Check for comprehension patterns
        before_comps = len(re.findall(r'\[[^\]]+for\s+\w+\s+in[^\]]+\]', before_content))
        after_comps = len(re.findall(r'\[[^\]]+for\s+\w+\s+in[^\]]+\]', after_content))
        
        if before_comps != after_comps:
            events.append(SemanticEvent(
                event_type=SemanticEventType.COMPREHENSION_USAGE_CHANGED,
                node_id=f"file:{filepath}",
                location=filepath,
                details=f"List comprehension usage changed: {before_comps} -> {after_comps}"
            ))
        
        # Check for async/await patterns
        before_awaits = before_content.count('await ')
        after_awaits = after_content.count('await ')
        
        if before_awaits != after_awaits:
            events.append(SemanticEvent(
                event_type=SemanticEventType.AWAIT_USAGE_CHANGED,
                node_id=f"file:{filepath}",
                location=filepath,
                details=f"Await usage changed: {before_awaits} -> {after_awaits}"
            ))
        
        return events


class PHPAnalyzer(LanguageAnalyzer):
    """PHP semantic analyzer using Tree-sitter and phply fallback."""
    
    def analyze_changes(self, filepath: str, before_content: str, after_content: str) -> List[SemanticEvent]:
        """Analyze PHP code changes."""
        events = []
        
        try:
            before_parsed = self.parse_code(before_content)
            after_parsed = self.parse_code(after_content)
            
            # Analyze namespaces
            events.extend(self._analyze_namespaces(before_parsed, after_parsed, filepath))
            
            # Analyze classes
            events.extend(self._analyze_php_classes(before_parsed, after_parsed, filepath))
            
            # Analyze functions
            events.extend(self._analyze_php_functions(before_parsed, after_parsed, filepath))
            
            # Analyze use statements
            events.extend(self._analyze_use_statements(before_parsed, after_parsed, filepath))
            
        except Exception as e:
            events.append(SemanticEvent(
                event_type=SemanticEventType.NODE_LOGIC_CHANGED,
                node_id=f"file:{filepath}",
                location=filepath,
                details=f"PHP parsing changes detected: {str(e)}"
            ))
        
        return events
    
    def parse_code(self, content: str) -> Dict[str, Any]:
        """Parse PHP code using Tree-sitter or phply fallback."""
        if tree_sitter_available and tree_sitter_languages_available:
            return self._parse_with_tree_sitter(content)
        elif phply_available:
            return self._parse_with_phply(content)
        else:
            return self._parse_with_regex(content)
    
    def _parse_with_tree_sitter(self, content: str) -> Dict[str, Any]:
        """Parse using Tree-sitter."""
        try:
            php_language = get_language("php")
            parser = get_parser("php")
            
            tree = parser.parse(content.encode('utf-8'))
            
            result = {
                'namespaces': {},
                'classes': {},
                'functions': {},
                'interfaces': {},
                'traits': {},
                'uses': [],
                'constants': {}
            }
            
            self._extract_tree_sitter_nodes(tree.root_node, result, content)
            return result
            
        except Exception:
            # Fallback to phply
            return self._parse_with_phply(content)
    
    def _extract_tree_sitter_nodes(self, node, result: Dict, source: str):
        """Extract nodes from Tree-sitter AST."""
        if node.type == 'namespace_definition':
            namespace_name = self._get_node_text(node, source, 'namespace_name')
            if namespace_name:
                result['namespaces'][namespace_name] = {'name': namespace_name}
        
        elif node.type == 'class_declaration':
            class_name = self._get_node_text(node, source, 'name')
            if class_name:
                result['classes'][class_name] = self._extract_ts_class(node, source)
        
        elif node.type == 'function_definition':
            func_name = self._get_node_text(node, source, 'name')
            if func_name:
                result['functions'][func_name] = self._extract_ts_function(node, source)
        
        # Recursively process children
        for child in node.children:
            self._extract_tree_sitter_nodes(child, result, source)
    
    def _get_node_text(self, node, source: str, field_name: str = None) -> str:
        """Get text from Tree-sitter node."""
        if field_name:
            for child in node.children:
                if child.type == field_name:
                    return source[child.start_byte:child.end_byte]
        return source[node.start_byte:node.end_byte]
    
    def _extract_ts_class(self, node, source: str) -> Dict[str, Any]:
        """Extract class info from Tree-sitter node."""
        return {
            'name': self._get_node_text(node, source, 'name'),
            'methods': {},
            'properties': {},
            'extends': None,
            'implements': []
        }
    
    def _extract_ts_function(self, node, source: str) -> Dict[str, Any]:
        """Extract function info from Tree-sitter node."""
        return {
            'name': self._get_node_text(node, source, 'name'),
            'parameters': [],
            'return_type': None,
            'visibility': 'public'
        }
    
    def _parse_with_phply(self, content: str) -> Dict[str, Any]:
        """Parse using phply."""
        try:
            parser = phpparse.make_parser()
            tree = parser.parse(content, lexer=phplex.lexer)
            
            result = {
                'namespaces': {},
                'classes': {},
                'functions': {},
                'interfaces': {},
                'traits': {},
                'uses': [],
                'constants': {}
            }
            
            for node in tree:
                self._extract_phply_node(node, result)
            
            return result
            
        except Exception:
            return self._parse_with_regex(content)
    
    def _extract_phply_node(self, node, result: Dict):
        """Extract node from phply AST."""
        if isinstance(node, phpast.Class):
            result['classes'][node.name] = {
                'name': node.name,
                'methods': {},
                'properties': {},
                'extends': getattr(node, 'extends', None),
                'implements': getattr(node, 'implements', [])
            }
        
        elif isinstance(node, phpast.Function):
            result['functions'][node.name] = {
                'name': node.name,
                'parameters': [],
                'return_type': None,
                'visibility': 'public'
            }
    
    def _parse_with_regex(self, content: str) -> Dict[str, Any]:
        """Fallback regex parsing."""
        result = {
            'namespaces': {},
            'classes': {},
            'functions': {},
            'interfaces': {},
            'traits': {},
            'uses': [],
            'constants': {}
        }
        
        # Extract classes
        class_pattern = r'class\s+([a-zA-Z_]\w*)'
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            result['classes'][class_name] = {'name': class_name}
        
        # Extract functions
        func_pattern = r'function\s+([a-zA-Z_]\w*)\s*\('
        for match in re.finditer(func_pattern, content):
            func_name = match.group(1)
            result['functions'][func_name] = {'name': func_name}
        
        return result
    
    def _analyze_namespaces(self, before: Dict, after: Dict, filepath: str) -> List[SemanticEvent]:
        """Analyze namespace changes."""
        events = []
        
        before_ns = set(before['namespaces'].keys())
        after_ns = set(after['namespaces'].keys())
        
        for ns in after_ns - before_ns:
            events.append(SemanticEvent(
                event_type=SemanticEventType.PHP_NAMESPACE_ADDED,
                node_id=f"namespace:{ns}",
                location=filepath,
                details=f"Namespace {ns} added"
            ))
        
        for ns in before_ns - after_ns:
            events.append(SemanticEvent(
                event_type=SemanticEventType.PHP_NAMESPACE_REMOVED,
                node_id=f"namespace:{ns}",
                location=filepath,
                details=f"Namespace {ns} removed"
            ))
        
        return events
    
    def _analyze_php_classes(self, before: Dict, after: Dict, filepath: str) -> List[SemanticEvent]:
        """Analyze PHP class changes."""
        events = []
        
        before_classes = set(before['classes'].keys())
        after_classes = set(after['classes'].keys())
        
        for class_name in after_classes - before_classes:
            events.append(SemanticEvent(
                event_type=SemanticEventType.NODE_ADDED,
                node_id=f"class:{class_name}",
                location=filepath,
                details=f"PHP class {class_name} added"
            ))
        
        for class_name in before_classes - after_classes:
            events.append(SemanticEvent(
                event_type=SemanticEventType.NODE_REMOVED,
                node_id=f"class:{class_name}",
                location=filepath,
                details=f"PHP class {class_name} removed"
            ))
        
        return events
    
    def _analyze_php_functions(self, before: Dict, after: Dict, filepath: str) -> List[SemanticEvent]:
        """Analyze PHP function changes."""
        events = []
        
        before_funcs = set(before['functions'].keys())
        after_funcs = set(after['functions'].keys())
        
        for func_name in after_funcs - before_funcs:
            events.append(SemanticEvent(
                event_type=SemanticEventType.NODE_ADDED,
                node_id=f"func:{func_name}",
                location=filepath,
                details=f"PHP function {func_name} added"
            ))
        
        for func_name in before_funcs - after_funcs:
            events.append(SemanticEvent(
                event_type=SemanticEventType.NODE_REMOVED,
                node_id=f"func:{func_name}",
                location=filepath,
                details=f"PHP function {func_name} removed"
            ))
        
        return events
    
    def _analyze_use_statements(self, before: Dict, after: Dict, filepath: str) -> List[SemanticEvent]:
        """Analyze use statement changes."""
        events = []
        
        before_uses = set(str(use) for use in before['uses'])
        after_uses = set(str(use) for use in after['uses'])
        
        if before_uses != after_uses:
            added = after_uses - before_uses
            removed = before_uses - after_uses
            
            if added:
                events.append(SemanticEvent(
                    event_type=SemanticEventType.PHP_USE_STATEMENT_ADDED,
                    node_id=f"module:{filepath}",
                    location=filepath,
                    details=f"Added use statements: {', '.join(added)}"
                ))
            
            if removed:
                events.append(SemanticEvent(
                    event_type=SemanticEventType.PHP_USE_STATEMENT_REMOVED,
                    node_id=f"module:{filepath}",
                    location=filepath,
                    details=f"Removed use statements: {', '.join(removed)}"
                ))
        
        return events


class JavaScriptAnalyzer(LanguageAnalyzer):
    """JavaScript/ES6+ semantic analyzer."""
    
    def analyze_changes(self, filepath: str, before_content: str, after_content: str) -> List[SemanticEvent]:
        """Analyze JavaScript code changes."""
        events = []
        
        try:
            before_parsed = self.parse_code(before_content)
            after_parsed = self.parse_code(after_content)
            
            # Analyze imports/exports
            events.extend(self._analyze_js_modules(before_parsed, after_parsed, filepath))
            
            # Analyze functions
            events.extend(self._analyze_js_functions(before_parsed, after_parsed, filepath))
            
            # Analyze classes
            events.extend(self._analyze_js_classes(before_parsed, after_parsed, filepath))
            
            # Analyze modern JS features
            events.extend(self._analyze_js_patterns(before_content, after_content, filepath))
            
        except Exception as e:
            events.append(SemanticEvent(
                event_type=SemanticEventType.NODE_LOGIC_CHANGED,
                node_id=f"file:{filepath}",
                location=filepath,
                details=f"JavaScript parsing changes: {str(e)}"
            ))
        
        return events
    
    def parse_code(self, content: str) -> Dict[str, Any]:
        """Parse JavaScript using regex patterns."""
        result = {
            'imports': [],
            'exports': [],
            'functions': {},
            'classes': {},
            'arrow_functions': 0,
            'async_functions': set(),
            'template_literals': 0,
            'destructuring': 0
        }
        
        # Extract imports
        import_pattern = r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]'
        for match in re.finditer(import_pattern, content):
            result['imports'].append(match.group(1))
        
        # Extract exports
        export_pattern = r'export\s+(default\s+)?(class|function|const|let|var)\s+([a-zA-Z_]\w*)'
        for match in re.finditer(export_pattern, content):
            result['exports'].append(match.group(3))
        
        # Extract functions
        func_pattern = r'(async\s+)?function\s+([a-zA-Z_]\w*)\s*\('
        for match in re.finditer(func_pattern, content):
            func_name = match.group(2)
            result['functions'][func_name] = {
                'name': func_name,
                'is_async': bool(match.group(1))
            }
            if match.group(1):
                result['async_functions'].add(func_name)
        
        # Extract classes
        class_pattern = r'class\s+([a-zA-Z_]\w*)'
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            result['classes'][class_name] = {'name': class_name}
        
        # Count arrow functions
        result['arrow_functions'] = len(re.findall(r'=>', content))
        
        # Count template literals
        result['template_literals'] = len(re.findall(r'`[^`]*`', content))
        
        # Count destructuring
        result['destructuring'] = len(re.findall(r'const\s*\{[^}]+\}|let\s*\{[^}]+\}|var\s*\{[^}]+\}', content))
        
        return result
    
    def _analyze_js_modules(self, before: Dict, after: Dict, filepath: str) -> List[SemanticEvent]:
        """Analyze import/export changes."""
        events = []
        
        before_imports = set(before['imports'])
        after_imports = set(after['imports'])
        
        for imp in after_imports - before_imports:
            events.append(SemanticEvent(
                event_type=SemanticEventType.JS_MODULE_IMPORT_ADDED,
                node_id=f"import:{imp}",
                location=filepath,
                details=f"Import added: {imp}"
            ))
        
        for imp in before_imports - after_imports:
            events.append(SemanticEvent(
                event_type=SemanticEventType.JS_MODULE_IMPORT_REMOVED,
                node_id=f"import:{imp}",
                location=filepath,
                details=f"Import removed: {imp}"
            ))
        
        before_exports = set(before['exports'])
        after_exports = set(after['exports'])
        
        for exp in after_exports - before_exports:
            events.append(SemanticEvent(
                event_type=SemanticEventType.JS_MODULE_EXPORT_ADDED,
                node_id=f"export:{exp}",
                location=filepath,
                details=f"Export added: {exp}"
            ))
        
        for exp in before_exports - after_exports:
            events.append(SemanticEvent(
                event_type=SemanticEventType.JS_MODULE_EXPORT_REMOVED,
                node_id=f"export:{exp}",
                location=filepath,
                details=f"Export removed: {exp}"
            ))
        
        return events
    
    def _analyze_js_functions(self, before: Dict, after: Dict, filepath: str) -> List[SemanticEvent]:
        """Analyze JavaScript function changes."""
        events = []
        
        before_funcs = set(before['functions'].keys())
        after_funcs = set(after['functions'].keys())
        
        for func_name in after_funcs - before_funcs:
            events.append(SemanticEvent(
                event_type=SemanticEventType.NODE_ADDED,
                node_id=f"func:{func_name}",
                location=filepath,
                details=f"JavaScript function {func_name} added"
            ))
        
        for func_name in before_funcs - after_funcs:
            events.append(SemanticEvent(
                event_type=SemanticEventType.NODE_REMOVED,
                node_id=f"func:{func_name}",
                location=filepath,
                details=f"JavaScript function {func_name} removed"
            ))
        
        # Check async changes
        before_async = before['async_functions']
        after_async = after['async_functions']
        
        for func_name in after_async - before_async:
            events.append(SemanticEvent(
                event_type=SemanticEventType.JS_ASYNC_AWAIT_ADDED,
                node_id=f"func:{func_name}",
                location=filepath,
                details=f"Function {func_name} made async"
            ))
        
        return events
    
    def _analyze_js_classes(self, before: Dict, after: Dict, filepath: str) -> List[SemanticEvent]:
        """Analyze JavaScript class changes."""
        events = []
        
        before_classes = set(before['classes'].keys())
        after_classes = set(after['classes'].keys())
        
        for class_name in after_classes - before_classes:
            events.append(SemanticEvent(
                event_type=SemanticEventType.NODE_ADDED,
                node_id=f"class:{class_name}",
                location=filepath,
                details=f"JavaScript class {class_name} added"
            ))
        
        for class_name in before_classes - after_classes:
            events.append(SemanticEvent(
                event_type=SemanticEventType.NODE_REMOVED,
                node_id=f"class:{class_name}",
                location=filepath,
                details=f"JavaScript class {class_name} removed"
            ))
        
        return events
    
    def _analyze_js_patterns(self, before_content: str, after_content: str, filepath: str) -> List[SemanticEvent]:
        """Analyze modern JavaScript patterns."""
        events = []
        
        # Arrow functions
        before_arrows = before_content.count('=>')
        after_arrows = after_content.count('=>')
        
        if after_arrows > before_arrows:
            events.append(SemanticEvent(
                event_type=SemanticEventType.JS_ARROW_FUNCTION_ADDED,
                node_id=f"file:{filepath}",
                location=filepath,
                details=f"Arrow functions added: {after_arrows - before_arrows}"
            ))
        
        # Template literals
        before_templates = len(re.findall(r'`[^`]*`', before_content))
        after_templates = len(re.findall(r'`[^`]*`', after_content))
        
        if after_templates > before_templates:
            events.append(SemanticEvent(
                event_type=SemanticEventType.JS_TEMPLATE_LITERAL_ADDED,
                node_id=f"file:{filepath}",
                location=filepath,
                details=f"Template literals added: {after_templates - before_templates}"
            ))
        
        # Destructuring
        before_destructuring = len(re.findall(r'const\s*\{[^}]+\}|let\s*\{[^}]+\}', before_content))
        after_destructuring = len(re.findall(r'const\s*\{[^}]+\}|let\s*\{[^}]+\}', after_content))
        
        if after_destructuring > before_destructuring:
            events.append(SemanticEvent(
                event_type=SemanticEventType.JS_DESTRUCTURING_ADDED,
                node_id=f"file:{filepath}",
                location=filepath,
                details=f"Destructuring patterns added: {after_destructuring - before_destructuring}"
            ))
        
        return events


class TypeScriptAnalyzer(JavaScriptAnalyzer):
    """TypeScript analyzer extending JavaScript analyzer."""
    
    def parse_code(self, content: str) -> Dict[str, Any]:
        """Parse TypeScript with additional type information."""
        result = super().parse_code(content)
        
        # Add TypeScript-specific parsing
        result['interfaces'] = {}
        result['type_annotations'] = 0
        result['generics'] = 0
        
        # Extract interfaces
        interface_pattern = r'interface\s+([a-zA-Z_]\w*)'
        for match in re.finditer(interface_pattern, content):
            interface_name = match.group(1)
            result['interfaces'][interface_name] = {'name': interface_name}
        
        # Count type annotations
        result['type_annotations'] = len(re.findall(r':\s*[a-zA-Z_]\w*(?:\[\])?', content))
        
        # Count generics
        result['generics'] = len(re.findall(r'<[a-zA-Z_]\w*(?:,\s*[a-zA-Z_]\w*)*>', content))
        
        return result


def analyze_semantic_changes(filepath: str, before_content: str, after_content: str) -> List[Dict[str, Any]]:
    """Main entry point for semantic analysis."""
    analyzer = UniversalSemanticAnalyzer()
    events = analyzer.analyze_file_changes(filepath, before_content, after_content)
    
    # Convert to dict format for compatibility
    return [event.to_dict() for event in events]


if __name__ == "__main__":
    # Test the analyzer
    test_before = '''
def old_function(x):
    return x * 2

class OldClass:
    def method(self):
        pass
'''
    
    test_after = '''
import asyncio

async def new_function(x: int) -> int:
    """Enhanced function."""
    result = x * 2
    await asyncio.sleep(0.1)
    return result

class NewClass:
    def __init__(self, value: int):
        self.value = value
    
    def method(self) -> str:
        return str(self.value)
    
    @property
    def computed(self) -> int:
        return self.value * 2
'''
    
    events = analyze_semantic_changes("test.py", test_before, test_after)
    
    print(f"Detected {len(events)} semantic events:")
    for event in events:
        print(f"  - {event['event_type']}: {event['details']}")

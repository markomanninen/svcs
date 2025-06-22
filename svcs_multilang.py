#!/usr/bin/env python3
"""
SVCS Multi-Language Support Module
Provides semantic analysis for multiple programming languages beyond Python.
"""

import re
import sys # For sys.stderr
# import ast # No longer needed for PHP part, assuming phpparser has its own AST nodes
# Let's assume a hypothetical PHP parsing library
try:
    import phpparser
    from phpparser import ast as php_ast # Assuming similar structure to Python's ast
    # Ensure php_ast is also available if phpparser is.
except ImportError:
    phpparser = None # Fallback or error handling will be needed
    php_ast = None # Initialize php_ast to None if phpparser import fails

from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

class LanguageAnalyzer(ABC):
    """Abstract base class for language-specific analyzers."""
    
    @abstractmethod
    def parse_code(self, content: str) -> Dict[str, Any]:
        """Parse code and extract semantic elements."""
        pass
    
    @abstractmethod
    def detect_changes(self, before: Dict[str, Any], after: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect semantic changes between parsed versions."""
        pass

class PHPAnalyzer(LanguageAnalyzer):
    """Semantic analyzer for PHP code."""

    def _extract_docstring(self, node: 'php_ast.Node') -> Optional[str]: # String literal type hint
        """Helper to extract docstring from a PHP node (hypothetical)."""
        if not php_ast: return None # Guard clause
        if hasattr(node, 'doc_comment') and node.doc_comment:
            return node.doc_comment.text
        return None

    def _parse_parameters(self, params_node: Optional['php_ast.Parameters']) -> list: # String literal type hint
        """Helper to parse function/method parameters (hypothetical)."""
        if not php_ast or not params_node or not hasattr(params_node, 'params'): # Guard clause
            return []

        parsed_params = []
        for param in params_node.params:
            param_info = {'name': param.name.name if hasattr(param.name, 'name') else str(param.name)}
            if hasattr(param, 'type') and param.type:
                param_info['type'] = php_ast.dump(param.type) # Or a more specific type name extraction
            if hasattr(param, 'default') and param.default:
                param_info['default'] = True # Mark that a default exists
            parsed_params.append(param_info)
        return parsed_params

    def _parse_body(self, body_nodes: list) -> dict:
        """Helper to get a summary of the body content (hypothetical)."""
        # This would be a complex part, for now, a simple hash or line count
        # In a real scenario, we'd extract statements, control flow, etc.
        source_lines = []
        for stmt in body_nodes:
            if hasattr(stmt, 'lineno') and hasattr(stmt, 'end_lineno'):
                 source_lines.append(f"{stmt.lineno}-{stmt.end_lineno}")
        return {"source_hash": hash(tuple(source_lines)), "line_count": len(source_lines)}


    def parse_code(self, content: str) -> Dict[str, Any]:
        """Parse PHP code using phpparser and extract detailed semantic elements."""
        if not phpparser:
            # Fallback to basic regex parsing if phpparser is not available
            # This is important for graceful degradation
            print("Warning: phpparser library not found. Falling back to basic PHP parsing.", file=sys.stderr)
            return self._parse_code_regex_fallback(content)

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
            tree = phpparser.parse(content)
        except Exception as e:
            print(f"Error parsing PHP code with phpparser: {e}", file=sys.stderr)
            # Optionally, fallback to regex on parsing failure
            return self._parse_code_regex_fallback(content)

        current_namespace = "global" # Default namespace

        for node in tree.children: # Assuming tree.children gives top-level nodes
            if isinstance(node, php_ast.Namespace):
                namespace_name = node.name.name if node.name else "global"
                current_namespace = namespace_name
                elements['namespaces'][f"namespace:{namespace_name}"] = {
                    'name': namespace_name,
                    'start_line': node.lineno,
                    'end_line': node.end_lineno,
                    'children': [] # Store top-level elements within this namespace
                }
                # Process nodes within the namespace
                for sub_node in node.children: # Assuming namespaces can have children
                    self._parse_node(sub_node, elements, current_namespace)
            elif isinstance(node, php_ast.UseDeclarations):
                 for use_node in node.uses:
                     elements['uses'].append({
                         'name': use_node.name.name,
                         'alias': use_node.alias.name if use_node.alias else None,
                         'type': use_node.type # function, const, or normal
                     })
            else:
                # Parse top-level elements in the global namespace
                self._parse_node(node, elements, current_namespace)
        
        # For simplicity, a placeholder for global code analysis
        elements['global_code'] = self._parse_body(tree.children)

        return elements

    def _parse_node(self, node: 'php_ast.Node', elements: Dict[str, Any], namespace: str): # String literal type hint
        """Helper function to parse individual PHP AST nodes."""
        if not php_ast: return # Guard clause, nothing to do if no AST module

        node_namespace_prefix = f"{namespace}::" if namespace != "global" else ""

        if isinstance(node, php_ast.FunctionDeclaration):
            func_name = node.name.name
            func_id = f"func:{node_namespace_prefix}{func_name}"
            elements['functions'][func_id] = {
                'name': func_name,
                'namespace': namespace,
                'params': self._parse_parameters(getattr(node, 'params', None)),
                'return_type': php_ast.dump(node.return_type) if getattr(node, 'return_type', None) else None,
                'body_summary': self._parse_body(node.body.children if hasattr(node, 'body') and hasattr(node.body, 'children') else []),
                'docstring': self._extract_docstring(node),
                'attributes': [php_ast.dump(attr) for attr in node.attributes] if hasattr(node, 'attributes') else [],
                'start_line': node.lineno,
                'end_line': node.end_lineno,
            }
        elif isinstance(node, php_ast.ClassDeclaration):
            class_name = node.name.name
            class_id = f"class:{node_namespace_prefix}{class_name}"
            elements['classes'][class_id] = {
                'name': class_name,
                'namespace': namespace,
                'extends': node.extends.name if hasattr(node, 'extends') and node.extends else None,
                'implements': [impl.name for impl in node.implements] if hasattr(node, 'implements') else [],
                'methods': {},
                'properties': {},
                'constants': {},
                'docstring': self._extract_docstring(node),
                'attributes': [php_ast.dump(attr) for attr in node.attributes] if hasattr(node, 'attributes') else [],
                'is_abstract': getattr(node, 'is_abstract', False),
                'is_final': getattr(node, 'is_final', False),
                'start_line': node.lineno,
                'end_line': node.end_lineno,
            }
            # Parse class members
            for member in node.body.children: # Assuming class body has children
                if isinstance(member, php_ast.MethodDeclaration):
                    method_name = member.name.name
                    method_id = f"method:{class_name}::{method_name}"
                    elements['classes'][class_id]['methods'][method_id] = {
                        'name': method_name,
                        'params': self._parse_parameters(getattr(member, 'params', None)),
                        'return_type': php_ast.dump(member.return_type) if getattr(member, 'return_type', None) else None,
                        'body_summary': self._parse_body(member.body.children if hasattr(member, 'body') and hasattr(member.body, 'children') else []),
                        'visibility': member.visibility, # public, protected, private
                        'is_static': getattr(member, 'is_static', False),
                        'is_abstract': getattr(member, 'is_abstract', False),
                        'is_final': getattr(member, 'is_final', False),
                        'docstring': self._extract_docstring(member),
                        'attributes': [php_ast.dump(attr) for attr in member.attributes] if hasattr(member, 'attributes') else [],
                        'start_line': member.lineno,
                        'end_line': member.end_lineno,
                    }
                elif isinstance(member, php_ast.PropertyDeclaration):
                    # Properties can declare multiple props like: public $a, $b;
                    for prop_item in member.props:
                        prop_name = prop_item.name.name
                        prop_id = f"prop:{class_name}::{prop_name}"
                        elements['classes'][class_id]['properties'][prop_id] = {
                            'name': prop_name,
                            'type': php_ast.dump(member.type) if hasattr(member, 'type') and member.type else None,
                            'visibility': member.visibility,
                            'is_static': getattr(member, 'is_static', False),
                            'default_value': php_ast.dump(prop_item.default) if hasattr(prop_item, 'default') and prop_item.default else None,
                            'docstring': self._extract_docstring(member), # Docstring is usually on the declaration
                            'attributes': [php_ast.dump(attr) for attr in member.attributes] if hasattr(member, 'attributes') else [],
                            'start_line': member.lineno,
                            'end_line': member.end_lineno,
                        }
                elif isinstance(member, php_ast.ClassConstantDeclaration):
                     for const_item in member.consts:
                        const_name = const_item.name.name
                        const_id = f"const:{class_name}::{const_name}"
                        elements['classes'][class_id]['constants'][const_id] = {
                            'name': const_name,
                            'value': php_ast.dump(const_item.value), # Or a better representation
                            'visibility': getattr(member, 'visibility', 'public'), # Constants have visibility in PHP 7.1+
                            'docstring': self._extract_docstring(member),
                            'start_line': member.lineno,
                            'end_line': member.end_lineno,
                        }
        elif isinstance(node, php_ast.InterfaceDeclaration):
            interface_name = node.name.name
            interface_id = f"interface:{node_namespace_prefix}{interface_name}"
            elements['interfaces'][interface_id] = {
                'name': interface_name,
                'namespace': namespace,
                'extends': [ext.name for ext in node.extends] if hasattr(node, 'extends') else [],
                'methods': {}, # Store method signatures
                'constants': {},
                'docstring': self._extract_docstring(node),
                'start_line': node.lineno,
                'end_line': node.end_lineno,
            }
            for member in node.body.children:
                if isinstance(member, php_ast.MethodDeclaration): # Interface methods
                    method_name = member.name.name
                    elements['interfaces'][interface_id]['methods'][f"method:{interface_name}::{method_name}"] = {
                         'name': method_name,
                         'params': self._parse_parameters(getattr(member, 'params', None)),
                         'return_type': php_ast.dump(member.return_type) if getattr(member, 'return_type', None) else None,
                         'visibility': member.visibility,
                         'is_static': getattr(member, 'is_static', False),
                         'docstring': self._extract_docstring(member),
                    }
                elif isinstance(member, php_ast.ClassConstantDeclaration): # Interface constants
                    for const_item in member.consts:
                        const_name = const_item.name.name
                        elements['interfaces'][interface_id]['constants'][f"const:{interface_name}::{const_name}"] = {
                            'name': const_name,
                            'value': php_ast.dump(const_item.value),
                            'docstring': self._extract_docstring(member),
                        }
        elif isinstance(node, php_ast.TraitDeclaration):
            trait_name = node.name.name
            trait_id = f"trait:{node_namespace_prefix}{trait_name}"
            elements['traits'][trait_id] = {
                'name': trait_name,
                'namespace': namespace,
                'methods': {}, # Similar to class methods
                'properties': {}, # Similar to class properties
                'uses': [], # For trait adaptations (insteadof, as) - complex
                'docstring': self._extract_docstring(node),
                'start_line': node.lineno,
                'end_line': node.end_lineno,
            }
            # Parse trait members (methods, properties) similar to classes
            # ... (implementation would be similar to class member parsing) ...
        elif isinstance(node, php_ast.ConstantDeclaration): # Global constants
            for const_item in node.consts:
                const_name = const_item.name.name
                const_id = f"const:{node_namespace_prefix}{const_name}"
                elements['constants'][const_id] = {
                    'name': const_name,
                    'namespace': namespace,
                    'value': php_ast.dump(const_item.value),
                    'docstring': self._extract_docstring(node),
                    'start_line': node.lineno,
                    'end_line': node.end_lineno,
                }

    def _parse_code_regex_fallback(self, content: str) -> Dict[str, Any]:
        """Original regex-based parsing as a fallback."""
        elements = {
            'functions': {}, 'classes': {}, 'variables': set(), 'includes': [],
            'interfaces': {}, 'traits': {}, 'namespaces': {}, 'constants': {}, 'uses': [], 'global_code': {}
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

    def detect_changes(self, before: Dict[str, Any], after: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect changes in PHP code based on detailed AST parsing."""
        events: List[Dict[str, Any]] = []
        location = "php_file" # Placeholder, will be overwritten by MultiLanguageAnalyzer

        # Fallback to simpler diff if using regex data (e.g. phpparser failed)
        # We can check this by seeing if 'params' exists for functions, a feature of the new parser.
        is_detailed_parsing = True
        if list(before['functions'].values()) and 'params' not in list(before['functions'].values())[0]:
            is_detailed_parsing = False
        if list(after['functions'].values()) and 'params' not in list(after['functions'].values())[0]:
            is_detailed_parsing = False

        if not is_detailed_parsing:
            # Use a simplified version of detect_changes for regex fallback data
            return self._detect_changes_regex_fallback(before, after)

        # Compare Namespaces (Addition/Removal)
        self._compare_top_level_elements(before, after, 'namespaces', 'Namespace', events, location)
        
        # Compare Use Statements
        if before.get('uses') != after.get('uses'):
            # For simplicity, just note a general change. A real diff would be more complex.
            added_uses = [u for u in after.get('uses', []) if u not in before.get('uses', [])]
            removed_uses = [u for u in before.get('uses', []) if u not in after.get('uses', [])]
            if added_uses:
                 events.append({'event_type': 'php_use_statement_added', 'node_id': 'module', 'location': location, 'details': f"Added use statements: {added_uses}"})
            if removed_uses:
                 events.append({'event_type': 'php_use_statement_removed', 'node_id': 'module', 'location': location, 'details': f"Removed use statements: {removed_uses}"})


        # Compare Global Constants
        self._compare_top_level_elements(before, after, 'constants', 'Global Constant', events, location, self._compare_constant_details)

        # Compare Functions
        self._compare_top_level_elements(before, after, 'functions', 'Function', events, location, self._compare_function_details)

        # Compare Classes
        self._compare_top_level_elements(before, after, 'classes', 'Class', events, location, self._compare_class_details)

        # Compare Interfaces
        self._compare_top_level_elements(before, after, 'interfaces', 'Interface', events, location, self._compare_interface_details)

        # Compare Traits
        self._compare_top_level_elements(before, after, 'traits', 'Trait', events, location, self._compare_trait_details)

        # Compare global code (very basic)
        if before.get('global_code', {}).get('source_hash') != after.get('global_code', {}).get('source_hash'):
            events.append({'event_type': 'php_global_code_changed', 'node_id': 'global_scope', 'location': location, 'details': 'Changes detected in global scope code.'})

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

        if sorted(before_class.get('implements', [])) != sorted(after_class.get('implements', [])):
            added = set(after_class.get('implements', [])) - set(before_class.get('implements', []))
            removed = set(before_class.get('implements', [])) - set(after_class.get('implements', []))
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
        if sorted(before_iface.get('extends', [])) != sorted(after_iface.get('extends', [])):
            events.append({'event_type': 'php_interface_extends_changed', 'node_id': iface_id, 'location': location,
                           'details': f"{context}extends changed from {before_iface.get('extends')} to {after_iface.get('extends')}"})

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


class JavaScriptAnalyzer(LanguageAnalyzer):
    """Semantic analyzer for JavaScript code."""
    
    def parse_code(self, content: str) -> Dict[str, Any]:
        """Parse JavaScript code and extract functions, classes, variables."""
        elements = {
            'functions': {},
            'classes': {},
            'variables': set(),
            'imports': []
        }
        
        # Extract JavaScript functions
        function_patterns = [
            r'function\s+([a-zA-Z_$]\w*)\s*\([^)]*\)',  # function declaration
            r'const\s+([a-zA-Z_$]\w*)\s*=\s*\([^)]*\)\s*=>',  # arrow function
            r'([a-zA-Z_$]\w*)\s*:\s*function\s*\([^)]*\)'  # object method
        ]
        
        for pattern in function_patterns:
            for match in re.finditer(pattern, content):
                func_name = match.group(1)
                elements['functions'][f'func:{func_name}'] = {
                    'name': func_name,
                    'start': match.start(),
                    'signature': match.group(0)
                }
        
        # Extract JavaScript classes
        class_pattern = r'class\s+([a-zA-Z_$]\w*)'
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            elements['classes'][f'class:{class_name}'] = {
                'name': class_name,
                'start': match.start()
            }
        
        # Extract variable declarations
        var_patterns = [
            r'(?:var|let|const)\s+([a-zA-Z_$]\w*)',
            r'([a-zA-Z_$]\w*)\s*='
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
            events.append({
                'event_type': 'node_added',
                'node_id': func_id,
                'location': 'js_file',
                'details': f'JavaScript function {func_id} added'
            })
        
        # Removed functions
        for func_id in before_funcs - after_funcs:
            events.append({
                'event_type': 'node_removed',
                'node_id': func_id,
                'location': 'js_file',
                'details': f'JavaScript function {func_id} removed'
            })
        
        # Class changes (similar pattern as PHP)
        before_classes = set(before['classes'].keys())
        after_classes = set(after['classes'].keys())
        
        for class_id in after_classes - before_classes:
            events.append({
                'event_type': 'node_added',
                'node_id': class_id,
                'location': 'js_file',
                'details': f'JavaScript class {class_id} added'
            })
        
        for class_id in before_classes - after_classes:
            events.append({
                'event_type': 'node_removed',
                'node_id': class_id,
                'location': 'js_file',
                'details': f'JavaScript class {class_id} removed'
            })
        
        return events

class MultiLanguageAnalyzer:
    """Main multi-language analyzer that delegates to language-specific analyzers."""
    
    def __init__(self):
        self.analyzers = {
            '.php': PHPAnalyzer(),
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
        
        # Add metadata
        for event in events:
            event['language'] = language.lstrip('.')
            event['location'] = filepath
        
        return events
    
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
    
    # Test PHP
    print("\n--- ADVANCED PHP ANALYSIS TEST ---")

    php_before_advanced = '''<?php
namespace MyProject\\Utils;

use AnotherProject\\Logger;

/**
 * A utility class.
 */
#[AnAttribute]
class Utility {
    private string $name;
    public const VERSION = "1.0";

    public function __construct(string $name) {
        $this->name = $name;
    }

    /**
     * Greets the user.
     */
    public function greet(): string {
        return "Hello, " . $this->name;
    }

    protected static function doSomethingInternal() {
        // internal logic
    }
}

interface Processable {
    public function process(array $data): bool;
}
?>'''
    
    php_after_advanced = '''<?php
namespace MyProject\\Utils;

// Use statement removed: use AnotherProject\\Logger;
use MyProject\\Helpers\\NewLogger; // Added use

/**
 * An enhanced utility class. (Docstring changed)
 */
#[AnAttribute] // Attribute unchanged
#[NewAttribute("beta")] // Attribute added
class Utility implements Processable { // Implements added
    private string $name;
    #[Versioned("2.0")] // Attribute added to property
    public string $description; // Property added
    public const VERSION = "1.1"; // Constant value changed
    final public const AUTHOR = "Jules"; // New constant added

    // Constructor signature changed, property promoted
    public function __construct(private string $name, string $description = "Default") {
        $this->description = $description;
    }

    /**
     * Greets the user with a title. (Docstring changed)
     */
    // greet signature changed, return type added
    public function greet(string $title): string {
        // Logic changed
        return "Hello, " . $title . " " . $this->name . "!";
    }

    // Method removed: doSomethingInternal

    public function process(array $data): bool { // Method from interface
        NewLogger::log("Processing data");
        return true;
    }

    public static function newStaticMethod(): void {} // New method
}

interface Processable { // Unchanged interface
    public function process(array $data): bool;
}

trait HelperTrait {
    public function help(): string { return "I am helping!"; }
}
?>'''
    
    print("\nAnalyzing advanced PHP changes (test_advanced.php):")
    # Simulate phpparser being available for this test run, if it's None
    original_phpparser_status = phpparser
    if phpparser is None:
        print("(Simulating phpparser availability for test by creating a mock)")
        # Create a minimal mock of phpparser and php_ast to allow test execution
        # This is very basic and won't actually parse, but prevents NameErrors
        class MockNameNode: # Helper for things that should have a .name attribute
            def __init__(self, name_val):
                self.name = name_val

        class MockAstNode:
            def __init__(self, name=None, lineno=0, end_lineno=0, children=None, **kwargs):
                # If name is a string, wrap it in MockNameNode for consistent access
                self.name = MockNameNode(name) if isinstance(name, str) else name
                self.lineno = lineno
                self.end_lineno = end_lineno
                self.children = children if children is not None else []
                self._mock_type = kwargs.pop('_mock_type', 'Node') # Store a mock type

                # Handle specific structures like 'params' or 'body' more carefully
                popped_params = kwargs.pop('params', None)
                if popped_params is not None:
                    if isinstance(popped_params, list): # if it's a list of param definitions
                        # Each item in popped_params should represent a parameter.
                        # Let's assume for simplicity params attribute holds a list of MockAstNode params
                        self.params = [MockAstNode(**p) if isinstance(p, dict) else p for p in popped_params]
                    elif isinstance(popped_params, MockAstNode): # if it's already a node
                        self.params = popped_params
                    else: # If it's something else, assign directly (or wrap if needed)
                        self.params = MockAstNode(_mock_type='ParametersNode', params_list=popped_params)


                popped_body = kwargs.pop('body', None)
                if popped_body is not None:
                    if isinstance(popped_body, list): # e.g. for functions/methods, list of statements
                        self.body = MockAstNode(children=popped_body, _mock_type='BodyNode')
                    elif isinstance(popped_body, MockAstNode): # if it's already a node
                        self.body = popped_body
                    else:
                        self.body = MockAstNode(_mock_type='BodyNode', content=popped_body)


                if 'props' in kwargs: # For PropertyDeclaration
                    self.props = [MockAstNode(**p) if isinstance(p, dict) else p for p in kwargs.pop('props')]
                if 'consts' in kwargs: # For ConstantDeclaration
                    self.consts = [MockAstNode(**c) if isinstance(c, dict) else c for c in kwargs.pop('consts')]
                if 'uses' in kwargs: # For UseDeclarations
                    self.uses = [MockAstNode(**u) if isinstance(u, dict) else u for u in kwargs.pop('uses')]


                for k,v in kwargs.items():
                    setattr(self, k, v)

            # Make isinstance work somewhat with _mock_type
            def __instancecheck__(self, instance):
                 return getattr(instance, '_mock_type', None) == self._mock_type


        MOCK_PHP_AST_TYPES = {}

        def create_mock_ast_type(type_name):
            class_attributes = {'_mock_type': type_name}
            # Define __isinstance__ for the dynamically created class
            def custom_isinstance(self, instance):
                # Check if instance has _mock_type and if it matches this class's type_name
                return getattr(instance, '_mock_type', None) == type_name

            # For some reason, directly assigning __isinstance__ doesn't work as expected for isinstance()
            # Instead, we'll rely on checking node._mock_type directly in parsing logic for mocks.
            # However, this structure is useful for type creation.
            NewType = type(type_name, (MockAstNode,), class_attributes)
            MOCK_PHP_AST_TYPES[type_name] = NewType
            return NewType

        # Define mock AST node types that are checked with isinstance
        # These will now be actual classes inheriting from MockAstNode
        MockNamespace = create_mock_ast_type('Namespace')
        MockUseDeclarations = create_mock_ast_type('UseDeclarations')
        MockFunctionDeclaration = create_mock_ast_type('FunctionDeclaration')
        MockClassDeclaration = create_mock_ast_type('ClassDeclaration')
        MockInterfaceDeclaration = create_mock_ast_type('InterfaceDeclaration')
        MockTraitDeclaration = create_mock_ast_type('TraitDeclaration')
        MockConstantDeclaration = create_mock_ast_type('ConstantDeclaration')
        MockMethodDeclaration = create_mock_ast_type('MethodDeclaration')
        MockPropertyDeclaration = create_mock_ast_type('PropertyDeclaration')
        MockClassConstantDeclaration = create_mock_ast_type('ClassConstantDeclaration')
        # Add other types as needed by the parser logic for isinstance checks

        # The global mock_php_ast object will provide these types
        mock_php_ast_global = type('MockPhpAstGlobal', (), {
            **MOCK_PHP_AST_TYPES, # Unpack all defined mock types
            'Node': MockAstNode, # Generic base
            'Parameters': create_mock_ast_type('Parameters'), # For function params
            'dump': lambda x: f"mock_dump:{str(x)}" if not isinstance(x, MockAstNode) else f"mock_dump_node:{getattr(x.name, 'name', 'UnnamedNode') if hasattr(x, 'name') and x.name else getattr(x, '_mock_type', 'Node')}"
        })


        class MockPhpParser:
            def parse(self, content):
                # This mock needs to return a tree of MockAstNode instances
                # that roughly match what the PHPAnalyzer expects.
                # This is highly simplified.
                root_children = []
                if "namespace MyProject\\Utils;" in content:
                    ns_children = []
                    if "class Utility" in content:
                        utility_methods = []
                        method_defaults = {
                            'visibility': 'public', 'is_static': False, 'is_abstract': False, 'is_final': False,
                            'attributes': [], 'doc_comment': None, 'return_type': None
                        }
                        if "function __construct" in content:
                             utility_methods.append(MockMethodDeclaration(name="__construct", params=[], body=[], **method_defaults))
                        if "function greet" in content:
                             utility_methods.append(MockMethodDeclaration(name="greet", params=[], body=[], **method_defaults))

                        class_defaults = {
                            'extends': None, 'implements': [], 'attributes': [], 'doc_comment': None,
                            'is_abstract': False, 'is_final': False
                        }
                        property_defaults = {
                            'type': None, 'visibility': 'public', 'is_static': False, 'default_value': None,
                            'attributes': [], 'doc_comment': None
                        }
                        const_defaults = {
                            'value': 'mock_value', 'visibility': 'public', 'doc_comment': None
                        }

                        # Simplified: Assume Utility class has some properties and constants for broader mock coverage
                        utility_properties = [
                            # props expects a list of nodes, each representing a property item
                            MockPropertyDeclaration(name='name', props=[MockAstNode(name='name', default=None)], **property_defaults)
                        ]
                        utility_constants = [
                            # consts expects a list of nodes, each representing a constant item
                            MockClassConstantDeclaration(name='VERSION', consts=[MockAstNode(name='VERSION', value='1.0')], **const_defaults)
                        ]

                        class_body_children = utility_methods + utility_properties + utility_constants
                        class_body = MockAstNode(children=class_body_children)
                        ns_children.append(MockClassDeclaration(name="Utility", body=class_body, **class_defaults))

                    root_children.append(MockNamespace(name="MyProject\\Utils", children=ns_children))

                if "trait HelperTrait" in content:
                     root_children.append(MockTraitDeclaration(name="HelperTrait", children=[]))

                return MockAstNode(children=root_children)

        # Temporarily assign mocks
        globals()['phpparser'] = MockPhpParser()
        globals()['php_ast'] = mock_php_ast_global


    advanced_events = analyzer.analyze_file_changes("test_advanced.php", php_before_advanced, php_after_advanced)

    # Restore original phpparser status
    if original_phpparser_status is None:
        globals()['phpparser'] = None
        globals()['php_ast'] = None # Also restore php_ast
        # No easy way to un-import php_ast if it was mocked, but phpparser = None handles it

    print(f"Advanced PHP events detected: {len(advanced_events)}")
    if not advanced_events:
        print("NOTE: No advanced events detected. This might be due to the phpparser not being available or the mock being too simple, causing fallback to regex.")
    else:
        print("Expected events (examples, actual events depend on full mock/parser):")
        print("  - php_use_statement_removed, php_use_statement_added")
        print("  - php_docstring_changed (for class Utility)")
        print("  - php_attribute_added (for class Utility, property description)")
        print("  - php_inheritance_changed (Utility implements Processable)")
        print("  - node_added (for property description, const AUTHOR, method newStaticMethod, trait HelperTrait)")
        print("  - php_constant_value_changed (for VERSION)")
        print("  - php_node_signature_changed (for Utility::__construct, Utility::greet)")
        print("  - php_return_type_changed (for Utility::greet)")
        print("  - php_node_logic_changed (for Utility::greet)")
        print("  - node_removed (for method doSomethingInternal)")

    for event in advanced_events[:15]: # Print first 15 events
        details = event.get('details', '')
        if len(details) > 100: # Truncate long details for display
            details = details[:97] + "..."
        print(f"  - {event['event_type']}: {event['node_id']} - {details}")
    if len(advanced_events) > 15:
        print(f"  ... and {len(advanced_events) - 15} more events.")

    print("\n--- BASIC PHP ANALYSIS TEST (Fallback if phpparser not found) ---")
    # This test will use the regex fallback if phpparser is truly None
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
    print(f"Basic PHP events detected (potentially fallback): {len(basic_events)}")
    for event in basic_events:
        print(f"  - {event['event_type']}: {event['node_id']} - {event['details']}")
    if not phpparser:
        print("(Running with regex fallback as phpparser is not available)")
    else:
        print("(Running with phpparser as it seems available/mocked)")

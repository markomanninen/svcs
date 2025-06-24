# SVCS JavaScript Parser
# Comprehensive JavaScript/TypeScript parser

import re
import ast
import json
from typing import Dict, Set, List, Any
from .base_parser import BaseParser

# Try to import esprima for JavaScript parsing
try:
    import esprima
    esprima_available = True
except ImportError:
    esprima_available = False
    print("Warning: esprima not available, falling back to regex parsing for JavaScript")

class JavaScriptParser(BaseParser):
    """JavaScript/TypeScript parser with esprima and regex fallbacks."""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = {'.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs'}
        self.language_name = "JavaScript"
    
    def parse_code(self, source_code: str) -> tuple:
        """Parse JavaScript/TypeScript code."""
        if esprima_available:
            try:
                return self._parse_with_esprima(source_code)
            except Exception as e:
                print(f"Esprima parsing failed: {e}, falling back to advanced regex")
                return self._parse_with_advanced_regex(source_code)
        else:
            return self._parse_with_advanced_regex(source_code)
    
    def _parse_with_esprima(self, source_code: str) -> tuple:
        """Parse JavaScript using esprima."""
        nodes = {}
        dependencies = set()
        
        try:
            # Try to parse as script first, then as module if that fails
            try:
                ast = esprima.parseScript(source_code, {'loc': True, 'tolerant': True})
            except:
                ast = esprima.parseModule(source_code, {'loc': True, 'tolerant': True})
            
            # Extract functions and classes
            self._extract_nodes_esprima(ast, nodes)
            
            # Extract dependencies (import/require statements)
            self._extract_dependencies_esprima(ast, dependencies)
            
            # Extract assignment targets from esprima AST
            assignment_targets = set()
            self._extract_assignment_targets_esprima(ast, assignment_targets)
            
            # Extract behavioral patterns for Layer 4 analysis (enhanced with esprima data)
            self._extract_behavioral_patterns_esprima(source_code, nodes, assignment_targets)
            
        except Exception as e:
            print(f"Warning: Esprima JavaScript parsing failed: {e}")
            return self._parse_with_advanced_regex(source_code)
        
        return nodes, dependencies
    
    def _parse_with_advanced_regex(self, source_code: str) -> tuple:
        """Advanced JavaScript parsing using regex patterns with ES6 support."""
        nodes = {}
        dependencies = set()
        
        # Clean the code - remove comments and normalize whitespace
        cleaned_code = self._preprocess_js(source_code)
        
        # Extract ES6 classes with methods and inheritance
        self._extract_es6_classes(cleaned_code, nodes)
        
        # Extract all function types (regular, arrow, async, generator)
        self._extract_functions(cleaned_code, nodes)
        
        # Extract imports and requires
        self._extract_dependencies(cleaned_code, dependencies)
        
        # Detect functional programming patterns
        self._detect_functional_programming(cleaned_code, nodes)
        
        # Extract detailed behavioral patterns for Layer 4 analysis
        self._extract_behavioral_patterns(cleaned_code, nodes)
        
        return nodes, dependencies
    
    def _preprocess_js(self, source_code: str) -> str:
        """Preprocess JavaScript code - remove comments, normalize spacing while preserving structure."""
        # Remove multi-line comments
        code = re.sub(r'/\*[\s\S]*?\*/', '', source_code)
        
        # Remove single-line comments while preserving line structure
        code = re.sub(r'//.*?$', '', code, flags=re.MULTILINE)
        
        # Preserve line breaks to maintain code structure
        # Replace sequences of whitespace with a single space, but preserve newlines
        code = re.sub(r'[ \t\f\v]+', ' ', code)
        
        # Remove whitespace between certain operators and operands to simplify parsing
        code = re.sub(r'\s*([=+\-*/%&|^<>!?:;,{}[\]()])\s*', r'\1', code)
        
        # Add the whitespace back in for cleaner parsing of more complex constructs
        code = re.sub(r'([=+\-*/%&|^<>!?:;,{}[\]()])', r' \1 ', code)
        
        # Fix augmented assignment operators FIRST (they have priority)
        code = re.sub(r' \+ \s* = ', ' += ', code)
        code = re.sub(r' \- \s* = ', ' -= ', code)
        code = re.sub(r' \* \s* = ', ' *= ', code)
        code = re.sub(r' / \s* = ', ' /= ', code)
        code = re.sub(r' % \s* = ', ' %= ', code)
        code = re.sub(r' \* \* \s* = ', ' **= ', code)
        code = re.sub(r' & \s* = ', ' &= ', code)
        code = re.sub(r' \| \s* = ', ' |= ', code)
        code = re.sub(r' \^ \s* = ', ' ^= ', code)
        code = re.sub(r' < < \s* = ', ' <<= ', code)
        code = re.sub(r' > > \s* = ', ' >>= ', code)
        
        # Fix overzealous whitespace for arrow functions and logical operators
        code = re.sub(r' > > ', '>>', code)
        code = re.sub(r' < < ', '<<', code)
        code = re.sub(r' \+ \+ ', '++', code)
        code = re.sub(r' \- \- ', '--', code)
        code = re.sub(r' \& \& ', '&&', code)
        code = re.sub(r' \| \| ', '||', code)
        code = re.sub(r' \= \> ', '=>', code)
        code = re.sub(r' \= \= ', '==', code)
        code = re.sub(r' \= \= \= ', '===', code)
        code = re.sub(r' \! \= ', '!=', code)
        code = re.sub(r' \! \= \= ', '!==', code)
        
        # Normalize template literal placeholders
        code = re.sub(r'\$\{\s*([^}]*)\s*\}', r'${{\1}}', code)
        
        return code
    
    def _extract_es6_classes(self, code: str, nodes: dict) -> None:
        """Extract ES6 class declarations with methods and inheritance."""
        # Match class declarations with potential inheritance
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{([^}]*?)\}'
        
        for match in re.finditer(class_pattern, code, re.DOTALL):  # Add DOTALL to handle multi-line classes
            class_name = match.group(1)
            extends = match.group(2)
            class_body = match.group(3)
            
            details = {
                "type": "class",
                "source": match.group(0),
                "base_classes": {extends} if extends else set(),
                "methods": set(),
                "properties": set(),
                "static_methods": set(),
                "static_properties": set(),
                "getters": set(),
                "setters": set()
            }
            
            # Extract class fields (properties) - ES Next class fields
            field_pattern = r'(?:static\s+)?(\w+)\s*=\s*'
            for field_match in re.finditer(field_pattern, class_body):
                field_name = field_match.group(1)
                if "static" in field_match.group(0):
                    details["static_properties"].add(field_name)
                else:
                    details["properties"].add(field_name)
            
            # Extract methods within the class
            method_pattern = r'(?:async\s+)?(?:static\s+)?(?:get\s+|set\s+)?(\w+)\s*\([^)]*\)'
            constructor_pattern = r'constructor\s*\(([^)]*)\)'
            
            # Extract constructor parameters and check for defaults
            constructor_match = re.search(constructor_pattern, class_body)
            if constructor_match:
                params = constructor_match.group(1)
                details["has_constructor"] = True
                details["constructor_params"] = params.strip()
                details["methods"].add("constructor")
                
                # Check for default parameters in constructor
                if "=" in params:
                    details["has_defaults"] = True
                
                # Check for destructuring in constructor
                if "{" in params or "}" in params or "[" in params or "]" in params:
                    details["has_destructuring"] = True
            else:
                details["has_constructor"] = False
            
            # Extract other methods
            for method_match in re.finditer(method_pattern, class_body):
                full_match = method_match.group(0)
                method_name = method_match.group(1)
                
                if method_name != 'constructor':  # Skip constructor as we already handled it
                    if "static" in full_match:
                        details["static_methods"].add(method_name)
                    elif "get " in full_match:
                        details["getters"].add(method_name)
                    elif "set " in full_match:
                        details["setters"].add(method_name)
                    else:
                        details["methods"].add(method_name)
            
            # Detect if class uses private fields (# prefix)
            private_field_pattern = r'#(\w+)'
            private_fields = re.findall(private_field_pattern, class_body)
            if private_fields:
                details["has_private_fields"] = True
                details["private_fields"] = set(private_fields)
            
            # Combine all properties into attributes for behavioral analysis
            all_attributes = details["properties"] | details["static_properties"]
            details["attributes"] = all_attributes
            
            nodes[f"class:{class_name}"] = details
    
    def _extract_functions(self, code: str, nodes: dict) -> None:
        """Extract various function types including ES6 features."""
        # Regular function declarations - more precise patterns
        func_patterns = {
            "regular": r'function\s+(\w+)\s*\(([^)]*)\)\s*\{',
            "method": r'(\w+)\s*:\s*function\s*\(([^)]*)\)\s*\{',
            "arrow_const": r'const\s+(\w+)\s*=\s*(?:async\s*)?\(?([^=>]*)\)?\s*=>\s*',
            "arrow_let": r'let\s+(\w+)\s*=\s*(?:async\s*)?\(?([^=>]*)\)?\s*=>\s*',
            "arrow_var": r'var\s+(\w+)\s*=\s*(?:async\s*)?\(?([^=>]*)\)?\s*=>\s*',
            "prop_method": r'(\w+)\s*\(([^)]*)\)\s*\{',  # ES6 object method shorthand
            "assignment": r'(\w+)\s*=\s*function\s*\(([^)]*)\)\s*\{',
            "object_method": r'(\w+)\s*\(([^)]*)\)\s*\{',  # ES6 object method shorthand
            "async_method": r'async\s+(\w+)\s*\(([^)]*)\)\s*\{',  # async method
            "generator_method": r'(\w+)\s*\*\s*\(([^)]*)\)\s*\{',  # generator method
        }
        
        # Object properties and destructuring patterns
        obj_pattern = r'(\w+)\s*:\s*(\w+)'
        destruct_pattern = r'(?:const|let|var)\s*\{([^}]+)\}'
        
        # First extract destructuring assignments
        for match in re.finditer(destruct_pattern, code):
            destructured = match.group(1)
            # Process each destructured variable
            for var_match in re.finditer(r'(\w+)(?:\s*:\s*(\w+))?', destructured):
                var_name = var_match.group(2) if var_match.group(2) else var_match.group(1)
                # Add as a special node
                nodes[f"var:{var_name}"] = {
                    "type": "variable",
                    "source": var_match.group(0),
                    "is_destructured": True
                }
        
        # Extract functions
        for pattern_type, pattern in func_patterns.items():
            for match in re.finditer(pattern, code):
                func_name = match.group(1)
                params = match.group(2).strip()
                
                # Enhanced default parameters detection - only check within parameter list
                has_defaults = False
                has_destructuring = False
                
                # More precise default parameter detection
                if params.strip():
                    # Check if there are actual default values in parameters
                    # Look for parameter = value pattern (not variable assignments)
                    # Split by comma and check each parameter
                    param_parts = []
                    in_object = 0
                    in_array = 0
                    current_param = ""
                    
                    for char in params:
                        if char == '{': in_object += 1
                        elif char == '}': in_object -= 1
                        elif char == '[': in_array += 1
                        elif char == ']': in_array -= 1
                        elif char == ',' and in_object == 0 and in_array == 0:
                            param_parts.append(current_param.strip())
                            current_param = ""
                            continue
                        current_param += char
                    
                    if current_param.strip():
                        param_parts.append(current_param.strip())
                    
                    # Check each parameter for default values
                    for param in param_parts:
                        if '=' in param and not param.startswith('='):
                            # This looks like a default parameter
                            has_defaults = True
                        if '{' in param or '}' in param or '[' in param or ']' in param:
                            has_destructuring = True
                
                # Extract parameter list properly
                param_list = []
                if params:
                    # Handle destructuring and default parameters properly
                    in_object = 0
                    in_array = 0
                    param_start = 0
                    
                    for i, char in enumerate(params):
                        if char == '{': in_object += 1
                        elif char == '}': in_object -= 1
                        elif char == '[': in_array += 1
                        elif char == ']': in_array -= 1
                        elif char == ',' and in_object == 0 and in_array == 0:
                            param = params[param_start:i].strip()
                            if param:
                                # Handle default values
                                clean_param = param.split('=')[0].strip()
                                param_list.append(clean_param)
                            param_start = i + 1
                    
                    # Don't forget the last parameter
                    last_param = params[param_start:].strip()
                    if last_param:
                        clean_param = last_param.split('=')[0].strip()
                        param_list.append(clean_param)
                
                # Detect if arrow function (for functional programming detection)
                is_arrow = "arrow" in pattern_type
                
                details = {
                    "type": "function",
                    "source": match.group(0),
                    "parameters": param_list,
                    "is_async": "async" in match.group(0),
                    "is_generator": "*" in match.group(0) or pattern_type == "generator_method",
                    "has_defaults": has_defaults,
                    "has_destructuring": has_destructuring,
                    "is_arrow_function": is_arrow,
                    "functional_programming": is_arrow  # Arrow functions indicate functional programming
                }
                
                # Add exception handling extraction for regex version
                try_catch_info = self._extract_exception_handling_regex(match.group(0))
                details["exception_handlers"] = try_catch_info.get("exception_handlers", set())
                details["exception_handling"] = {
                    "has_try_catch": try_catch_info.get("has_try_catch", False),
                    "catch_types": try_catch_info.get("catch_types", set())
                }
                
                # Add scope information extraction
                scope_info = self._extract_scope_patterns_regex(match.group(0))
                details["global_statements"] = scope_info.get("global_statements", set())
                details["nonlocal_statements"] = scope_info.get("nonlocal_statements", set())
                
                # Add signature
                details["signature"] = f"{func_name}({params})"
                
                nodes[f"func:{func_name}"] = details
    
    def _extract_dependencies(self, code: str, dependencies: set) -> None:
        """Extract all forms of JavaScript dependencies."""
        import_patterns = [
            # ES6 imports
            r'import\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]',  # import Module from 'module'
            r'import\s+\{\s*([^}]+)\s*\}\s+from\s+[\'"]([^\'"]+)[\'"]',  # import { named } from 'module'
            r'import\s+\*\s+as\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]',  # import * as Module from 'module'
            r'import\s+[\'"]([^\'"]+)[\'"]',  # import 'module' (side effects)
            
            # Dynamic imports
            r'import\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)',  # import('module')
            
            # CommonJS require
            r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)',  # require('module')
            
            # AMD define
            r'define\s*\(\s*\[\s*[\'"]([^\'"]+)[\'"]\s*\]',  # define(['module'])
            
            # Module exports
            r'export\s+(\w+|default|class|function|const|let|var)\s+(\w+)',  # export class Foo
            r'export\s+\{\s*([^}]+)\s*\}',  # export { named }
            r'export\s+\*\s+from\s+[\'"]([^\'"]+)[\'"]',  # export * from 'module'
        ]
        
        for pattern in import_patterns:
            for match in re.finditer(pattern, code):
                # Get the module path from the appropriate group
                if 'from' in pattern or 'export *' in pattern:
                    if match.lastindex >= 2:
                        dependencies.add(match.group(match.lastindex))
                    elif match.lastindex == 1:
                        # Handle direct import or export * from
                        dependencies.add(match.group(1))
                else:
                    # For require, dynamic import, etc.
                    dependencies.add(match.group(1))
                    
        # Handle ESM named exports to track internal dependencies
        export_pattern = r'export\s+(?:const|let|var|function|class)\s+(\w+)'
        for match in re.finditer(export_pattern, code):
            # Add as an exported symbol
            dependencies.add(f"export:{match.group(1)}")
    
    def _extract_nodes_esprima(self, node, nodes: dict):
        """Extract nodes using esprima AST."""
        if hasattr(node, 'type'):
            # Function declarations
            if node.type == 'FunctionDeclaration':
                if hasattr(node, 'id') and node.id:
                    func_name = node.id.name
                    nodes[f"func:{func_name}"] = self._get_function_details_esprima(node)
            
            # Class declarations
            elif node.type == 'ClassDeclaration':
                if hasattr(node, 'id') and node.id:
                    class_name = node.id.name
                    nodes[f"class:{class_name}"] = self._get_class_details_esprima(node)
            
            # Variable declarations
            elif node.type == 'VariableDeclaration':
                if hasattr(node, 'declarations'):
                    for decl in node.declarations:
                        self._process_variable_declaration(decl, nodes)
            
            # Export declarations
            elif node.type == 'ExportNamedDeclaration' or node.type == 'ExportDefaultDeclaration':
                if hasattr(node, 'declaration') and node.declaration:
                    # Process the declaration itself
                    self._extract_nodes_esprima(node.declaration, nodes)
                    
                    # Mark as exported
                    if hasattr(node.declaration, 'id') and node.declaration.id:
                        name = node.declaration.id.name
                        if f"func:{name}" in nodes:
                            nodes[f"func:{name}"]["exported"] = True
                        elif f"class:{name}" in nodes:
                            nodes[f"class:{name}"]["exported"] = True
            
            # Object expressions with methods
            elif node.type == 'ObjectExpression':
                if hasattr(node, 'properties'):
                    for prop in node.properties:
                        if hasattr(prop, 'key') and hasattr(prop, 'value'):
                            if hasattr(prop.key, 'name') and hasattr(prop.value, 'type'):
                                if prop.value.type in ['FunctionExpression', 'ArrowFunctionExpression']:
                                    obj_method_name = prop.key.name
                                    nodes[f"method:{obj_method_name}"] = self._get_function_details_esprima(prop.value)
        
        # Recursively process children
        for key, value in vars(node).items():
            if isinstance(value, list):
                for item in value:
                    if hasattr(item, 'type'):
                        self._extract_nodes_esprima(item, nodes)
            elif hasattr(value, 'type'):
                self._extract_nodes_esprima(value, nodes)
    
    def _process_variable_declaration(self, decl, nodes: dict):
        """Process a variable declaration node from esprima."""
        # Handle function expressions assigned to variables
        if (hasattr(decl, 'init') and decl.init and 
            hasattr(decl.init, 'type')):
            
            # Handle identifier
            if hasattr(decl, 'id'):
                # Simple variable name
                if hasattr(decl.id, 'name'):
                    var_name = decl.id.name
                    
                    # Function expressions (including arrow functions)
                    if decl.init.type in ['FunctionExpression', 'ArrowFunctionExpression']:
                        func_details = self._get_function_details_esprima(decl.init)
                        func_details["signature"] = f"{var_name}{func_details.get('signature', '()')}"
                        nodes[f"func:{var_name}"] = func_details
                    
                    # Class expressions
                    elif decl.init.type == 'ClassExpression':
                        class_details = self._get_class_details_esprima(decl.init)
                        nodes[f"class:{var_name}"] = class_details
                    
                    # Object expressions (potential module pattern)
                    elif decl.init.type == 'ObjectExpression':
                        if hasattr(decl.init, 'properties'):
                            obj_details = {
                                "type": "object",
                                "properties": set(),
                                "methods": set()
                            }
                            
                            for prop in decl.init.properties:
                                if hasattr(prop, 'key') and hasattr(prop.key, 'name'):
                                    prop_name = prop.key.name
                                    
                                    if hasattr(prop, 'value') and hasattr(prop.value, 'type'):
                                        # Method in object
                                        if prop.value.type in ['FunctionExpression', 'ArrowFunctionExpression']:
                                            obj_details["methods"].add(prop_name)
                                            # Also add as a separate function
                                            method_name = f"{var_name}.{prop_name}"
                                            func_details = self._get_function_details_esprima(prop.value)
                                            func_details["signature"] = f"{method_name}{func_details.get('signature', '()')}"
                                            nodes[f"func:{method_name}"] = func_details
                                        else:
                                            obj_details["properties"].add(prop_name)
                            
                            nodes[f"obj:{var_name}"] = obj_details
                
                # Object/array destructuring pattern
                elif hasattr(decl.id, 'type') and decl.id.type in ['ObjectPattern', 'ArrayPattern']:
                    self._process_destructuring_pattern(decl.id, decl.init, nodes)
    
    def _extract_dependencies_esprima(self, node, dependencies: set):
        """Extract dependencies using esprima AST."""
        if hasattr(node, 'type'):
            if node.type == 'ImportDeclaration':
                if hasattr(node, 'source') and node.source:
                    dependencies.add(node.source.value)
            
            elif node.type == 'CallExpression':
                # Handle require() calls
                if (hasattr(node, 'callee') and 
                    hasattr(node.callee, 'name') and 
                    node.callee.name == 'require'):
                    if (hasattr(node, 'arguments') and 
                        len(node.arguments) > 0 and 
                        hasattr(node.arguments[0], 'value')):
                        dependencies.add(node.arguments[0].value)
        
        # Recursively process children
        for key, value in vars(node).items():
            if isinstance(value, list):
                for item in value:
                    if hasattr(item, 'type'):
                        self._extract_dependencies_esprima(item, dependencies)
            elif hasattr(value, 'type'):
                self._extract_dependencies_esprima(value, dependencies)
    
    def _get_function_details_esprima(self, node) -> dict:
        """Get detailed function information from esprima node."""
        details = {
            "type": "function",
            "is_async": getattr(node, 'isAsync', False) or getattr(node, 'async', False),
            "is_generator": getattr(node, 'generator', False),
            "has_defaults": False,  # Initialize default parameter flag
            "has_destructuring": False,  # Initialize destructuring flag
            "is_arrow_function": node.type == 'ArrowFunctionExpression' if hasattr(node, 'type') else False,
            "functional_programming": node.type == 'ArrowFunctionExpression' if hasattr(node, 'type') else False
        }
        
        # Extract parameters
        if hasattr(node, 'params'):
            params = []
            param_sources = []  # Store parameter representations including defaults
            has_defaults = False
            has_destructuring = False
            
            for param in node.params:
                param_name = None
                param_source = None  # Full parameter representation
                
                # Basic parameter name
                if hasattr(param, 'name'):
                    param_name = param.name
                    param_source = param_name
                    params.append(param_name)
                    param_sources.append(param_source)
                
                # Check param type for destructuring patterns
                elif hasattr(param, 'type'):
                    # ES6 destructuring (object pattern)
                    if param.type == 'ObjectPattern':
                        has_destructuring = True
                        if hasattr(param, 'properties'):
                            for prop in param.properties:
                                if hasattr(prop, 'key') and hasattr(prop.key, 'name'):
                                    param_name = f"{{{prop.key.name}}}"
                                    params.append(param_name)
                                    param_sources.append(param_name)
                    
                    # ES6 destructuring (array pattern)
                    elif param.type == 'ArrayPattern':
                        has_destructuring = True
                        if hasattr(param, 'elements'):
                            for i, elem in enumerate(param.elements):
                                if elem and hasattr(elem, 'name'):
                                    param_name = f"[{elem.name}]"
                                    params.append(param_name)
                                    param_sources.append(param_name)
                    
                    # Check for default parameters (ES6 style)
                    elif param.type == 'AssignmentPattern':
                        has_defaults = True
                        # Get the parameter name from the left side
                        if hasattr(param, 'left') and hasattr(param.left, 'name'):
                            param_name = param.left.name
                            # Try to extract default value representation
                            default_repr = "defaultValue"
                            if hasattr(param, 'right'):
                                if hasattr(param.right, 'value'):
                                    if isinstance(param.right.value, str):
                                        default_repr = f"'{param.right.value}'"
                                    else:
                                        default_repr = str(param.right.value)
                                elif hasattr(param.right, 'name'):
                                    default_repr = param.right.name
                                elif hasattr(param.right, 'type'):
                                    if param.right.type == 'ObjectExpression':
                                        default_repr = "{...}"
                                    elif param.right.type == 'ArrayExpression':
                                        default_repr = "[...]"
                                    elif param.right.type == 'Literal':
                                        if hasattr(param.right, 'raw'):
                                            default_repr = param.right.raw
                            
                            param_source = f"{param_name} = {default_repr}"
                            if param_name:
                                params.append(param_name)
                                param_sources.append(param_source)
                
                # Check for object param with default (ES6) - only for AssignmentPattern
                if hasattr(param, 'right') and hasattr(param, 'type') and param.type == 'AssignmentPattern':
                    has_defaults = True
            
            details["parameters"] = [p for p in params if p is not None]
            details["parameter_sources"] = param_sources  # Store full parameter representations
            details["has_defaults"] = has_defaults
            details["has_destructuring"] = has_destructuring
            
            # Calculate function signature
            param_names = [p for p in params if p is not None]
            param_str = ", ".join(param_names)
            details["signature"] = f"({param_str})"
            
            # Enhance functional programming detection
            if details["is_arrow_function"]:
                details["functional_programming"] = True
            
            # Additional functional programming indicators from function body
            if hasattr(node, 'body'):
                body_str = str(node.body)
                if any(fp_pattern in body_str for fp_pattern in 
                       ['.map(', '.filter(', '.reduce(', '.forEach(', '.some(', '.every(']):
                    details["functional_programming"] = True
        
        # Extract actual source code from the original source
        if hasattr(node, 'range') and hasattr(node, 'loc'):
            # If we have range information, we could extract actual source
            # For now, construct a representative source with parameters
            func_name = getattr(node.id, 'name', 'anonymous') if hasattr(node, 'id') and node.id else 'anonymous'
            
            # Use parameter_sources if available, otherwise use param names
            if details.get("parameter_sources"):
                # Filter out None values before joining
                param_sources_filtered = [ps for ps in details["parameter_sources"] if ps is not None]
                param_str = ", ".join(param_sources_filtered)
            else:
                param_names = [p for p in details["parameters"] if p is not None]
                param_str = ", ".join(param_names)
            
            # Include async/generator markers
            prefix = ""
            if details.get("is_async"):
                prefix = "async "
            if details.get("is_generator"):
                prefix += "function* " if not prefix else "function* "
            else:
                prefix += "function "
            
            details["source"] = f"{prefix}{func_name}({param_str}) {{}}"
        else:
            details["source"] = f"function {getattr(node.id, 'name', 'anonymous') if hasattr(node, 'id') and node.id else 'anonymous'}() {{}}"
        
        # Extract exception handling information
        exception_handlers = set()
        catch_types = set()
        has_try_catch = False
        
        # Extract try-catch blocks from function body
        if hasattr(node, 'body'):
            try_catch_info = self._extract_exception_handling_esprima(node.body)
            exception_handlers = try_catch_info.get("exception_handlers", set())
            catch_types = try_catch_info.get("catch_types", set())
            has_try_catch = try_catch_info.get("has_try_catch", False)
        
        details["exception_handlers"] = exception_handlers
        details["exception_handling"] = {
            "has_try_catch": has_try_catch,
            "catch_types": catch_types
        }
        
        # Extract scope information (for global/nonlocal equivalent patterns)
        scope_info = self._extract_scope_patterns_esprima(node)
        details["global_statements"] = scope_info.get("global_statements", set())
        details["nonlocal_statements"] = scope_info.get("nonlocal_statements", set())
        
        return details
    
    def _get_class_details_esprima(self, node) -> dict:
        """Get detailed class information from esprima node."""
        details = {
            "type": "class",
            "base_classes": set(),
            "methods": set(),
            "static_methods": set(),
            "getters": set(),
            "setters": set(),
            "properties": set(),
            "static_properties": set(),
            "has_constructor": False,
            "has_defaults": False,
            "has_destructuring": False,
            "has_private_fields": False
        }
        
        # Extract superclass
        if hasattr(node, 'superClass') and node.superClass:
            if hasattr(node.superClass, 'name'):
                details["base_classes"].add(node.superClass.name)
        
        # Extract methods and properties
        if hasattr(node, 'body') and hasattr(node.body, 'body'):
            for member in node.body.body:
                if hasattr(member, 'type'):
                    # Handle method definitions
                    if member.type == 'MethodDefinition':
                        if hasattr(member, 'key') and hasattr(member.key, 'name'):
                            method_name = member.key.name
                            
                            # Check for method type
                            if hasattr(member, 'kind'):
                                if member.kind == 'constructor':
                                    details["has_constructor"] = True
                                    
                                    # Check constructor params for defaults
                                    if (hasattr(member, 'value') and hasattr(member.value, 'params')):
                                        for param in member.value.params:
                                            if hasattr(param, 'type') and param.type == 'AssignmentPattern':
                                                details["has_defaults"] = True
                                            if hasattr(param, 'type') and param.type in ['ObjectPattern', 'ArrayPattern']:
                                                details["has_destructuring"] = True
                                
                                elif member.kind == 'get':
                                    details["getters"].add(method_name)
                                elif member.kind == 'set':
                                    details["setters"].add(method_name)
                                else:
                                    # Regular method
                                    if hasattr(member, 'static') and member.static:
                                        details["static_methods"].add(method_name)
                                    else:
                                        details["methods"].add(method_name)
                    
                    # Handle class property definitions (ES Next)
                    elif member.type == 'PropertyDefinition':
                        if hasattr(member, 'key') and hasattr(member.key, 'name'):
                            prop_name = member.key.name
                            
                            # Check if it's a private field
                            if prop_name.startswith('#'):
                                details["has_private_fields"] = True
                                prop_name = prop_name[1:]  # Remove the # prefix
                            
                            if hasattr(member, 'static') and member.static:
                                details["static_properties"].add(prop_name)
                            else:
                                details["properties"].add(prop_name)
        
        # Combine all properties into attributes for behavioral analysis
        all_attributes = details["properties"] | details["static_properties"]
        details["attributes"] = all_attributes
        
        return details
    
    def _process_destructuring_pattern(self, pattern_node, init_node, nodes: dict):
        """Process a destructuring pattern in variable declarations."""
        if pattern_node.type == 'ObjectPattern':
            if hasattr(pattern_node, 'properties'):
                for prop in pattern_node.properties:
                    if hasattr(prop, 'key') and hasattr(prop.key, 'name'):
                        var_name = prop.key.name
                        
                        # Handle renaming via { key: newName }
                        if hasattr(prop, 'value') and hasattr(prop.value, 'name'):
                            var_name = prop.value.name
                        
                        # Add as a destructured variable
                        nodes[f"var:{var_name}"] = {
                            "type": "variable",
                            "source": f"{var_name} (destructured)",
                            "is_destructured": True,
                            "from_object": True
                        }
        
        elif pattern_node.type == 'ArrayPattern':
            if hasattr(pattern_node, 'elements'):
                for i, elem in enumerate(pattern_node.elements):
                    if elem and hasattr(elem, 'name'):
                        var_name = elem.name
                        
                        # Add as a destructured variable
                        nodes[f"var:{var_name}"] = {
                            "type": "variable",
                            "source": f"{var_name} (destructured)",
                            "is_destructured": True,
                            "from_array": True,
                            "array_index": i
                        }
    
    def _detect_functional_programming(self, code: str, nodes: dict) -> None:
        """Detect functional programming patterns in JavaScript code."""
        # Look for higher-order function usage - more inclusive patterns
        fp_patterns = {
            "map": r'\.map\s*\(',
            "filter": r'\.filter\s*\(',
            "reduce": r'\.reduce\s*\(',
            "forEach": r'\.forEach\s*\(',
            "find": r'\.find\s*\(',
            "every": r'\.every\s*\(',
            "some": r'\.some\s*\(',
            "arrow_functions": r'\w+\s*=>\s*',
            "arrow_functions_param": r'\([^)]*\)\s*=>\s*',
            "currying": r'(?:return\s+function|=>\s*\([^)]*\)\s*=>)',
            "compose": r'(?:compose|pipe)\s*\(',
            "spread_operator": r'\.\.\.', # Spread for immutability
        }
        
        # Check for functional programming patterns in the code
        fp_usage = {}
        for pattern_name, pattern in fp_patterns.items():
            matches = re.findall(pattern, code)
            if matches:
                fp_usage[pattern_name] = len(matches)
        
        # If functional programming patterns are detected, mark relevant nodes
        if fp_usage:
            for node_id, node in nodes.items():
                if node.get("type") == "function":
                    # Update existing functions with functional programming info
                    source = node.get("source", "")
                    for fp_pattern in fp_patterns.keys():
                        if fp_pattern in source.lower() or any(re.search(fp_patterns[fp_pattern], source) for _ in [None]):
                            node["functional_programming"] = True
                            if "fp_patterns" not in node:
                                node["fp_patterns"] = {}
                            node["fp_patterns"][fp_pattern] = fp_usage.get(fp_pattern, 0)
            
            # Create a special node to track overall functional programming usage
            nodes["meta:functional_programming"] = {
                "type": "meta",
                "fp_usage": fp_usage,
                "fp_score": sum(fp_usage.values()),
                "is_functional": sum(fp_usage.values()) > 2  # Threshold for considering code functional
            }
    
    def _extract_behavioral_patterns(self, code: str, nodes: dict) -> None:
        """Extract detailed behavioral patterns that Layer 4 needs."""
        
        # Extract assignment patterns
        assignment_patterns = set()
        assignment_targets = set()  # Add assignment targets tracking
        augmented_assignments = set()
        
        # Regular assignments
        assign_pattern = r'(\w+)\s*=\s*([^=;]+)'
        for match in re.finditer(assign_pattern, code):
            if not re.search(r'[!=<>]=', match.group(0)):  # Not comparison
                target = match.group(1)
                assignment_patterns.add(target)
                assignment_targets.add(target)  # Track assignment targets separately
        
        # Augmented assignments
        aug_assign_patterns = [
            (r'(\w+)\s*\+=', '+='),
            (r'(\w+)\s*-=', '-='),
            (r'(\w+)\s*\*=', '*='),
            (r'(\w+)\s*/=', '/='),
            (r'(\w+)\s*%=', '%='),
            (r'(\w+)\s*\*\*=', '**='),
            (r'(\w+)\s*&=', '&='),
            (r'(\w+)\s*\|=', '|='),
            (r'(\w+)\s*\^=', '^='),
            (r'(\w+)\s*<<=', '<<='),
            (r'(\w+)\s*>>=', '>>=')
        ]
        
        for pattern, op in aug_assign_patterns:
            if re.search(pattern, code):
                augmented_assignments.add(op)
        
        # Extract operators
        binary_operators = set()
        unary_operators = set()
        comparison_operators = set()
        logical_operators = set()
        
        # Binary operators
        binary_ops = [
            (r'\+(?!=)', 'Add'),
            (r'-(?!=)', 'Sub'),
            (r'\*(?!=)', 'Mult'),
            (r'/(?!=)', 'Div'),
            (r'%(?!=)', 'Mod'),
            (r'\*\*(?!=)', 'Pow'),
            (r'&(?!=)', 'BitAnd'),
            (r'\|(?!=)', 'BitOr'),
            (r'\^(?!=)', 'BitXor'),
            (r'<<(?!=)', 'LShift'),
            (r'>>(?!=)', 'RShift')
        ]
        
        for pattern, op_name in binary_ops:
            if re.search(pattern, code):
                binary_operators.add(op_name)
        
        # Unary operators
        unary_ops = [
            (r'\+\+', 'UAdd'),
            (r'--', 'USub'),
            (r'!(?!=)', 'Not'),
            (r'~', 'Invert'),
            (r'typeof\s+', 'Typeof'),
            (r'delete\s+', 'Delete')
        ]
        
        for pattern, op_name in unary_ops:
            if re.search(pattern, code):
                unary_operators.add(op_name)
        
        # Comparison operators
        comp_ops = [
            (r'===', 'Eq'),
            (r'!==', 'NotEq'),
            (r'==', 'Eq'),
            (r'!=', 'NotEq'),
            (r'<=', 'LtE'),
            (r'>=', 'GtE'),
            (r'<(?!=)', 'Lt'),
            (r'>(?!=)', 'Gt'),
            (r'instanceof\s+', 'Is'),
            (r'in\s+', 'In')
        ]
        
        for pattern, op_name in comp_ops:
            if re.search(pattern, code):
                comparison_operators.add(op_name)
        
        # Logical operators
        logical_ops = [
            (r'&&', 'And'),
            (r'\|\|', 'Or'),
            (r'!(?!=)', 'Not')
        ]
        
        for pattern, op_name in logical_ops:
            if re.search(pattern, code):
                logical_operators.add(op_name)
        
        # Extract literals
        string_literals = set()
        numeric_literals = set()
        boolean_literals = set()
        
        # String literals
        string_patterns = [
            r"'([^'\\\\]|\\\\.)*'",  # Single quotes
            r'"([^"\\\\]|\\\\.)*"',  # Double quotes
            r'`([^`\\\\]|\\\\.)*`'   # Template literals
        ]
        
        for pattern in string_patterns:
            matches = re.findall(pattern, code)
            string_literals.update(matches)
        
        # Numeric literals
        numeric_patterns = [
            r'\b\d+\.?\d*([eE][+-]?\d+)?\b',  # Numbers
            r'\b0x[0-9a-fA-F]+\b',           # Hex
            r'\b0b[01]+\b',                   # Binary
            r'\b0o[0-7]+\b'                   # Octal
        ]
        
        for pattern in numeric_patterns:
            matches = re.findall(pattern, code)
            numeric_literals.update(matches)
        
        # Boolean literals
        if re.search(r'\btrue\b', code):
            boolean_literals.add('true')
        if re.search(r'\bfalse\b', code):
            boolean_literals.add('false')
        if re.search(r'\bnull\b', code):
            boolean_literals.add('null')
        if re.search(r'\bundefined\b', code):
            boolean_literals.add('undefined')
        
        # Extract attribute and subscript access
        attribute_access = set()
        subscript_access = set()
        
        # Attribute access (dot notation)
        attr_pattern = r'(\w+)\s*\.\s*(\w+)'
        for match in re.finditer(attr_pattern, code):
            if match.lastindex == 2:
                obj_name = match.group(1)
                attr_name = match.group(2)
                attribute_access.add(f"{obj_name}.{attr_name}")
        
        # Subscript access (bracket notation)
        subscript_pattern = r'(\w+)\s*\[\s*([^]]+)\s*\]'
        for match in re.finditer(subscript_pattern, code):
            if match.lastindex == 2:
                obj_name = match.group(1)
                index_expr = match.group(2)
                subscript_access.add(f"{obj_name}[{index_expr}]")
        
        # Extract control flow patterns
        control_flow = set()
        if re.search(r'\bif\s*\(', code):
            control_flow.add('if')
        if re.search(r'\bfor\s*\(', code):
            control_flow.add('for')
        if re.search(r'\bwhile\s*\(', code):
            control_flow.add('while')
        if re.search(r'\bswitch\s*\(', code):
            control_flow.add('switch')
        if re.search(r'\bcatch\s*\(', code):
            control_flow.add('catch')
        
        # Extract function call patterns
        internal_calls = set()
        call_pattern = r'(\w+)\s*\('
        for match in re.finditer(call_pattern, code):
            func_name = match.group(1)
            # Filter out keywords
            if func_name not in ['if', 'for', 'while', 'switch', 'catch', 'function', 'class', 'return']:
                internal_calls.add(func_name)
        
        # Extract return patterns
        return_count = len(re.findall(r'\breturn\b', code))
        yield_count = len(re.findall(r'\byield\b', code))
        
        # Extract assertion patterns (console.assert, assert, etc.)
        assert_patterns = [
            r'console\.assert\s*\(',  # console.assert(...)
            r'\bassert\s*\(',         # assert(...)
        ]
        assert_count = 0
        for pattern in assert_patterns:
            assert_count += len(re.findall(pattern, code))
        
        # Add behavioral patterns to all function and class nodes
        behavioral_data = {
            "assignment_patterns": assignment_patterns,
            "assignment_targets": assignment_targets,  # Add assignment targets
            "augmented_assignments": augmented_assignments,
            "binary_operators": binary_operators,
            "unary_operators": unary_operators,
            "comparison_operators": comparison_operators,
            "logical_operators": logical_operators,
            "string_literals": string_literals,
            "numeric_literals": numeric_literals,
            "boolean_literals": boolean_literals,
            "attribute_access": attribute_access,
            "subscript_access": subscript_access,
            "control_flow": {"if": 1 if "if" in control_flow else 0,
                            "for": 1 if "for" in control_flow else 0,
                            "while": 1 if "while" in control_flow else 0,
                            "switch": 1 if "switch" in control_flow else 0},
            "calls": internal_calls,
            "return_count": return_count,
            "yield_count": yield_count,
            # Also provide the expected field names for layer consistency
            "return_statements": return_count,
            "yield_statements": yield_count,
            "assert_statements": assert_count
        }
        
        # Add behavioral data to all nodes
        for node_id, node_data in nodes.items():
            if node_data.get("type") in ["function", "class", "method"]:
                node_data.update(behavioral_data)
        
        # Also create a special behavioral analysis node
        nodes["behavioral:patterns"] = {
            "type": "behavioral",
            **behavioral_data
        }
    
    def _extract_exception_handling_esprima(self, body_node) -> dict:
        """Extract exception handling information from esprima AST."""
        exception_handlers = set()
        catch_types = set()
        has_try_catch = False
        
        def traverse_for_try_catch(node):
            nonlocal exception_handlers, catch_types, has_try_catch
            
            if hasattr(node, 'type'):
                if node.type == 'TryStatement':
                    has_try_catch = True
                    
                    # Extract catch clause information
                    if hasattr(node, 'handler') and node.handler:
                        # In modern JS, catch clause can be: catch (error) or catch (error: Type)
                        if hasattr(node.handler, 'param') and node.handler.param:
                            param = node.handler.param
                            if hasattr(param, 'name'):
                                exception_handlers.add(param.name)
                            
                            # Look for type annotations or error type checks in catch body
                            if hasattr(node.handler, 'body') and hasattr(node.handler.body, 'body'):
                                for stmt in node.handler.body.body:
                                    # Look for instanceof checks
                                    error_types = self._extract_error_types_from_statement(stmt)
                                    catch_types.update(error_types)
                    
                    # If no specific types found, add generic error
                    if not catch_types and has_try_catch:
                        catch_types.add("Error")
            
            # Recursively traverse child nodes
            if hasattr(node, '__dict__'):
                for attr_name, attr_value in node.__dict__.items():
                    if isinstance(attr_value, list):
                        for item in attr_value:
                            if hasattr(item, 'type'):
                                traverse_for_try_catch(item)
                    elif hasattr(attr_value, 'type'):
                        traverse_for_try_catch(attr_value)
        
        traverse_for_try_catch(body_node)
        
        return {
            "exception_handlers": exception_handlers,
            "catch_types": catch_types,
            "has_try_catch": has_try_catch
        }
    
    def _extract_error_types_from_statement(self, stmt) -> set:
        """Extract error types from catch statement."""
        error_types = set()
        
        # Convert statement to string and look for common error type patterns
        stmt_str = str(stmt)
        
        # Common JavaScript error types
        js_error_types = [
            'Error', 'TypeError', 'ReferenceError', 'SyntaxError', 'RangeError',
            'EvalError', 'URIError', 'AggregateError', 'InternalError',
            'ValidationError', 'AuthenticationError', 'NetworkError', 'CustomError'
        ]
        
        for error_type in js_error_types:
            if error_type in stmt_str:
                error_types.add(error_type)
        
        return error_types
    
    def _extract_scope_patterns_esprima(self, node) -> dict:
        """Extract scope-related patterns from esprima AST."""
        global_statements = set()
        nonlocal_statements = set()
        
        def traverse_for_scope(node):
            nonlocal global_statements, nonlocal_statements
            
            if hasattr(node, 'type'):
                # Look for variable declarations at global scope
                if node.type == 'VariableDeclaration':
                    if hasattr(node, 'declarations'):
                        for decl in node.declarations:
                            if hasattr(decl, 'id') and hasattr(decl.id, 'name'):
                                var_name = decl.id.name
                                # Check if it's declared with 'var' (more global-like)
                                if hasattr(node, 'kind') and node.kind == 'var':
                                    global_statements.add(var_name)
                
                # Look for assignments to global objects (window, global, this at top level)
                elif node.type == 'AssignmentExpression':
                    if hasattr(node, 'left') and hasattr(node.left, 'object'):
                        obj = node.left.object
                        if hasattr(obj, 'name') and obj.name in ['window', 'global', 'globalThis']:
                            if hasattr(node.left, 'property') and hasattr(node.left.property, 'name'):
                                global_statements.add(node.left.property.name)
                
                # Look for closure patterns that modify outer scope
                elif node.type == 'MemberExpression':
                    if hasattr(node, 'object') and hasattr(node.object, 'type'):
                        if node.object.type == 'ThisExpression':
                            if hasattr(node, 'property') and hasattr(node.property, 'name'):
                                nonlocal_statements.add(node.property.name)
            
            # Recursively traverse child nodes
            if hasattr(node, '__dict__'):
                for attr_name, attr_value in node.__dict__.items():
                    if isinstance(attr_value, list):
                        for item in attr_value:
                            if hasattr(item, 'type'):
                                traverse_for_scope(item)
                    elif hasattr(attr_value, 'type'):
                        traverse_for_scope(attr_value)
        
        traverse_for_scope(node)
        
        return {
            "global_statements": global_statements,
            "nonlocal_statements": nonlocal_statements
        }
    
    def _extract_exception_handling_regex(self, function_source: str) -> dict:
        """Extract exception handling information using regex patterns."""
        exception_handlers = set()
        catch_types = set()
        has_try_catch = False
        
        # Check for try-catch blocks
        try_pattern = r'\btry\s*\{'
        catch_pattern = r'\bcatch\s*\(\s*(\w+)\s*\)\s*\{'
        catch_typed_pattern = r'\bcatch\s*\(\s*(\w+)\s*:\s*(\w+)\s*\)\s*\{'
        
        if re.search(try_pattern, function_source):
            has_try_catch = True
        
        # Extract catch parameter names
        for match in re.finditer(catch_pattern, function_source):
            exception_handlers.add(match.group(1))
        
        # Extract typed catch blocks (TypeScript style)
        for match in re.finditer(catch_typed_pattern, function_source):
            exception_handlers.add(match.group(1))
            catch_types.add(match.group(2))
        
        # Look for error type patterns in catch blocks
        error_type_patterns = [
            r'\bif\s*\(\s*\w+\s+instanceof\s+(\w+Error?)\s*\)',
            r'\b(\w+Error?)\b(?=\s*[:\(])',
            r'throw\s+new\s+(\w+Error?)\s*\(',
            r'console\.error.*?(\w+Error?)',
        ]
        
        for pattern in error_type_patterns:
            for match in re.finditer(pattern, function_source):
                catch_types.add(match.group(1))
        
        # Default to generic Error if we have try-catch but no specific types
        if has_try_catch and not catch_types:
            catch_types.add("Error")
        
        return {
            "exception_handlers": exception_handlers,
            "catch_types": catch_types,
            "has_try_catch": has_try_catch
        }
    
    def _extract_scope_patterns_regex(self, function_source: str) -> dict:
        """Extract scope patterns using regex."""
        global_statements = set()
        nonlocal_statements = set()
        
        # Look for global variable patterns
        global_patterns = [
            r'\bwindow\.(\w+)\s*=',  # window.variable = 
            r'\bglobal\.(\w+)\s*=',  # global.variable =
            r'\bglobalThis\.(\w+)\s*=',  # globalThis.variable =
            r'\bvar\s+(\w+)\s*(?=;|=)',  # var declarations (more global-like)
        ]
        
        for pattern in global_patterns:
            for match in re.finditer(pattern, function_source):
                global_statements.add(match.group(1))
        
        # Look for closure/nonlocal patterns
        nonlocal_patterns = [
            r'\bthis\.(\w+)\s*=',  # this.variable = (accessing outer scope)
            r'(?:^|\s)(\w+)\s*=.*?(?=;|\n|$)',  # variable assignment without declaration
        ]
        
        for pattern in nonlocal_patterns:
            for match in re.finditer(pattern, function_source, re.MULTILINE):
                var_name = match.group(1)
                # Exclude common keywords and built-ins
                if var_name not in ['var', 'let', 'const', 'function', 'class', 'if', 'for', 'while', 'return']:
                    nonlocal_statements.add(var_name)
        
        return {
            "global_statements": global_statements,
            "nonlocal_statements": nonlocal_statements
        }
    
    def get_node_details(self, node) -> Dict[str, Any]:
        """Get details for a parsed node."""
        if isinstance(node, dict):
            return node
        return {"source": str(node), "type": "unknown"}

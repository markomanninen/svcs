# SVCS PHP Parser
# Comprehensive PHP parser with fallback strategies

import re
from typing import Dict, Set, List, Any
from .base_parser import BaseParser

# Try to import tree-sitter for modern PHP parsing
try:
    import tree_sitter
    import tree_sitter_php
    tree_sitter_available = True
    php_language = tree_sitter.Language(tree_sitter_php.language_php())
except ImportError:
    tree_sitter_available = False
except Exception as e:
    print(f"Warning: Tree-sitter PHP setup failed: {e}")
    tree_sitter_available = False

# Try to import phply for legacy PHP parsing
try:
    from phply import phplex, phpparse, phpast
    phply_available = True
except ImportError:
    phply_available = False

class PHPParser(BaseParser):
    """PHP parser with tree-sitter and phply fallbacks."""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = {'.php', '.phtml', '.php3', '.php4', '.php5', '.phps'}
        self.language_name = "PHP"
    
    def parse_code(self, source_code: str) -> tuple:
        """Parse PHP code using available parsers."""
        if tree_sitter_available:
            return self._parse_with_tree_sitter(source_code)
        elif phply_available:
            return self._parse_with_phply(source_code)
        else:
            return self._parse_with_regex(source_code)
    
    def _parse_with_tree_sitter(self, source_code: str) -> tuple:
        """Parse PHP using tree-sitter (modern PHP 7.4+ and 8.x)."""
        nodes = {}
        dependencies = set()
        
        try:
            parser = tree_sitter.Parser()
            parser.language = php_language
            tree = parser.parse(source_code.encode('utf-8'))
            
            # Extract functions and classes
            self._extract_nodes_tree_sitter(tree.root_node, nodes, source_code)
            
            # Extract dependencies (use/require statements)
            self._extract_dependencies_tree_sitter(tree.root_node, dependencies, source_code)
            
            # Extract exception handling information
            self._extract_exception_handling_tree_sitter(tree.root_node, nodes, source_code)
            
        except Exception as e:
            print(f"Warning: Tree-sitter PHP parsing failed: {e}")
            return self._parse_with_regex(source_code)
        
        return nodes, dependencies
    
    def _parse_with_phply(self, source_code: str) -> tuple:
        """Parse PHP using phply (legacy PHP 5.x-7.3)."""
        nodes = {}
        dependencies = set()
        
        try:
            lexer = phplex.lexer
            parser = phpparse.make_parser()
            ast_tree = parser.parse(source_code, lexer=lexer)
            
            # Extract functions and classes from AST
            self._extract_nodes_phply(ast_tree, nodes)
            
            # Extract dependencies
            self._extract_dependencies_phply(ast_tree, dependencies)
            
        except Exception as e:
            print(f"Warning: phply PHP parsing failed: {e}")
            return self._parse_with_regex(source_code)
        
        return nodes, dependencies
    
    def _parse_with_regex(self, source_code: str) -> tuple:
        """Fallback PHP parsing using regex patterns."""
        nodes = {}
        dependencies = set()
        
        # Extract functions
        function_pattern = r'function\s+(\w+)\s*\([^)]*\)'
        for match in re.finditer(function_pattern, source_code, re.IGNORECASE):
            func_name = match.group(1)
            nodes[f"func:{func_name}"] = {
                "source": match.group(0),
                "signature": match.group(0),
                "type": "function"
            }
        
        # Extract classes
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?'
        for match in re.finditer(class_pattern, source_code, re.IGNORECASE):
            class_name = match.group(1)
            extends = match.group(2)
            implements = match.group(3)
            
            details = {
                "source": match.group(0),
                "type": "class",
                "base_classes": {extends} if extends else set(),
                "interfaces": set(impl.strip() for impl in implements.split(',')) if implements else set()
            }
            nodes[f"class:{class_name}"] = details
        
        # Extract namespace and use statements
        namespace_pattern = r'namespace\s+([^;]+);'
        use_pattern = r'use\s+([^;]+);'
        
        for match in re.finditer(use_pattern, source_code, re.IGNORECASE):
            dependencies.add(match.group(1).strip())
        
        return nodes, dependencies
    
    def _extract_nodes_tree_sitter(self, node, nodes: dict, source_code: str):
        """Extract nodes using tree-sitter."""
        if node.type == 'function_definition':
            func_name = self._get_node_text(node.child_by_field_name('name'), source_code)
            if func_name:
                nodes[f"func:{func_name}"] = self._get_function_details_tree_sitter(node, source_code)
        
        elif node.type == 'class_declaration':
            class_name = self._get_node_text(node.child_by_field_name('name'), source_code)
            if class_name:
                nodes[f"class:{class_name}"] = self._get_class_details_tree_sitter(node, source_code)
        
        # Recursively process children
        for child in node.children:
            self._extract_nodes_tree_sitter(child, nodes, source_code)
    
    def _extract_dependencies_tree_sitter(self, node, dependencies: set, source_code: str):
        """Extract dependencies using tree-sitter."""
        if node.type == 'use_declaration':
            use_text = self._get_node_text(node, source_code)
            if use_text:
                dependencies.add(use_text)
        
        # Recursively process children
        for child in node.children:
            self._extract_dependencies_tree_sitter(child, dependencies, source_code)
    
    def _get_node_text(self, node, source_code: str) -> str:
        """Get text content of a tree-sitter node."""
        if node:
            return source_code[node.start_byte:node.end_byte]
        return ""
    
    def _get_function_details_tree_sitter(self, node, source_code: str) -> dict:
        """Get detailed function information from tree-sitter node."""
        return {
            "source": self._get_node_text(node, source_code),
            "type": "function",
            "visibility": self._extract_visibility(node, source_code),
            "is_static": self._is_static(node, source_code),
            "parameters": self._extract_parameters(node, source_code)
        }
    
    def _get_class_details_tree_sitter(self, node, source_code: str) -> dict:
        """Get detailed class information from tree-sitter node."""
        return {
            "source": self._get_node_text(node, source_code),
            "type": "class",
            "base_classes": self._extract_base_classes(node, source_code),
            "interfaces": self._extract_interfaces(node, source_code),
            "methods": self._extract_methods(node, source_code),
            "properties": self._extract_properties(node, source_code)
        }
    
    def _extract_nodes_phply(self, ast_node, nodes: dict):
        """Extract nodes using phply AST."""
        if hasattr(ast_node, 'nodes'):
            for child in ast_node.nodes:
                self._extract_nodes_phply(child, nodes)
        
        if hasattr(ast_node, '__class__'):
            if ast_node.__class__.__name__ == 'Function':
                nodes[f"func:{ast_node.name}"] = {
                    "source": str(ast_node),
                    "type": "function",
                    "name": ast_node.name
                }
            elif ast_node.__class__.__name__ == 'Class':
                nodes[f"class:{ast_node.name}"] = {
                    "source": str(ast_node),
                    "type": "class",
                    "name": ast_node.name
                }
    
    def _extract_dependencies_phply(self, ast_node, dependencies: set):
        """Extract dependencies using phply AST."""
        # Implementation for phply dependency extraction
        pass
    
    def _extract_visibility(self, node, source_code: str) -> str:
        """Extract visibility modifier (public, private, protected)."""
        text = self._get_node_text(node, source_code)
        if 'private' in text:
            return 'private'
        elif 'protected' in text:
            return 'protected'
        return 'public'
    
    def _is_static(self, node, source_code: str) -> bool:
        """Check if function/method is static."""
        return 'static' in self._get_node_text(node, source_code)
    
    def _extract_parameters(self, node, source_code: str) -> list:
        """Extract function parameters."""
        # Simplified parameter extraction
        return []
    
    def _extract_base_classes(self, node, source_code: str) -> set:
        """Extract base classes for inheritance."""
        return set()
    
    def _extract_interfaces(self, node, source_code: str) -> set:
        """Extract implemented interfaces."""
        return set()
    
    def _extract_methods(self, node, source_code: str) -> set:
        """Extract class methods."""
        return set()
    
    def _extract_properties(self, node, source_code: str) -> set:
        """Extract class properties."""
        return set()
    
    def get_node_details(self, node) -> Dict[str, Any]:
        """Get details for a parsed node."""
        if isinstance(node, dict):
            return node
        return {"source": str(node), "type": "unknown"}

    def _extract_exception_handling_tree_sitter(self, node, nodes, source_code):
        """Extract exception handling information from tree-sitter node."""
        self._process_node_for_exceptions(node, nodes, source_code)
    
    def _process_node_for_exceptions(self, node, nodes, source_code):
        """Process a node and its children for exception handling constructs."""
        # Check if this is a try statement
        if hasattr(node, 'type') and node.type == 'try_statement':
            # Find the containing function/method for this try block
            containing_node_id = self._find_containing_node(node, nodes, source_code)
            
            if containing_node_id:
                if 'exception_handling' not in nodes[containing_node_id]:
                    nodes[containing_node_id]['exception_handling'] = {
                        'has_try_catch': True,
                        'catch_types': set(),
                        'has_finally': False
                    }
                
                # Find catch blocks and extract exception types
                for child in node.children:
                    if child.type == 'catch_clause':
                        for catch_child in child.children:
                            if catch_child.type == 'name':
                                exception_type = source_code[catch_child.start_byte:catch_child.end_byte].decode('utf-8')
                                nodes[containing_node_id]['exception_handling']['catch_types'].add(exception_type)
                    
                    elif child.type == 'finally_clause':
                        nodes[containing_node_id]['exception_handling']['has_finally'] = True
        
        # Check if this is a throw statement
        elif hasattr(node, 'type') and node.type == 'throw_statement':
            containing_node_id = self._find_containing_node(node, nodes, source_code)
            
            if containing_node_id:
                if 'exception_handling' not in nodes[containing_node_id]:
                    nodes[containing_node_id]['exception_handling'] = {
                        'has_try_catch': False,
                        'catch_types': set(),
                        'has_finally': False
                    }
                
                nodes[containing_node_id]['exception_handling']['has_throw'] = True
        
        # Check if this is an exception class
        elif (hasattr(node, 'type') and node.type == 'class_declaration'):
            # Check if it extends Exception
            extends_exception = False
            for child in node.children:
                if child.type == 'extends_clause':
                    for extends_child in child.children:
                        if extends_child.type == 'name':
                            base = source_code[extends_child.start_byte:extends_child.end_byte].decode('utf-8')
                            if 'Exception' in base:
                                extends_exception = True
            
            if extends_exception:
                # Extract the class name
                for child in node.children:
                    if child.type == 'name':
                        class_name = source_code[child.start_byte:child.end_byte].decode('utf-8')
                        node_id = f"class:{class_name}"
                        
                        if node_id in nodes:
                            nodes[node_id]['is_exception_class'] = True
        
        # Recursively process children
        if hasattr(node, 'children'):
            for child in node.children:
                self._process_node_for_exceptions(child, nodes, source_code)
    
    def _find_containing_node(self, node, nodes, source_code):
        """Find the node ID of the function/method containing this AST node."""
        # Simple implementation - would need to be enhanced with proper scope tracking
        for node_id, details in nodes.items():
            if node_id.startswith('func:') or node_id.startswith('method:'):
                # For demonstration purposes only - this is simplified
                # A real implementation would need to check if the node is within the scope of this function
                return node_id
        
        return None

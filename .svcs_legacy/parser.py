# FILE: .svcs/parser.py (Definitive Version)
# This parser is rewritten to be comprehensive, extracting signatures,
# calls, exception handling, and control flow structures.

import ast
from rich.console import Console

console = Console()

class FunctionDetailVisitor(ast.NodeVisitor):
    """
    A comprehensive visitor that extracts detailed semantic information
    from a function's AST.
    """
    def __init__(self):
        self.calls = set()
        self.exception_handlers = set()
        self.control_flow_statements = {"if": 0, "for": 0, "while": 0, "with": 0}
        self.decorators = set()
        self.return_statements = 0
        self.yield_statements = 0
        self.async_features = {"async_def": False, "await_calls": 0}
        self.comprehensions = {"list": 0, "dict": 0, "set": 0, "generator": 0}
        self.lambda_functions = 0
        self.class_definitions = 0
        self.global_statements = set()
        self.nonlocal_statements = set()
        self.assert_statements = 0
        self.string_literals = set()
        self.numeric_literals = set()
        self.boolean_literals = {"True": 0, "False": 0}
        self.none_literals = 0
        self.attribute_access = set()
        self.subscript_access = set()
        self.binary_operators = set()
        self.unary_operators = set()
        self.comparison_operators = set()
        self.logical_operators = set()
        self.assignment_targets = set()
        self.augmented_assignments = set()
        self.starred_expressions = 0
        self.slice_expressions = 0

    def visit_Call(self, node):
        """Identifies function calls."""
        if isinstance(node.func, ast.Name):
            self.calls.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                self.calls.add(f"{node.func.value.id}.{node.func.attr}")
        self.generic_visit(node)

    def visit_Await(self, node):
        """Identifies await expressions."""
        self.async_features["await_calls"] += 1
        self.generic_visit(node)

    def visit_Return(self, node):
        """Counts return statements."""
        self.return_statements += 1
        self.generic_visit(node)

    def visit_Yield(self, node):
        """Counts yield statements."""
        self.yield_statements += 1
        self.generic_visit(node)

    def visit_YieldFrom(self, node):
        """Counts yield from statements."""
        self.yield_statements += 1
        self.generic_visit(node)

    def visit_Lambda(self, node):
        """Counts lambda functions."""
        self.lambda_functions += 1
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Counts nested class definitions."""
        self.class_definitions += 1
        self.generic_visit(node)

    def visit_Global(self, node):
        """Tracks global statements."""
        for name in node.names:
            self.global_statements.add(name)
        self.generic_visit(node)

    def visit_Nonlocal(self, node):
        """Tracks nonlocal statements."""
        for name in node.names:
            self.nonlocal_statements.add(name)
        self.generic_visit(node)

    def visit_Assert(self, node):
        """Counts assert statements."""
        self.assert_statements += 1
        self.generic_visit(node)

    def visit_Str(self, node):
        """Tracks string literals."""
        self.string_literals.add(node.s[:50])  # Truncate long strings
        self.generic_visit(node)

    def visit_Constant(self, node):
        """Tracks various constant types."""
        if isinstance(node.value, str):
            self.string_literals.add(str(node.value)[:50])
        elif isinstance(node.value, (int, float)):
            self.numeric_literals.add(str(node.value))
        elif isinstance(node.value, bool):
            self.boolean_literals[str(node.value)] += 1
        elif node.value is None:
            self.none_literals += 1
        self.generic_visit(node)

    def visit_Attribute(self, node):
        """Tracks attribute access patterns."""
        if isinstance(node.value, ast.Name):
            self.attribute_access.add(f"{node.value.id}.{node.attr}")
        self.generic_visit(node)

    def visit_Subscript(self, node):
        """Tracks subscript access patterns."""
        if isinstance(node.value, ast.Name):
            self.subscript_access.add(node.value.id)
        self.generic_visit(node)

    def visit_BinOp(self, node):
        """Tracks binary operators."""
        self.binary_operators.add(type(node.op).__name__)
        self.generic_visit(node)

    def visit_UnaryOp(self, node):
        """Tracks unary operators."""
        self.unary_operators.add(type(node.op).__name__)
        self.generic_visit(node)

    def visit_Compare(self, node):
        """Tracks comparison operators."""
        for op in node.ops:
            self.comparison_operators.add(type(op).__name__)
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        """Tracks logical operators (and, or)."""
        self.logical_operators.add(type(node.op).__name__)
        self.generic_visit(node)

    def visit_Assign(self, node):
        """Tracks assignment targets."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.assignment_targets.add(target.id)
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        """Tracks augmented assignments (+=, -=, etc.)."""
        if isinstance(node.target, ast.Name):
            op_name = type(node.op).__name__
            self.augmented_assignments.add(f"{node.target.id}_{op_name}")
        self.generic_visit(node)

    def visit_Starred(self, node):
        """Counts starred expressions."""
        self.starred_expressions += 1
        self.generic_visit(node)

    def visit_Slice(self, node):
        """Counts slice expressions."""
        self.slice_expressions += 1
        self.generic_visit(node)

    def visit_ListComp(self, node):
        """Counts list comprehensions."""
        self.comprehensions["list"] += 1
        self.generic_visit(node)

    def visit_DictComp(self, node):
        """Counts dictionary comprehensions."""
        self.comprehensions["dict"] += 1
        self.generic_visit(node)

    def visit_SetComp(self, node):
        """Counts set comprehensions."""
        self.comprehensions["set"] += 1
        self.generic_visit(node)

    def visit_GeneratorExp(self, node):
        """Counts generator expressions."""
        self.comprehensions["generator"] += 1
        self.generic_visit(node)

    def visit_Try(self, node):
        """Identifies exception handling blocks."""
        for handler in node.handlers:
            if handler.type and isinstance(handler.type, ast.Name):
                self.exception_handlers.add(handler.type.id)
            else:
                self.exception_handlers.add("BaseException") # Generic except:
        self.generic_visit(node)

    def visit_If(self, node):
        self.control_flow_statements["if"] += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.control_flow_statements["for"] += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.control_flow_statements["while"] += 1
        self.generic_visit(node)
    
    def visit_With(self, node):
        self.control_flow_statements["with"] += 1
        self.generic_visit(node)


def get_node_details(node):
    """Extracts detailed information from a single AST function or class node."""
    details = {"source": ast.unparse(node)}
    
    if isinstance(node, ast.FunctionDef):
        # Extract function signature (argument names)
        args = [arg.arg for arg in node.args.args]
        defaults = len(node.args.defaults)
        vararg = node.args.vararg.arg if node.args.vararg else None
        kwarg = node.args.kwonlyargs
        kwarg_defaults = node.args.kw_defaults
        
        signature_parts = []
        if args:
            signature_parts.extend(args)
        if vararg:
            signature_parts.append(f"*{vararg}")
        if kwarg:
            signature_parts.extend([kw.arg for kw in kwarg])
        if node.args.kwarg:
            signature_parts.append(f"**{node.args.kwarg.arg}")
            
        details["signature"] = f"({', '.join(signature_parts)})"
        details["has_defaults"] = defaults > 0
        details["is_async"] = isinstance(node, ast.AsyncFunctionDef)
        
        # Extract decorators
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
            elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                decorators.append(decorator.func.id)
        details["decorators"] = set(decorators)

        # Use the visitor to get deep details
        visitor = FunctionDetailVisitor()
        if isinstance(node, ast.AsyncFunctionDef):
            visitor.async_features["async_def"] = True
        visitor.visit(node)
        
        # Store all the extracted semantic information
        details["calls"] = visitor.calls
        details["exception_handlers"] = visitor.exception_handlers
        details["control_flow"] = visitor.control_flow_statements
        details["return_statements"] = visitor.return_statements
        details["yield_statements"] = visitor.yield_statements
        details["async_features"] = visitor.async_features
        details["comprehensions"] = visitor.comprehensions
        details["lambda_functions"] = visitor.lambda_functions
        details["class_definitions"] = visitor.class_definitions
        details["global_statements"] = visitor.global_statements
        details["nonlocal_statements"] = visitor.nonlocal_statements
        details["assert_statements"] = visitor.assert_statements
        details["string_literals"] = visitor.string_literals
        details["numeric_literals"] = visitor.numeric_literals
        details["boolean_literals"] = visitor.boolean_literals
        details["none_literals"] = visitor.none_literals
        details["attribute_access"] = visitor.attribute_access
        details["subscript_access"] = visitor.subscript_access
        details["binary_operators"] = visitor.binary_operators
        details["unary_operators"] = visitor.unary_operators
        details["comparison_operators"] = visitor.comparison_operators
        details["logical_operators"] = visitor.logical_operators
        details["assignment_targets"] = visitor.assignment_targets
        details["augmented_assignments"] = visitor.augmented_assignments
        details["starred_expressions"] = visitor.starred_expressions
        details["slice_expressions"] = visitor.slice_expressions
        
    elif isinstance(node, ast.ClassDef):
        # Extract class-specific information
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
        details["base_classes"] = set(bases)
        
        # Extract decorators for classes too
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
        details["decorators"] = set(decorators)
        
        # Count methods and attributes
        methods = []
        attributes = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(item.name)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attributes.append(target.id)
        details["methods"] = set(methods)
        details["attributes"] = set(attributes)
        
    return details

def parse_code(source_code):
    """
    Parses Python source code and extracts module-level dependencies
    and a dictionary of semantic nodes.
    """
    nodes = {}
    module_dependencies = set()
    if not source_code:
        return nodes, module_dependencies
        
    try:
        tree = ast.parse(source_code)
        
        # Find all module-level imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_dependencies.add(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                module_dependencies.add(node.module)
        
        # Find all function and class definitions
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    node_type = "func"
                else:
                    node_type = "class"
                node_id = f"{node_type}:{node.name}"
                nodes[node_id] = get_node_details(node)
                
    except SyntaxError:
        console.print(f"[bold yellow]Warning:[/bold yellow] Could not parse a file due to a syntax error.")
        
    return nodes, module_dependencies
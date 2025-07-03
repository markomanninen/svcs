#!/usr/bin/env python3

import ast
import sys
import os

# Add the svcs directory to path
sys.path.insert(0, 'os.path.dirname(os.path.dirname(os.path.abspath(__file__)))')

from svcs.parsers.python_parser import FunctionDetailVisitor

def test_visitor_directly():
    """Test the visitor directly on a constant node."""
    
    test_code = """
def test_func():
    x = True
    y = False
    return x and y
"""
    
    tree = ast.parse(test_code)
    func_node = tree.body[0]  # Get the function node
    
    visitor = FunctionDetailVisitor()
    
    print("Testing visitor directly...")
    print("=" * 40)
    
    # Test visit_Constant directly on a boolean node
    for node in ast.walk(func_node):
        if isinstance(node, ast.Constant) and isinstance(node.value, bool):
            print(f"Found Constant node with boolean value: {node.value}")
            print(f"Before visit_Constant: {visitor.boolean_literals}")
            visitor.visit_Constant(node)
            print(f"After visit_Constant: {visitor.boolean_literals}")
    
    print("\nTesting full visitor traversal...")
    visitor2 = FunctionDetailVisitor()
    print(f"Before visitor.visit(): {visitor2.boolean_literals}")
    visitor2.visit(func_node)
    print(f"After visitor.visit(): {visitor2.boolean_literals}")

if __name__ == "__main__":
    test_visitor_directly()

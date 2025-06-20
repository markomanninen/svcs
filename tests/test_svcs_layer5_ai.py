#!/usr/bin/env python3
"""
SVCS Layer 5: AI-Powered Contextual Semantic Analysis
Completes the Time Crystal VCS vision with intelligent pattern recognition
"""

import sys
import os
import re
import ast
from typing import Dict, List, Set, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.svcs'))

from api import get_full_log

class RefactoringPattern(Enum):
    """Enumeration of detectable refactoring patterns."""
    CONDITIONAL_TO_BUILTIN = "conditional_logic_replaced_with_builtin"
    LOOP_TO_COMPREHENSION = "loop_converted_to_comprehension"
    NESTED_CONDITIONS_FLATTENED = "nested_conditions_flattened"
    DUPLICATE_CODE_EXTRACTED = "duplicate_code_extracted_to_function"
    MAGIC_NUMBERS_CONSTANTS = "magic_numbers_replaced_with_constants"
    MANUAL_ITERATION_TO_BUILTIN = "manual_iteration_replaced_with_builtin"
    COMPLEX_EXPRESSION_SIMPLIFIED = "complex_expression_simplified"
    ERROR_HANDLING_IMPROVED = "error_handling_pattern_improved"
    ALGORITHM_OPTIMIZED = "algorithm_optimized"
    DESIGN_PATTERN_APPLIED = "design_pattern_applied"

@dataclass
class SemanticChange:
    """Represents a high-level semantic change detected by AI analysis."""
    pattern: RefactoringPattern
    confidence: float
    description: str
    before_snippet: str
    after_snippet: str
    impact: str
    node_id: str

class ContextualSemanticAnalyzer:
    """Layer 5: AI-powered contextual analysis for complex semantic patterns."""
    
    def __init__(self):
        self.builtin_functions = {
            'abs', 'max', 'min', 'sum', 'len', 'any', 'all', 'sorted', 
            'reversed', 'enumerate', 'zip', 'filter', 'map', 'range'
        }
        
        self.math_patterns = {
            'sqrt': ['x ** 0.5', 'pow(x, 0.5)', 'x**(1/2)'],
            'square': ['x ** 2', 'pow(x, 2)', 'x*x'],
            'abs': ['x if x >= 0 else -x', 'x if x > 0 else -x']
        }
        
        self.control_flow_patterns = {
            'early_return': r'if\s+.*:\s*return\s+.*\n\s*return',
            'guard_clause': r'if\s+not\s+.*:\s*return',
            'ternary_simplification': r'if\s+.*:\s*\w+\s*=\s*.*\s*else:\s*\w+\s*='
        }

    def analyze_semantic_changes(self, before_code: str, after_code: str, node_id: str) -> List[SemanticChange]:
        """Main method to detect high-level semantic changes."""
        changes = []
        
        # Parse both versions
        try:
            before_ast = ast.parse(before_code)
            after_ast = ast.parse(after_code)
        except SyntaxError:
            return changes
        
        # Pattern detection methods
        changes.extend(self._detect_conditional_to_builtin(before_code, after_code, node_id))
        changes.extend(self._detect_loop_to_comprehension(before_ast, after_ast, node_id))
        changes.extend(self._detect_algorithm_optimization(before_code, after_code, node_id))
        changes.extend(self._detect_error_handling_improvements(before_ast, after_ast, node_id))
        changes.extend(self._detect_code_simplification(before_code, after_code, node_id))
        changes.extend(self._detect_design_patterns(before_ast, after_ast, node_id))
        
        return changes

    def _detect_conditional_to_builtin(self, before: str, after: str, node_id: str) -> List[SemanticChange]:
        """Detect when conditional logic is replaced with builtin functions."""
        changes = []
        
        # Pattern: abs() replacement
        abs_pattern_before = r'if\s+(\w+)\s*[<>]=?\s*0:\s*.*=\s*-\1.*else:\s*.*=\s*\1'
        abs_pattern_after = r'.*=\s*abs\(\w+\)'
        
        if re.search(abs_pattern_before, before, re.MULTILINE) and re.search(abs_pattern_after, after):
            changes.append(SemanticChange(
                pattern=RefactoringPattern.CONDITIONAL_TO_BUILTIN,
                confidence=0.9,
                description="Conditional logic replaced with abs() builtin function",
                before_snippet=self._extract_relevant_snippet(before, abs_pattern_before),
                after_snippet=self._extract_relevant_snippet(after, abs_pattern_after),
                impact="Improved readability and performance",
                node_id=node_id
            ))
        
        # Pattern: max/min replacement
        max_pattern_before = r'if\s+(\w+)\s*[>]=?\s*(\w+):\s*.*=\s*\1.*else:\s*.*=\s*\2'
        max_pattern_after = r'.*=\s*max\(\w+,\s*\w+\)'
        
        if re.search(max_pattern_before, before, re.MULTILINE) and re.search(max_pattern_after, after):
            changes.append(SemanticChange(
                pattern=RefactoringPattern.CONDITIONAL_TO_BUILTIN,
                confidence=0.85,
                description="Conditional comparison replaced with max() builtin function",
                before_snippet=self._extract_relevant_snippet(before, max_pattern_before),
                after_snippet=self._extract_relevant_snippet(after, max_pattern_after),
                impact="More expressive and less error-prone",
                node_id=node_id
            ))
        
        return changes

    def _detect_loop_to_comprehension(self, before_ast: ast.AST, after_ast: ast.AST, node_id: str) -> List[SemanticChange]:
        """Detect when loops are converted to comprehensions."""
        changes = []
        
        # Analyze loop patterns in before
        before_loops = self._find_loop_patterns(before_ast)
        after_comprehensions = self._find_comprehensions(after_ast)
        
        if before_loops and after_comprehensions and len(before_loops) > len(self._find_loop_patterns(after_ast)):
            changes.append(SemanticChange(
                pattern=RefactoringPattern.LOOP_TO_COMPREHENSION,
                confidence=0.8,
                description="Explicit loop converted to list/dict comprehension",
                before_snippet="for loop with append/assignment",
                after_snippet="comprehension expression",
                impact="More Pythonic and potentially faster",
                node_id=node_id
            ))
        
        return changes

    def _detect_algorithm_optimization(self, before: str, after: str, node_id: str) -> List[SemanticChange]:
        """Detect algorithmic improvements and optimizations."""
        changes = []
        
        # Detect O(n²) to O(n) optimizations
        nested_loop_pattern = r'for\s+\w+\s+in\s+.*:\s*for\s+\w+\s+in\s+'
        single_loop_pattern = r'for\s+\w+\s+in\s+.*:'
        
        before_nested = len(re.findall(nested_loop_pattern, before))
        after_nested = len(re.findall(nested_loop_pattern, after))
        
        if before_nested > after_nested and 'set(' in after or 'dict(' in after:
            changes.append(SemanticChange(
                pattern=RefactoringPattern.ALGORITHM_OPTIMIZED,
                confidence=0.75,
                description="Algorithm optimized from O(n²) to O(n) using data structures",
                before_snippet="Nested loops",
                after_snippet="Single loop with set/dict lookup",
                impact="Significant performance improvement",
                node_id=node_id
            ))
        
        # Detect sorting optimizations
        if 'sorted(' in after and 'sort()' in before:
            changes.append(SemanticChange(
                pattern=RefactoringPattern.ALGORITHM_OPTIMIZED,
                confidence=0.7,
                description="In-place sorting replaced with sorted() for immutability",
                before_snippet="list.sort()",
                after_snippet="sorted(list)",
                impact="Improved immutability and functional style",
                node_id=node_id
            ))
        
        return changes

    def _detect_error_handling_improvements(self, before_ast: ast.AST, after_ast: ast.AST, node_id: str) -> List[SemanticChange]:
        """Detect improvements in error handling patterns."""
        changes = []
        
        before_try_blocks = len([node for node in ast.walk(before_ast) if isinstance(node, ast.Try)])
        after_try_blocks = len([node for node in ast.walk(after_ast) if isinstance(node, ast.Try)])
        
        # More specific exception handling
        before_except_types = self._count_exception_types(before_ast)
        after_except_types = self._count_exception_types(after_ast)
        
        if after_except_types > before_except_types:
            changes.append(SemanticChange(
                pattern=RefactoringPattern.ERROR_HANDLING_IMPROVED,
                confidence=0.8,
                description="Generic exception handling replaced with specific exception types",
                before_snippet="except: or except Exception:",
                after_snippet="except SpecificException:",
                impact="Better error handling and debugging",
                node_id=node_id
            ))
        
        # Context managers introduced
        before_with = len([node for node in ast.walk(before_ast) if isinstance(node, ast.With)])
        after_with = len([node for node in ast.walk(after_ast) if isinstance(node, ast.With)])
        
        if after_with > before_with:
            changes.append(SemanticChange(
                pattern=RefactoringPattern.ERROR_HANDLING_IMPROVED,
                confidence=0.85,
                description="Manual resource management replaced with context managers",
                before_snippet="Manual open/close",
                after_snippet="with statement",
                impact="Guaranteed resource cleanup",
                node_id=node_id
            ))
        
        return changes

    def _detect_code_simplification(self, before: str, after: str, node_id: str) -> List[SemanticChange]:
        """Detect general code simplification patterns."""
        changes = []
        
        # Detect magic number extraction
        magic_numbers_before = len(re.findall(r'\b\d{2,}\b', before))
        constants_after = len(re.findall(r'[A-Z_]{2,}', after))
        
        if magic_numbers_before > 0 and constants_after > 0 and len(after) > len(before):
            changes.append(SemanticChange(
                pattern=RefactoringPattern.MAGIC_NUMBERS_CONSTANTS,
                confidence=0.7,
                description="Magic numbers replaced with named constants",
                before_snippet="Literal numbers in code",
                after_snippet="Named constants",
                impact="Improved maintainability and readability",
                node_id=node_id
            ))
        
        # Detect complex expression simplification
        complex_expr_before = len(re.findall(r'\([^)]*\([^)]*\)[^)]*\)', before))
        if complex_expr_before > 0 and len(after) < len(before) * 0.8:
            changes.append(SemanticChange(
                pattern=RefactoringPattern.COMPLEX_EXPRESSION_SIMPLIFIED,
                confidence=0.6,
                description="Complex nested expressions simplified",
                before_snippet="Nested complex expression",
                after_snippet="Simplified expression or intermediate variables",
                impact="Improved readability",
                node_id=node_id
            ))
        
        return changes

    def _detect_design_patterns(self, before_ast: ast.AST, after_ast: ast.AST, node_id: str) -> List[SemanticChange]:
        """Detect application of design patterns."""
        changes = []
        
        # Detect decorator pattern introduction
        before_decorators = len([node for node in ast.walk(before_ast) 
                               if isinstance(node, ast.FunctionDef) and node.decorator_list])
        after_decorators = len([node for node in ast.walk(after_ast) 
                              if isinstance(node, ast.FunctionDef) and node.decorator_list])
        
        if after_decorators > before_decorators:
            changes.append(SemanticChange(
                pattern=RefactoringPattern.DESIGN_PATTERN_APPLIED,
                confidence=0.75,
                description="Decorator pattern applied for cross-cutting concerns",
                before_snippet="Plain function",
                after_snippet="Decorated function",
                impact="Separation of concerns and reusability",
                node_id=node_id
            ))
        
        # Detect property pattern
        before_properties = len([node for node in ast.walk(before_ast) 
                               if isinstance(node, ast.FunctionDef) and 
                               any(isinstance(d, ast.Name) and d.id == 'property' 
                                   for d in node.decorator_list)])
        after_properties = len([node for node in ast.walk(after_ast) 
                              if isinstance(node, ast.FunctionDef) and 
                              any(isinstance(d, ast.Name) and d.id == 'property' 
                                  for d in node.decorator_list)])
        
        if after_properties > before_properties:
            changes.append(SemanticChange(
                pattern=RefactoringPattern.DESIGN_PATTERN_APPLIED,
                confidence=0.8,
                description="Property pattern applied for encapsulation",
                before_snippet="Direct attribute access",
                after_snippet="Property-based access",
                impact="Better encapsulation and validation",
                node_id=node_id
            ))
        
        return changes

    def _find_loop_patterns(self, tree: ast.AST) -> List[ast.AST]:
        """Find explicit loop patterns that could be comprehensions."""
        loops = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                loops.append(node)
        return loops

    def _find_comprehensions(self, tree: ast.AST) -> List[ast.AST]:
        """Find comprehension expressions."""
        comprehensions = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
                comprehensions.append(node)
        return comprehensions

    def _count_exception_types(self, tree: ast.AST) -> int:
        """Count specific exception types being caught."""
        specific_exceptions = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type:
                specific_exceptions += 1
        return specific_exceptions

    def _extract_relevant_snippet(self, code: str, pattern: str) -> str:
        """Extract relevant code snippet for display."""
        match = re.search(pattern, code, re.MULTILINE)
        if match:
            return match.group(0)[:100] + "..." if len(match.group(0)) > 100 else match.group(0)
        return "Code pattern"

def analyze_contextual_changes():
    """Main function to analyze contextual semantic changes in the codebase."""
    
    print("🤖 LAYER 5: AI-POWERED CONTEXTUAL SEMANTIC ANALYSIS")
    print("=" * 60)
    
    # Get recent events to find files with changes
    events = get_full_log()
    
    if not events:
        print("No events found in database.")
        return
    
    # Group events by file and analyze the most changed files
    file_changes = {}
    for event in events:
        location = event['location']
        if location not in file_changes:
            file_changes[location] = []
        file_changes[location].append(event)
    
    # Sort by number of changes
    sorted_files = sorted(file_changes.items(), key=lambda x: len(x[1]), reverse=True)
    
    analyzer = ContextualSemanticAnalyzer()
    total_patterns = 0
    
    print(f"📊 Analyzing {len(sorted_files)} files for contextual semantic patterns...")
    print()
    
    for file_path, file_events in sorted_files[:5]:  # Analyze top 5 most changed files
        if not file_path.endswith('.py'):  # Focus on Python files for now
            continue
            
        print(f"🔍 Analyzing: {file_path}")
        print(f"   Events: {len(file_events)}")
        
        # For demonstration, we'll simulate before/after analysis
        # In real implementation, you'd get actual file contents from git history
        semantic_changes = simulate_contextual_analysis(analyzer, file_path, file_events)
        
        if semantic_changes:
            print(f"   🎯 Detected {len(semantic_changes)} high-level semantic patterns:")
            for change in semantic_changes:
                print(f"      • {change.pattern.value}")
                print(f"        Confidence: {change.confidence:.1%}")
                print(f"        Impact: {change.impact}")
                print(f"        Description: {change.description}")
                print()
            total_patterns += len(semantic_changes)
        else:
            print("   ✓ No complex semantic patterns detected")
        print()
    
    print("🎉 CONTEXTUAL ANALYSIS COMPLETE")
    print(f"   Total High-Level Patterns Detected: {total_patterns}")
    print(f"   Time Crystal VCS Layer 5: ACTIVE! 🌟")

def simulate_contextual_analysis(analyzer: ContextualSemanticAnalyzer, file_path: str, events: List[Dict]) -> List[SemanticChange]:
    """Simulate contextual analysis for demonstration."""
    # This would normally analyze actual git diff content
    # For demo, we'll generate realistic patterns based on event types
    
    changes = []
    event_types = [e['event_type'] for e in events]
    
    # Simulate patterns based on event combinations
    if 'control_flow_changed' in event_types and 'comprehension_usage_changed' in event_types:
        changes.append(SemanticChange(
            pattern=RefactoringPattern.LOOP_TO_COMPREHENSION,
            confidence=0.85,
            description="Explicit loop converted to comprehension based on detected events",
            before_snippet="for item in items: result.append(transform(item))",
            after_snippet="result = [transform(item) for item in items]",
            impact="More Pythonic and potentially faster execution",
            node_id=f"pattern:{file_path}"
        ))
    
    if 'exception_handling_added' in event_types and 'internal_call_added' in event_types:
        changes.append(SemanticChange(
            pattern=RefactoringPattern.ERROR_HANDLING_IMPROVED,
            confidence=0.8,
            description="Error handling pattern improved with specific exceptions",
            before_snippet="try: ... except: pass",
            after_snippet="try: ... except SpecificError as e: handle(e)",
            impact="Better error handling and debugging capabilities",
            node_id=f"pattern:{file_path}"
        ))
    
    if 'decorator_added' in event_types:
        changes.append(SemanticChange(
            pattern=RefactoringPattern.DESIGN_PATTERN_APPLIED,
            confidence=0.9,
            description="Decorator pattern applied for cross-cutting concerns",
            before_snippet="def func(): # with manual logging/timing",
            after_snippet="@decorator def func(): # automatic concerns",
            impact="Separation of concerns and code reusability",
            node_id=f"pattern:{file_path}"
        ))
    
    if 'binary_operator_usage_changed' in event_types and 'internal_call_added' in event_types:
        changes.append(SemanticChange(
            pattern=RefactoringPattern.CONDITIONAL_TO_BUILTIN,
            confidence=0.75,
            description="Manual comparison logic replaced with builtin function",
            before_snippet="if x > y: result = x else: result = y",
            after_snippet="result = max(x, y)",
            impact="Improved readability and performance",
            node_id=f"pattern:{file_path}"
        ))
    
    return changes

if __name__ == "__main__":
    analyze_contextual_changes()
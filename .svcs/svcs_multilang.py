#!/usr/bin/env python3
"""
SVCS Multi-Language Support Module
Provides semantic analysis for multiple programming languages beyond Python.
"""

import re
import ast
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
    
    def parse_code(self, content: str) -> Dict[str, Any]:
        """Parse PHP code and extract functions, classes, variables."""
        elements = {
            'functions': {},
            'classes': {},
            'variables': set(),
            'includes': []
        }
        
        # Extract PHP functions
        function_pattern = r'function\s+([a-zA-Z_]\w*)\s*\([^)]*\)'
        for match in re.finditer(function_pattern, content):
            func_name = match.group(1)
            elements['functions'][f'func:{func_name}'] = {
                'name': func_name,
                'start': match.start(),
                'signature': match.group(0)
            }
        
        # Extract PHP classes
        class_pattern = r'class\s+([a-zA-Z_]\w*)'
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            elements['classes'][f'class:{class_name}'] = {
                'name': class_name,
                'start': match.start()
            }
        
        # Extract variables
        var_pattern = r'\$([a-zA-Z_]\w*)'
        for match in re.finditer(var_pattern, content):
            elements['variables'].add(match.group(1))
        
        # Extract includes/requires
        include_pattern = r'(?:include|require)(?:_once)?\s*[\'"]([^\'"]+)[\'"]'
        for match in re.finditer(include_pattern, content):
            elements['includes'].append(match.group(1))
        
        return elements
    
    def detect_changes(self, before: Dict[str, Any], after: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect changes in PHP code."""
        events = []
        
        # Function changes
        before_funcs = set(before['functions'].keys())
        after_funcs = set(after['functions'].keys())
        
        # Added functions
        for func_id in after_funcs - before_funcs:
            events.append({
                'event_type': 'node_added',
                'node_id': func_id,
                'location': 'php_file',
                'details': f'PHP function {func_id} added'
            })
        
        # Removed functions
        for func_id in before_funcs - after_funcs:
            events.append({
                'event_type': 'node_removed',
                'node_id': func_id,
                'location': 'php_file',
                'details': f'PHP function {func_id} removed'
            })
        
        # Class changes
        before_classes = set(before['classes'].keys())
        after_classes = set(after['classes'].keys())
        
        # Added classes
        for class_id in after_classes - before_classes:
            events.append({
                'event_type': 'node_added',
                'node_id': class_id,
                'location': 'php_file',
                'details': f'PHP class {class_id} added'
            })
        
        # Removed classes
        for class_id in before_classes - after_classes:
            events.append({
                'event_type': 'node_removed',
                'node_id': class_id,
                'location': 'php_file',
                'details': f'PHP class {class_id} removed'
            })
        
        # Variable changes
        before_vars = before['variables']
        after_vars = after['variables']
        
        if before_vars != after_vars:
            added_vars = after_vars - before_vars
            removed_vars = before_vars - after_vars
            
            if added_vars:
                events.append({
                    'event_type': 'variable_usage_changed',
                    'node_id': 'global_scope',
                    'location': 'php_file',
                    'details': f'Added variables: {", ".join(sorted(added_vars))}'
                })
            
            if removed_vars:
                events.append({
                    'event_type': 'variable_usage_changed',
                    'node_id': 'global_scope',
                    'location': 'php_file',
                    'details': f'Removed variables: {", ".join(sorted(removed_vars))}'
                })
        
        # Include changes
        before_includes = set(before['includes'])
        after_includes = set(after['includes'])
        
        if before_includes != after_includes:
            added_includes = after_includes - before_includes
            removed_includes = before_includes - after_includes
            
            if added_includes:
                events.append({
                    'event_type': 'dependency_added',
                    'node_id': 'module:php_file',
                    'location': 'php_file',
                    'details': f'Added includes: {", ".join(sorted(added_includes))}'
                })
            
            if removed_includes:
                events.append({
                    'event_type': 'dependency_removed',
                    'node_id': 'module:php_file',
                    'location': 'php_file',
                    'details': f'Removed includes: {", ".join(sorted(removed_includes))}'
                })
        
        return events

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
    php_before = '''<?php
function hello() {
    echo "Hello";
}
?>'''
    
    php_after = '''<?php
function hello($name = "World") {
    echo "Hello " . $name;
}

function goodbye($name) {
    echo "Goodbye " . $name;
}
?>'''
    
    events = analyzer.analyze_file_changes("test.php", php_before, php_after)
    print(f"PHP events detected: {len(events)}")
    for event in events:
        print(f"  - {event['event_type']}: {event['node_id']} - {event['details']}")

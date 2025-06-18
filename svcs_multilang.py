#!/usr/bin/env python3
"""
SVCS Multi-Language Support Framework
Extensible framework for analyzing semantic changes across programming languages
"""

import os
import sys
import ast
from abc import ABC, abstractmethod
from typing import Dict, List, Set, Tuple, Any
import re

class SemanticAnalyzer(ABC):
    """Abstract base class for language-specific semantic analyzers."""
    
    @abstractmethod
    def parse_code(self, source_code: str) -> Tuple[Dict[str, Any], Set[str]]:
        """Parse code and return (nodes, dependencies)."""
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """Return list of file extensions this analyzer supports."""
        pass
    
    @abstractmethod
    def get_language_name(self) -> str:
        """Return the name of the programming language."""
        pass
    
    def extract_semantic_features(self, node_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract semantic features from parsed node information."""
        return node_info

class PythonSemanticAnalyzer(SemanticAnalyzer):
    """Enhanced Python semantic analyzer with comprehensive pattern detection."""
    
    def get_supported_extensions(self) -> List[str]:
        return ['.py', '.pyw', '.pyi']
    
    def get_language_name(self) -> str:
        return "Python"
    
    def parse_code(self, source_code: str) -> Tuple[Dict[str, Any], Set[str]]:
        """Parse Python code using our existing enhanced parser."""
        # Import our existing parser
        sys.path.insert(0, '.svcs')
        from parser import parse_code
        return parse_code(source_code)

class JavaScriptSemanticAnalyzer(SemanticAnalyzer):
    """Basic JavaScript semantic analyzer."""
    
    def get_supported_extensions(self) -> List[str]:
        return ['.js', '.jsx', '.ts', '.tsx', '.mjs']
    
    def get_language_name(self) -> str:
        return "JavaScript/TypeScript"
    
    def parse_code(self, source_code: str) -> Tuple[Dict[str, Any], Set[str]]:
        """Basic JavaScript parsing using regex patterns."""
        nodes = {}
        dependencies = set()
        
        # Extract imports/requires
        import_patterns = [
            r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'require\([\'"]([^\'"]+)[\'"]\)',
            r'import\([\'"]([^\'"]+)[\'"]\)'
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, source_code)
            dependencies.update(matches)
        
        # Extract function definitions
        function_patterns = [
            r'function\s+(\w+)\s*\([^)]*\)',
            r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>', 
            r'(\w+)\s*:\s*function\s*\([^)]*\)',
            r'(\w+)\s*:\s*\([^)]*\)\s*=>'
        ]
        
        for pattern in function_patterns:
            matches = re.findall(pattern, source_code)
            for match in matches:
                func_name = match if isinstance(match, str) else match[0]
                node_id = f"func:{func_name}"
                nodes[node_id] = {
                    "source": f"function {func_name}(...)",
                    "language": "javascript",
                    "type": "function"
                }
        
        # Extract class definitions
        class_pattern = r'class\s+(\w+)'
        class_matches = re.findall(class_pattern, source_code)
        for class_name in class_matches:
            node_id = f"class:{class_name}"
            nodes[node_id] = {
                "source": f"class {class_name}",
                "language": "javascript", 
                "type": "class"
            }
        
        return nodes, dependencies

class GoSemanticAnalyzer(SemanticAnalyzer):
    """Basic Go semantic analyzer."""
    
    def get_supported_extensions(self) -> List[str]:
        return ['.go']
    
    def get_language_name(self) -> str:
        return "Go"
    
    def parse_code(self, source_code: str) -> Tuple[Dict[str, Any], Set[str]]:
        """Basic Go parsing using regex patterns."""
        nodes = {}
        dependencies = set()
        
        # Extract imports
        import_pattern = r'import\s+(?:\(\s*((?:[^)]+\n)*)\s*\)|"([^"]+)")'
        matches = re.finditer(import_pattern, source_code, re.MULTILINE)
        for match in matches:
            if match.group(1):  # Multi-line import
                imports = re.findall(r'"([^"]+)"', match.group(1))
                dependencies.update(imports)
            elif match.group(2):  # Single import
                dependencies.add(match.group(2))
        
        # Extract function definitions
        func_pattern = r'func\s+(?:\([^)]*\)\s+)?(\w+)\s*\([^)]*\)'
        func_matches = re.findall(func_pattern, source_code)
        for func_name in func_matches:
            node_id = f"func:{func_name}"
            nodes[node_id] = {
                "source": f"func {func_name}(...)",
                "language": "go",
                "type": "function"
            }
        
        # Extract struct definitions
        struct_pattern = r'type\s+(\w+)\s+struct'
        struct_matches = re.findall(struct_pattern, source_code)
        for struct_name in struct_matches:
            node_id = f"struct:{struct_name}"
            nodes[node_id] = {
                "source": f"type {struct_name} struct",
                "language": "go",
                "type": "struct"
            }
        
        return nodes, dependencies

class PHPSemanticAnalyzer(SemanticAnalyzer):
    """Comprehensive PHP semantic analyzer."""
    
    def get_supported_extensions(self) -> List[str]:
        return ['.php', '.phtml', '.php3', '.php4', '.php5', '.phps']
    
    def get_language_name(self) -> str:
        return "PHP"
    
    def parse_code(self, source_code: str) -> Tuple[Dict[str, Any], Set[str]]:
        """Parse PHP code and extract semantic features."""
        nodes = {}
        dependencies = set()
        
        # Extract namespace declarations
        namespace_pattern = r'namespace\s+([\w\\]+)\s*;'
        namespace_matches = re.findall(namespace_pattern, source_code)
        for namespace in namespace_matches:
            dependencies.add(f"namespace:{namespace}")
        
        # Extract use statements (imports)
        use_patterns = [
            r'use\s+([\w\\]+)(?:\s+as\s+(\w+))?\s*;',
            r'use\s+function\s+([\w\\]+)(?:\s+as\s+(\w+))?\s*;',
            r'use\s+const\s+([\w\\]+)(?:\s+as\s+(\w+))?\s*;'
        ]
        
        for pattern in use_patterns:
            matches = re.findall(pattern, source_code)
            for match in matches:
                if isinstance(match, tuple):
                    dependencies.add(match[0])
                else:
                    dependencies.add(match)
        
        # Extract require/include statements
        include_patterns = [
            r'(?:require|include)(?:_once)?\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
            r'(?:require|include)(?:_once)?\s+[\'"]([^\'"]+)[\'"]'
        ]
        
        for pattern in include_patterns:
            matches = re.findall(pattern, source_code)
            dependencies.update(matches)
        
        # Extract class definitions
        class_pattern = r'(?:abstract\s+|final\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w\s,]+))?'
        class_matches = re.finditer(class_pattern, source_code)
        for match in class_matches:
            class_name = match.group(1)
            extends = match.group(2)
            implements = match.group(3)
            
            node_id = f"class:{class_name}"
            class_info = {
                "source": f"class {class_name}",
                "language": "php",
                "type": "class",
                "extends": extends,
                "implements": implements.split(',') if implements else []
            }
            nodes[node_id] = class_info
            
            if extends:
                dependencies.add(f"extends:{extends}")
            if implements:
                for interface in implements.split(','):
                    dependencies.add(f"implements:{interface.strip()}")
        
        # Extract interface definitions
        interface_pattern = r'interface\s+(\w+)(?:\s+extends\s+([\w\s,]+))?'
        interface_matches = re.finditer(interface_pattern, source_code)
        for match in interface_matches:
            interface_name = match.group(1)
            extends = match.group(2)
            
            node_id = f"interface:{interface_name}"
            nodes[node_id] = {
                "source": f"interface {interface_name}",
                "language": "php",
                "type": "interface",
                "extends": extends.split(',') if extends else []
            }
        
        # Extract trait definitions
        trait_pattern = r'trait\s+(\w+)'
        trait_matches = re.findall(trait_pattern, source_code)
        for trait_name in trait_matches:
            node_id = f"trait:{trait_name}"
            nodes[node_id] = {
                "source": f"trait {trait_name}",
                "language": "php",
                "type": "trait"
            }
        
        # Extract function definitions (both global and methods)
        function_patterns = [
            # Global functions
            r'function\s+(\w+)\s*\([^)]*\)',
            # Class methods with visibility
            r'(?:public|private|protected|static|\s)+function\s+(\w+)\s*\([^)]*\)',
            # Anonymous functions assigned to variables
            r'\$(\w+)\s*=\s*function\s*\([^)]*\)'
        ]
        
        for pattern in function_patterns:
            matches = re.findall(pattern, source_code)
            for func_name in matches:
                node_id = f"func:{func_name}"
                nodes[node_id] = {
                    "source": f"function {func_name}(...)",
                    "language": "php",
                    "type": "function"
                }
        
        # Extract properties and constants
        property_pattern = r'(?:public|private|protected|static|\s)*\$(\w+)'
        property_matches = re.findall(property_pattern, source_code)
        for prop_name in property_matches:
            node_id = f"prop:{prop_name}"
            nodes[node_id] = {
                "source": f"${prop_name}",
                "language": "php",
                "type": "property"
            }
        
        # Extract constants
        const_patterns = [
            r'const\s+(\w+)',
            r'define\s*\(\s*[\'"](\w+)[\'"]'
        ]
        
        for pattern in const_patterns:
            matches = re.findall(pattern, source_code)
            for const_name in matches:
                node_id = f"const:{const_name}"
                nodes[node_id] = {
                    "source": f"const {const_name}",
                    "language": "php",
                    "type": "constant"
                }
        
        return nodes, dependencies

class MultiLanguageAnalyzer:
    """Multi-language semantic analysis coordinator."""
    
    def __init__(self):
        self.analyzers = {
            'python': PythonSemanticAnalyzer(),
            'javascript': JavaScriptSemanticAnalyzer(), 
            'go': GoSemanticAnalyzer(),
            'php': PHPSemanticAnalyzer()
        }
        
        # Build extension mapping
        self.extension_to_analyzer = {}
        for name, analyzer in self.analyzers.items():
            for ext in analyzer.get_supported_extensions():
                self.extension_to_analyzer[ext] = analyzer
    
    def get_analyzer_for_file(self, filepath: str) -> SemanticAnalyzer:
        """Get the appropriate analyzer for a file."""
        _, ext = os.path.splitext(filepath.lower())
        return self.extension_to_analyzer.get(ext, self.analyzers['python'])  # Default to Python
    
    def analyze_file_changes(self, filepath: str, before_content: str, after_content: str) -> List[Dict[str, Any]]:
        """Analyze semantic changes in any supported language."""
        
        analyzer = self.get_analyzer_for_file(filepath)
        language = analyzer.get_language_name()
        
        if before_content == after_content:
            return []
        
        # Parse before and after
        nodes_before, deps_before = analyzer.parse_code(before_content)
        nodes_after, deps_after = analyzer.parse_code(after_content)
        
        events = []
        
        # Analyze dependency changes
        added_deps = deps_after - deps_before
        removed_deps = deps_before - deps_after
        
        if added_deps:
            events.append({
                "event_type": "dependency_added",
                "node_id": f"module:{filepath}",
                "location": filepath,
                "details": f"Added: {', '.join(sorted(added_deps))}",
                "language": language
            })
        
        if removed_deps:
            events.append({
                "event_type": "dependency_removed", 
                "node_id": f"module:{filepath}",
                "location": filepath,
                "details": f"Removed: {', '.join(sorted(removed_deps))}",
                "language": language
            })
        
        # Analyze node changes
        all_node_ids = set(nodes_before.keys()) | set(nodes_after.keys())
        
        for node_id in all_node_ids:
            base_event = {"node_id": node_id, "location": filepath, "language": language}
            
            if node_id not in nodes_before:
                events.append({**base_event, "event_type": "node_added", "details": ""})
            elif node_id not in nodes_after:
                events.append({**base_event, "event_type": "node_removed", "details": ""})
            elif nodes_before[node_id].get("source") != nodes_after[node_id].get("source"):
                events.append({**base_event, "event_type": "node_modified", "details": "Implementation changed"})
        
        return events
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return [analyzer.get_language_name() for analyzer in self.analyzers.values()]
    
    def get_language_statistics(self, events: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get statistics by programming language."""
        stats = {}
        for event in events:
            lang = event.get('language', 'Unknown')
            stats[lang] = stats.get(lang, 0) + 1
        return stats

def test_multi_language_support():
    """Test the multi-language analyzer with sample code."""
    
    print("🌍 TESTING MULTI-LANGUAGE SUPPORT")
    print("=" * 40)
    
    analyzer = MultiLanguageAnalyzer()
    
    # Test JavaScript
    js_before = '''
function greet(name) {
    return "Hello " + name;
}
'''
    
    js_after = '''
import React from 'react';

const greet = (name) => {
    return `Hello ${name}!`;
};

class Greeter {
    constructor(greeting) {
        this.greeting = greeting;
    }
}
'''
    
    print("📄 JavaScript Analysis:")
    js_events = analyzer.analyze_file_changes("test.js", js_before, js_after)
    for event in js_events:
        print(f"   • {event['event_type']}: {event['node_id']} - {event.get('details', '')}")
    
    # Test Go
    go_before = '''
package main

func hello(name string) string {
    return "Hello " + name
}
'''
    
    go_after = '''
package main

import "fmt"

type Person struct {
    Name string
}

func (p Person) hello() string {
    return fmt.Sprintf("Hello %s", p.Name)
}

func greet(name string) string {
    return "Hi " + name
}
'''
    
    print("\n📄 Go Analysis:")
    go_events = analyzer.analyze_file_changes("test.go", go_before, go_after)
    for event in go_events:
        print(f"   • {event['event_type']}: {event['node_id']} - {event.get('details', '')}")
    
    # Test PHP
    php_before = '''<?php

class User {
    private $name;
    
    public function __construct($name) {
        $this->name = $name;
    }
    
    public function getName() {
        return $this->name;
    }
}

function greet($name) {
    return "Hello " . $name;
}
?>'''
    
    php_after = '''<?php

namespace App\\Models;

use DateTime;
use App\\Contracts\\UserInterface;

class User implements UserInterface {
    private $name;
    private $email;
    private $createdAt;
    
    const STATUS_ACTIVE = 'active';
    
    public function __construct($name, $email = null) {
        $this->name = $name;
        $this->email = $email;
        $this->createdAt = new DateTime();
    }
    
    public function getName(): string {
        return $this->name;
    }
    
    public function getEmail(): ?string {
        return $this->email;
    }
    
    public function isActive(): bool {
        return true;
    }
}

trait Timestampable {
    private $updatedAt;
    
    public function touch() {
        $this->updatedAt = new DateTime();
    }
}

interface UserInterface {
    public function getName(): string;
}

function greet(string $name): string {
    return "Hello " . $name . "!";
}

function createUser(string $name, ?string $email = null): User {
    return new User($name, $email);
}
?>'''
    
    print("\n📄 PHP Analysis:")
    php_events = analyzer.analyze_file_changes("test.php", php_before, php_after)
    for event in php_events:
        print(f"   • {event['event_type']}: {event['node_id']} - {event.get('details', '')}")
    
    print(f"\n🌐 Supported Languages: {', '.join(analyzer.get_supported_languages())}")
    
    all_events = js_events + go_events + php_events
    language_stats = analyzer.get_language_statistics(all_events)
    print(f"📊 Language Event Distribution: {language_stats}")

if __name__ == "__main__":
    test_multi_language_support()

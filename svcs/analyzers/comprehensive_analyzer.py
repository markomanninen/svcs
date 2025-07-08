# SVCS Comprehensive Modular Analyzer
# Integrates all 5 layers of semantic analysis

import os
from typing import List, Dict, Any, Optional
from ..parsers import PythonParser, PHPParser, JavaScriptParser, BaseParser
from ..layers import (StructuralAnalyzer, SyntacticAnalyzer, SemanticAnalyzer, 
                     BehavioralAnalyzer, AIPatternAnalyzer, TrueAIAnalyzer)
from ..storage import initialize_database, store_commit_events, get_recent_events, get_event_statistics

class ComprehensiveAnalyzer:
    """
    Comprehensive 5-layer modular semantic analyzer.
    
    Layers:
    1. Structural - File and module structure
    2. Syntactic - Syntax and signatures  
    3. Semantic - Logic and meaning
    4. Behavioral - Patterns and complexity
    5a. AI Patterns - Pattern recognition
    5b. True AI - LLM analysis
    """
    
    def __init__(self):
        # Initialize parsers
        self.parsers = {
            'python': PythonParser(),
            'php': PHPParser(), 
            'javascript': JavaScriptParser()
        }
        
        # Initialize all analysis layers
        self.layer1 = StructuralAnalyzer()
        self.layer2 = SyntacticAnalyzer()
        self.layer3 = SemanticAnalyzer()
        self.layer4 = BehavioralAnalyzer()
        self.layer5a = AIPatternAnalyzer()
        self.layer5b = TrueAIAnalyzer()
        
        self.layers = [
            self.layer1, self.layer2, self.layer3, 
            self.layer4, self.layer5a, self.layer5b
        ]
    
    def analyze_file_changes(self, filepath: str, before_content: str, 
                           after_content: str) -> List[Dict[str, Any]]:
        """
        Comprehensive analysis of file changes using all 5 layers.
        
        Args:
            filepath: Path to the file being analyzed
            before_content: Content before changes
            after_content: Content after changes
            
        Returns:
            List of semantic events from all layers
        """
        all_events = []
        
        # Skip if no actual change
        if before_content == after_content:
            return all_events
        
        # Select appropriate parser
        parser = self._get_parser_for_file(filepath)
        if not parser:
            return all_events
        
        # Parse both versions
        nodes_before, deps_before = parser.parse_code(before_content)
        nodes_after, deps_after = parser.parse_code(after_content)
        
        # Run all layers of analysis
        try:
            # Layer 1: Structural Analysis
            events = self.layer1.analyze(
                filepath, before_content, after_content, 
                nodes_before, nodes_after, deps_before, deps_after
            )
            all_events.extend(events)
            
            # Layer 2: Syntactic Analysis
            events = self.layer2.analyze(filepath, nodes_before, nodes_after)
            all_events.extend(events)
            
            # Layer 3: Semantic Analysis
            events = self.layer3.analyze(filepath, nodes_before, nodes_after)
            all_events.extend(events)
            
            # Layer 4: Behavioral Analysis
            events = self.layer4.analyze(filepath, nodes_before, nodes_after)
            all_events.extend(events)
            
            # Layer 5a: AI Pattern Analysis
            events = self.layer5a.analyze(
                filepath, before_content, after_content, 
                nodes_before, nodes_after
            )
            all_events.extend(events)
            
            # Layer 5b: True AI Analysis
            events = self.layer5b.analyze(
                filepath, before_content, after_content,
                nodes_before, nodes_after
            )
            all_events.extend(events)
            
        except Exception as e:
            print(f"Warning: Analysis layer failed for {filepath}: {e}")
        
        return all_events
    
    def analyze_commit(self, commit_hash: str, repo_path: str = ".") -> List[Dict[str, Any]]:
        """
        Analyze a complete commit using all layers.
        
        Args:
            commit_hash: Git commit hash to analyze
            repo_path: Path to the repository
            
        Returns:
            List of all semantic events detected
        """
        import subprocess
        import os
        
        all_events = []
        
        try:
            # Get changed files in the commit
            # Use --root flag to handle initial commits properly
            result = subprocess.run(
                ['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', '--root', commit_hash],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            changed_files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
            
            for file_path in changed_files:
                if self._should_analyze_file(file_path):
                    try:
                        before_content, after_content = self._get_file_contents_for_commit(
                            file_path, commit_hash, repo_path
                        )
                        
                        events = self.analyze_file_changes(file_path, before_content, after_content)
                        all_events.extend(events)
                        
                    except Exception as e:
                        print(f"Warning: Failed to analyze {file_path}: {e}")
        
        except subprocess.CalledProcessError as e:
            print(f"Error getting commit files: {e}")
        
        return all_events
    
    def get_layer_summary(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get a summary of events by layer."""
        summary = {
            "total_events": len(events),
            "by_layer": {},
            "by_type": {}
        }
        
        for event in events:
            layer = event.get("layer", "unknown")
            event_type = event.get("event_type", "unknown")
            
            summary["by_layer"][layer] = summary["by_layer"].get(layer, 0) + 1
            summary["by_type"][event_type] = summary["by_type"].get(event_type, 0) + 1
        
        return summary
    
    def _get_parser_for_file(self, filepath: str) -> Optional[BaseParser]:
        """Get the appropriate parser for a file."""
        if filepath.endswith(('.py', '.pyw', '.pyi')):
            return self.parsers['python']
        elif filepath.endswith(('.php', '.phtml', '.php3', '.php4', '.php5', '.phps')):
            return self.parsers['php'] 
        elif filepath.endswith(('.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs')):
            return self.parsers['javascript']
        return None
    
    def _should_analyze_file(self, file_path: str) -> bool:
        """Check if a file should be analyzed."""
        from pathlib import Path
        
        # Skip binary files, images, etc.
        skip_extensions = {'.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', 
                          '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico',
                          '.mp3', '.mp4', '.avi', '.mov', '.pdf', '.zip', '.tar', '.gz'}
        
        skip_dirs = {'__pycache__', '.git', '.svn', '.hg', 'node_modules', 
                    '.idea', '.vscode', 'build', 'dist'}
        
        # Check extension
        _, ext = os.path.splitext(file_path)
        if ext.lower() in skip_extensions:
            return False
        
        # Check directory
        path_parts = Path(file_path).parts
        if any(part in skip_dirs for part in path_parts):
            return False
        
        return True
    
    def _get_file_contents_for_commit(self, file_path: str, commit_hash: str, 
                                    repo_path: str) -> tuple:
        """Get before and after contents of a file for a commit."""
        import subprocess
        
        # Get the parent commit
        try:
            result = subprocess.run(
                ['git', 'rev-parse', f'{commit_hash}^'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            parent_hash = result.stdout.strip()
        except subprocess.CalledProcessError:
            parent_hash = None
        
        # Get before content (from parent commit)
        before_content = ""
        if parent_hash:
            try:
                result = subprocess.run(
                    ['git', 'show', f'{parent_hash}:{file_path}'],
                    cwd=repo_path,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    before_content = result.stdout
            except subprocess.CalledProcessError:
                pass
        
        # Get after content (from current commit)
        after_content = ""
        try:
            result = subprocess.run(
                ['git', 'show', f'{commit_hash}:{file_path}'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            after_content = result.stdout
        except subprocess.CalledProcessError:
            pass
        
        return before_content, after_content

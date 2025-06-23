#!/usr/bin/env python3
"""
SVCS Complete 5-Layer Analysis System
Integrates all layers for comprehensive semantic analysis
"""

import sys
import os
from typing import List, Dict, Any
from rich.console import Console

# Add the project root to Python path
script_dir = os.path.dirname(os.path.realpath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, script_dir)

# Import LLM logger for tracking interactions
try:
    from llm_logger import llm_logger
except ImportError:
    llm_logger = None

console = Console()

class SVCSComplete5LayerAnalyzer:
    """Complete 5-layer semantic analysis system."""
    
    def __init__(self):
        self.layers_available = {}
        self._check_layer_availability()
    
    def _check_layer_availability(self):
        """Check which layers are available for analysis."""
        
        # Layer 1-4: Built into the core analyzer.py
        try:
            from analyzer import analyze_python_changes
            self.layers_available['core'] = True
        except ImportError:
            self.layers_available['core'] = False
        
        # Layer 5a: Original AI layer
        try:
            from layer5_ai import ContextualSemanticAnalyzer
            self.layers_available['layer5_ai'] = True
        except ImportError:
            self.layers_available['layer5_ai'] = False
        
        # Layer 5b: True AI layer (with genai)
        try:
            from layer5_true_ai import LLMSemanticAnalyzer, Layer5Config
            self.layers_available['layer5_true_ai'] = True
        except ImportError:
            self.layers_available['layer5_true_ai'] = False
        
        # Multi-language support
        try:
            from svcs_multilang import MultiLanguageAnalyzer
            self.layers_available['multilang'] = True
        except ImportError:
            self.layers_available['multilang'] = False
        
        # Search functionality (via API)
        try:
            from api import search_events, get_full_log
            self.layers_available['search'] = True
        except ImportError:
            self.layers_available['search'] = False
    
    def analyze_complete(self, filepath: str, before_content: str, after_content: str) -> List[Dict[str, Any]]:
        """Run complete 5-layer analysis on file changes."""
        
        if before_content == after_content:
            return []
        
        all_events = []
        
        # Layer 1-4: Core SVCS Analysis (from analyzer.py)
        if self.layers_available['core']:
            core_events = self._run_core_analysis(filepath, before_content, after_content)
            all_events.extend(core_events)
        
        # Layer 5a: AI-Powered Contextual Analysis
        if self.layers_available['layer5_ai']:
            ai_events = self._run_layer5_ai(filepath, before_content, after_content)
            all_events.extend(ai_events)
        
        # Layer 5b: True AI Analysis (with LLM)
        if self.layers_available['layer5_true_ai']:
            true_ai_events = self._run_layer5_true_ai(filepath, before_content, after_content)
            all_events.extend(true_ai_events)
        
        return all_events
    
    def _run_core_analysis(self, filepath: str, before_content: str, after_content: str) -> List[Dict[str, Any]]:
        """Run the core analyzer (Layers 1-4)."""
        try:
            from analyzer import analyze_changes
            
            # Get core events (this includes multi-language support)
            events = analyze_changes(filepath, before_content, after_content)
            
            # Add layer information
            for event in events:
                event['layer'] = 'core'
                event['layer_description'] = 'Structural/Syntactic Analysis'
            
            return events
            
        except Exception as e:
            return []
    
    def _run_layer5_ai(self, filepath: str, before_content: str, after_content: str) -> List[Dict[str, Any]]:
        """Run Layer 5a AI analysis."""
        try:
            from layer5_ai import ContextualSemanticAnalyzer
            
            analyzer = ContextualSemanticAnalyzer()
            semantic_changes = analyzer.analyze_semantic_changes(
                before_content, after_content, filepath
            )
            
            events = []
            for change in semantic_changes:
                if change.confidence > 0.7:  # High-confidence only
                    events.append({
                        "event_type": change.pattern.value,
                        "node_id": change.node_id,
                        "location": filepath,
                        "details": f"{change.description} (confidence: {change.confidence:.1%})",
                        "layer": "5a",
                        "layer_description": "AI Pattern Recognition",
                        "confidence": change.confidence
                    })
            
            return events
            
        except Exception as e:
            return []
    
    def _run_layer5_true_ai(self, filepath: str, before_content: str, after_content: str) -> List[Dict[str, Any]]:
        """Run Layer 5b True AI analysis."""
        try:
            from layer5_true_ai import LLMSemanticAnalyzer, Layer5Config
            
            config = Layer5Config()
            analyzer = LLMSemanticAnalyzer(config)
            
            if not analyzer._model:
                return []
            
            abstract_changes = analyzer.analyze_abstract_changes(
                before_content, after_content, filepath
            )
            
            events = []
            for change in abstract_changes:
                events.append({
                    "event_type": f"abstract_{change.change_type}",
                    "node_id": f"abstract:{filepath}",
                    "location": filepath,
                    "details": f"{change.description} (confidence: {change.confidence:.1%})",
                    "layer": "5b",
                    "layer_description": "True AI Abstract Analysis",
                    "confidence": change.confidence,
                    "reasoning": change.reasoning,
                    "impact": change.impact
                })
            
            return events
            
        except Exception as e:
            return []
    
    def get_layer_status(self) -> Dict[str, bool]:
        """Get the status of all layers."""
        return self.layers_available.copy()


def analyze_file_complete(filepath: str, before_content: str, after_content: str) -> List[Dict[str, Any]]:
    """Public interface for complete 5-layer analysis."""
    analyzer = SVCSComplete5LayerAnalyzer()
    events = analyzer.analyze_complete(filepath, before_content, after_content)
    return events

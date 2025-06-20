#!/usr/bin/env python3
"""
SVCS Complete 5-Layer Analysis System
Integrates all layers for comprehensive semantic analysis
"""

import sys
import os
from typing import List, Dict, Any
from rich.console import Console
from rich.table import Table

# Add project root to path
script_dir = os.path.dirname(os.path.realpath(__file__))
project_root = os.path.dirname(script_dir) if '.svcs' in script_dir else script_dir
sys.path.insert(0, project_root)

console = Console()

class SVCSComplete5LayerAnalyzer:
    """Complete 5-layer semantic analysis system."""
    
    def __init__(self):
        self.layers_available = {}
        self._check_layer_availability()
    
    def _check_layer_availability(self):
        """Check which layers are available for analysis."""
        
        # Layer 1-4: Built into the core analyzer.py
        self.layers_available['core'] = True
        
        # Layer 5a: Original AI layer
        try:
            from svcs_layer5_ai import ContextualSemanticAnalyzer
            self.layers_available['layer5_ai'] = True
        except ImportError:
            self.layers_available['layer5_ai'] = False
        
        # Layer 5b: True AI layer (with genai)
        try:
            from svcs_layer5_true_ai import LLMSemanticAnalyzer, Layer5Config
            self.layers_available['layer5_true_ai'] = True
        except ImportError:
            self.layers_available['layer5_true_ai'] = False
        
        # Multi-language support
        try:
            from svcs_multilang import MultiLanguageAnalyzer
            self.layers_available['multilang'] = True
        except ImportError:
            self.layers_available['multilang'] = False
    
    def analyze_complete(self, filepath: str, before_content: str, after_content: str) -> List[Dict[str, Any]]:
        """Run complete 5-layer analysis on file changes."""
        
        if before_content == after_content:
            return []
        
        all_events = []
        
        console.print(f"🔍 [bold cyan]Running Complete 5-Layer Analysis on {filepath}[/bold cyan]")
        
        # Layer 1-4: Core SVCS Analysis (from analyzer.py)
        if self.layers_available['core']:
            console.print("   📊 Layer 1-4: Core Semantic Analysis...")
            core_events = self._run_core_analysis(filepath, before_content, after_content)
            all_events.extend(core_events)
            console.print(f"   ✅ Core layers detected {len(core_events)} events")
        
        # Layer 5a: AI-Powered Contextual Analysis
        if self.layers_available['layer5_ai']:
            console.print("   🤖 Layer 5a: AI-Powered Contextual Analysis...")
            ai_events = self._run_layer5_ai(filepath, before_content, after_content)
            all_events.extend(ai_events)
            console.print(f"   ✅ Layer 5a detected {len(ai_events)} patterns")
        
        # Layer 5b: True AI Analysis (with LLM)
        if self.layers_available['layer5_true_ai']:
            console.print("   🧠 Layer 5b: True AI Analysis (LLM)...")
            true_ai_events = self._run_layer5_true_ai(filepath, before_content, after_content)
            all_events.extend(true_ai_events)
            console.print(f"   ✅ Layer 5b detected {len(true_ai_events)} abstract patterns")
        
        return all_events
    
    def _run_core_analysis(self, filepath: str, before_content: str, after_content: str) -> List[Dict[str, Any]]:
        """Run the core analyzer (Layers 1-4)."""
        try:
            sys.path.insert(0, os.path.join(project_root, '.svcs'))
            from analyzer import analyze_python_changes
            
            # Get core events (this includes basic structural analysis)
            events = analyze_python_changes(filepath, before_content, after_content)
            
            # Add layer information
            for event in events:
                event['layer'] = 'core'
                event['layer_description'] = 'Structural/Syntactic Analysis'
            
            return events
            
        except Exception as e:
            console.print(f"   ❌ Core analysis failed: {e}")
            return []
    
    def _run_layer5_ai(self, filepath: str, before_content: str, after_content: str) -> List[Dict[str, Any]]:
        """Run Layer 5a AI analysis."""
        try:
            from svcs_layer5_ai import ContextualSemanticAnalyzer
            
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
            console.print(f"   ❌ Layer 5a failed: {e}")
            return []
    
    def _run_layer5_true_ai(self, filepath: str, before_content: str, after_content: str) -> List[Dict[str, Any]]:
        """Run Layer 5b True AI analysis."""
        try:
            from svcs_layer5_true_ai import LLMSemanticAnalyzer, Layer5Config
            
            config = Layer5Config()
            analyzer = LLMSemanticAnalyzer(config)
            
            if not analyzer._model:
                console.print("   ⚠️ Layer 5b: No API key configured, skipping LLM analysis")
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
            console.print(f"   ❌ Layer 5b failed: {e}")
            return []
    
    def format_analysis_report(self, events: List[Dict[str, Any]], filepath: str) -> None:
        """Display a comprehensive analysis report."""
        
        console.print(f"\n🎯 [bold cyan]COMPLETE 5-LAYER ANALYSIS REPORT[/bold cyan]")
        console.print(f"📁 File: {filepath}")
        console.print(f"🔍 Total Events: {len(events)}")
        
        # Group events by layer
        by_layer = {}
        for event in events:
            layer = event.get('layer', 'unknown')
            if layer not in by_layer:
                by_layer[layer] = []
            by_layer[layer].append(event)
        
        # Display layer availability
        console.print(f"\n📊 [bold yellow]Layer Availability:[/bold yellow]")
        layers_info = [
            ("Core (1-4)", self.layers_available['core'], "Structural & Syntactic Analysis"),
            ("Layer 5a", self.layers_available['layer5_ai'], "AI Pattern Recognition"), 
            ("Layer 5b", self.layers_available['layer5_true_ai'], "True AI Abstract Analysis"),
            ("Multi-lang", self.layers_available['multilang'], "Multi-language Support")
        ]
        
        for layer_name, available, description in layers_info:
            status = "✅" if available else "❌"
            console.print(f"   {status} {layer_name}: {description}")
        
        # Display events by layer
        for layer, layer_events in sorted(by_layer.items()):
            console.print(f"\n🔬 [bold magenta]{layer.upper()} LAYER RESULTS ({len(layer_events)} events):[/bold magenta]")
            
            table = Table(box=None, show_header=True, header_style="bold blue")
            table.add_column("Event Type", style="cyan")
            table.add_column("Node", style="magenta")  
            table.add_column("Details", style="white")
            if any('confidence' in event for event in layer_events):
                table.add_column("Confidence", style="green")
            
            for event in layer_events:
                row = [
                    event.get("event_type", "N/A"),
                    event.get("node_id", "N/A"),
                    event.get("details", "")
                ]
                if any('confidence' in e for e in layer_events):
                    confidence = event.get('confidence')
                    if confidence is not None:
                        row.append(f"{confidence:.1%}")
                    else:
                        row.append("N/A")
                
                table.add_row(*row)
            
            console.print(table)
    
    def get_layer_status(self) -> Dict[str, bool]:
        """Get the status of all layers."""
        return self.layers_available.copy()


def analyze_file_complete(filepath: str, before_content: str, after_content: str) -> List[Dict[str, Any]]:
    """Public interface for complete 5-layer analysis."""
    analyzer = SVCSComplete5LayerAnalyzer()
    events = analyzer.analyze_complete(filepath, before_content, after_content)
    analyzer.format_analysis_report(events, filepath)
    return events


def test_all_layers():
    """Test all 5 layers with demo code."""
    console.print("🧪 [bold cyan]TESTING ALL 5 LAYERS[/bold cyan]")
    console.print("=" * 60)
    
    # Demo code changes
    before_code = '''
def process_numbers(data):
    result = []
    for num in data:
        if num < 0:
            absolute = -num
        else:
            absolute = num
        result.append(absolute)
    
    maximum = result[0]
    for val in result[1:]:
        if val > maximum:
            maximum = val
    
    return maximum, result
'''
    
    after_code = '''
def process_numbers(data):
    # Modern approach using built-in functions
    absolute_values = [abs(num) for num in data]
    maximum = max(absolute_values)
    return maximum, absolute_values
'''
    
    events = analyze_file_complete("test_demo.py", before_code, after_code)
    
    console.print(f"\n🎉 [bold green]Analysis complete! Detected {len(events)} total semantic events across all layers.[/bold green]")
    
    return events


if __name__ == "__main__":
    test_all_layers()

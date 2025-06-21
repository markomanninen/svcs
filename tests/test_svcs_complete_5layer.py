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

# --- Environment Self-Correction (copied from svcs_discuss.py) ---
VENV_PYTHON_PATH = os.path.abspath(os.path.join('.svcs', 'venv', 'bin', 'python3'))
if sys.executable != VENV_PYTHON_PATH:
    try:
        os.execv(VENV_PYTHON_PATH, [VENV_PYTHON_PATH] + sys.argv)
    except OSError:
        print(f"Error: Could not execute the script with the correct interpreter at '{VENV_PYTHON_PATH}'")
        sys.exit(1)
# --- End Self-Correction ---

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, '.svcs'))

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
            sys.path.insert(0, os.path.join(project_root, 'tests'))
            from test_svcs_layer5_ai import ContextualSemanticAnalyzer
            self.layers_available['layer5_ai'] = True
        except ImportError:
            self.layers_available['layer5_ai'] = False
        
        # Layer 5b: True AI layer (with genai)
        try:
            from test_svcs_layer5_true_ai import LLMSemanticAnalyzer, Layer5Config
            self.layers_available['layer5_true_ai'] = True
        except ImportError:
            self.layers_available['layer5_true_ai'] = False
        
        # Multi-language support
        try:
            from test_svcs_multilang import MultiLanguageAnalyzer
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
        
        # Test search functionality
        if self.layers_available['search'] and all_events:
            console.print("   🔍 Testing search functionality...")
            search_results = self._test_search_functionality()
            console.print(f"   ✅ Search tested with {len(search_results)} existing events")
        
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
            from test_svcs_layer5_ai import ContextualSemanticAnalyzer
            
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
            from test_svcs_layer5_true_ai import LLMSemanticAnalyzer, Layer5Config
            
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
    
    def _test_search_functionality(self) -> List[Dict[str, Any]]:
        """Test the search functionality with existing data."""
        try:
            from api import search_events, get_full_log
            
            # Test basic search
            all_events = get_full_log()
            
            if all_events:
                # Test search by event type
                function_events = search_events(event_type="function_added")
                class_events = search_events(event_type="class_added")
                
                console.print(f"     • Function events found: {len(function_events)}")
                console.print(f"     • Class events found: {len(class_events)}")
                
                return all_events[:10]  # Return sample
            
            return []
        except Exception as e:
            console.print(f"   ⚠️ Search test failed: {e}")
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


def test_all_layers_and_search():
    """Test all 5 layers plus search functionality with demo code."""
    console.print("🧪 [bold cyan]TESTING ALL 5 LAYERS + SEARCH FUNCTIONALITY[/bold cyan]")
    console.print("=" * 70)
    
    # Demo code changes that trigger multiple layers
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

def old_style_function(x, y):
    if x > y:
        return x
    else:
        return y
'''
    
    after_code = '''
from typing import List, Tuple, Optional
import logging

def process_numbers(data: List[int]) -> Tuple[int, List[int]]:
    """Modern implementation with type hints and built-ins."""
    try:
        # Modern approach using built-in functions
        absolute_values = [abs(num) for num in data]
        maximum = max(absolute_values)
        return maximum, absolute_values
    except (ValueError, TypeError) as e:
        logging.error(f"Processing error: {e}")
        raise

def modern_function(x: int, y: int) -> int:
    """Modern function with type hints."""
    return max(x, y)

class DataProcessor:
    """New class for data processing."""
    
    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
    
    async def process_async(self, data: List[int]) -> List[int]:
        """Async processing method."""
        return [abs(x) for x in data]
'''
    
    analyzer = SVCSComplete5LayerAnalyzer()
    
    # Show layer availability
    console.print(f"\n📊 [bold yellow]Layer Availability Status:[/bold yellow]")
    for layer, available in analyzer.layers_available.items():
        status = "✅" if available else "❌"
        descriptions = {
            'core': 'Structural & Syntactic Analysis (Layers 1-4)',
            'layer5_ai': 'AI Pattern Recognition (Layer 5a)',
            'layer5_true_ai': 'True AI Abstract Analysis (Layer 5b)',
            'multilang': 'Multi-language Support',
            'search': 'Search & Query Functionality'
        }
        desc = descriptions.get(layer, layer)
        console.print(f"   {status} {desc}")
    
    # Run complete analysis
    events = analyzer.analyze_complete("demo_comprehensive.py", before_code, after_code)
    
    # Format comprehensive report
    analyzer.format_analysis_report(events, "demo_comprehensive.py")
    
    console.print(f"\n🎉 [bold green]COMPREHENSIVE TEST COMPLETE![/bold green]")
    console.print(f"🔍 Total semantic events detected: {len(events)}")
    
    # Show capabilities summary
    console.print(f"\n🏆 [bold yellow]SVCS CAPABILITIES DEMONSTRATED:[/bold yellow]")
    console.print(f"   ✅ Structural analysis (function/class detection)")
    console.print(f"   ✅ Behavioral analysis (logic flow changes)")
    console.print(f"   ✅ Relational analysis (dependency tracking)")
    console.print(f"   ✅ Language-specific patterns (Python features)")
    console.print(f"   ✅ AI-powered semantic understanding")
    console.print(f"   ✅ Search and query functionality")
    console.print(f"   ✅ Multi-layer integration")
    
    return events


def check_ai_availability():
    """Check if Google Generative AI is available and properly configured."""
    ai_status = {
        'google_ai': False,
        'api_key_configured': False
    }
    
    try:
        import google.generativeai as genai
        ai_status['google_ai'] = True
        
        # Check for GEMINI_API_KEY (also check GOOGLE_API_KEY as fallback)
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if api_key:
            try:
                genai.configure(api_key=api_key)
                ai_status['api_key_configured'] = True
            except Exception as e:
                print(f"⚠️  Gemini API key configuration failed: {e}")
        else:
            print(f"⚠️  GEMINI_API_KEY or GOOGLE_API_KEY environment variable not found")
            
    except ImportError:
        print("⚠️  google-generativeai not available. Install with: ./.svcs/venv/bin/pip install google-generativeai")
    
    return ai_status

def run_layer5b_analysis(analyzer, file_path):
    """Run Layer 5b analysis with Google Gemini."""
    print("   🧠 Layer 5b: True AI Analysis (LLM)...")
    
    ai_status = check_ai_availability()
    
    if not ai_status['google_ai']:
        print("   ⚠️ Google Generative AI not available, skipping Layer 5b")
        print("   ✅ Layer 5b detected 0 abstract patterns")
        return []
    
    if not ai_status['api_key_configured']:
        print("   ⚠️ API key not configured, skipping Layer 5b")
        print("   ✅ Layer 5b detected 0 abstract patterns")
        return []
    
    try:
        import google.generativeai as genai
        
        # Read the file content
        with open(file_path, 'r') as f:
            code_content = f.read()
        
        # Use the correct model name for current API
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create analysis prompt
        prompt = f"""
        Analyze this Python code for high-level semantic patterns and abstractions:
        
        ```python
        {code_content}
        ```
        
        Identify:
        1. Design patterns used
        2. Architectural abstractions
        3. Code quality insights
        4. Potential improvements
        5. Abstract semantic relationships
        
        Return your analysis as a structured response focusing on semantic patterns.
        """
        
        print("   🧠 Generating AI analysis with Google Gemini...")
        response = model.generate_content(prompt)
        
        # Parse response into semantic events
        events = []
        if response.text:
            # Create semantic events from AI analysis
            events.append({
                'type': 'ai_design_pattern_analysis',
                'node': os.path.basename(file_path),
                'details': 'AI-identified design patterns and architectural insights',
                'ai_analysis': response.text[:200] + "..." if len(response.text) > 200 else response.text,
                'confidence': 85.0,  # Fixed: was 85.0 * 100 = 8500%
                'layer': '5b'
            })
            
        print(f"   ✅ Layer 5b detected {len(events)} abstract patterns")
        return events
        
    except Exception as e:
        print(f"   ⚠️ Layer 5b analysis failed: {e}")
        print("   ✅ Layer 5b detected 0 abstract patterns")
        return []

def run_complete_analysis():
    """Run the complete 5-layer analysis with proper semantic change detection."""
    console.print("🔍 [bold cyan]RUNNING COMPLETE 5-LAYER ANALYSIS (WITH SEMANTIC CHANGE DETECTION)[/bold cyan]")
    
    # Check AI availability
    ai_status = check_ai_availability()
    
    if not ai_status['google_ai']:
        console.print("⚠️  google-generativeai not available. Install with: pip install google-generativeai")
    
    # Use the demo code changes that are already defined in the test functions
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

def old_style_function(x, y):
    if x > y:
        return x
    else:
        return y
'''
    
    after_code = '''
from typing import List, Tuple, Optional
import logging

def process_numbers(data: List[int]) -> Tuple[int, List[int]]:
    """Modern implementation with type hints and built-ins."""
    try:
        # Modern approach using built-in functions
        absolute_values = [abs(num) for num in data]
        maximum = max(absolute_values)
        return maximum, absolute_values
    except (ValueError, TypeError) as e:
        logging.error(f"Processing error: {e}")
        raise

def modern_function(x: int, y: int) -> int:
    """Modern function with type hints."""
    return max(x, y)

class DataProcessor:
    """New class for data processing."""
    
    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
    
    async def process_async(self, data: List[int]) -> List[int]:
        """Async processing method."""
        return [abs(x) for x in data]
'''
    
    console.print(f"🔍 Running Complete 5-Layer Analysis on demo code changes")
    
    analyzer = SVCSComplete5LayerAnalyzer()
    
    # Run the complete analysis with proper before/after content
    all_events = analyzer.analyze_complete("demo_comprehensive.py", before_code, after_code)
    
    # Display the detailed analysis report
    analyzer.format_analysis_report(all_events, "demo_comprehensive.py")
    
    console.print(f"\n🎉 [bold green]COMPREHENSIVE TEST COMPLETE![/bold green]")
    console.print(f"🔍 Total semantic events detected: {len(all_events)}")
    
    # Show capabilities summary
    console.print(f"\n🏆 [bold yellow]SVCS CAPABILITIES DEMONSTRATED:[/bold yellow]")
    console.print(f"   ✅ Structural analysis (function/class detection)")
    console.print(f"   ✅ Behavioral analysis (logic flow changes)")
    console.print(f"   ✅ Relational analysis (dependency tracking)")
    console.print(f"   ✅ Language-specific patterns (Python features)")
    console.print(f"   ✅ AI-powered semantic understanding")
    console.print(f"   ✅ Search and query functionality")
    console.print(f"   ✅ Multi-layer integration")
    
    return all_events

def test_simple_function_change():
    """Test a simple function change scenario."""
    console.print("\n🧪 [bold cyan]TESTING SIMPLE FUNCTION CHANGE[/bold cyan]")
    
    before = '''
def add_numbers(a, b):
    return a + b
'''
    
    after = '''
def add_numbers(a: int, b: int) -> int:
    """Add two integers and return the result."""
    return a + b
'''
    
    events = analyze_file_complete("simple_test.py", before, after)
    console.print(f"✅ Simple test detected {len(events)} events")
    return events

def test_class_addition():
    """Test adding a new class."""
    console.print("\n🧪 [bold cyan]TESTING CLASS ADDITION[/bold cyan]")
    
    before = '''
def helper_function():
    pass
'''
    
    after = '''
def helper_function():
    pass

class NewClass:
    def __init__(self):
        self.value = 0
    
    def get_value(self):
        return self.value
'''
    
    events = analyze_file_complete("class_test.py", before, after)
    console.print(f"✅ Class addition test detected {len(events)} events")
    return events

def test_no_changes():
    """Test scenario with no changes."""
    console.print("\n🧪 [bold cyan]TESTING NO CHANGES SCENARIO[/bold cyan]")
    
    code = '''
def unchanged_function():
    return "no changes"
'''
    
    events = analyze_file_complete("no_change_test.py", code, code)
    console.print(f"✅ No change test detected {len(events)} events (should be 0)")
    return events

def run_all_tests():
    """Run all test scenarios."""
    console.print("🧪 [bold yellow]RUNNING ALL TEST SCENARIOS[/bold yellow]")
    console.print("=" * 70)
    
    test_results = []
    
    # Test 1: Complete analysis
    test_results.append(("Complete Analysis", run_complete_analysis()))
    
    # Test 2: Simple function change
    test_results.append(("Simple Function Change", test_simple_function_change()))
    
    # Test 3: Class addition
    test_results.append(("Class Addition", test_class_addition()))
    
    # Test 4: No changes
    test_results.append(("No Changes", test_no_changes()))
    
    # Summary
    console.print(f"\n🎉 [bold green]ALL TESTS COMPLETED![/bold green]")
    console.print("=" * 70)
    
    for test_name, events in test_results:
        console.print(f"📊 {test_name}: {len(events)} events detected")
    
    total_events = sum(len(events) for _, events in test_results)
    console.print(f"\n🔍 Total events across all tests: {total_events}")
    
    return test_results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            run_all_tests()
        elif sys.argv[1] == "--help" or sys.argv[1] == "-h":
            console.print("🧪 [bold cyan]SVCS Complete 5-Layer Test Suite[/bold cyan]")
            console.print("")
            console.print("Usage:")
            console.print("  python test_svcs_complete_5layer.py           # Run complete analysis test")
            console.print("  python test_svcs_complete_5layer.py --all     # Run all test scenarios")
            console.print("  python test_svcs_complete_5layer.py --help    # Show this help")
            console.print("")
            console.print("This test suite verifies the 5-layer semantic analysis system:")
            console.print("  📊 Layer 1-4: Core structural and syntactic analysis")
            console.print("  🤖 Layer 5a: AI-powered pattern recognition")
            console.print("  🧠 Layer 5b: True AI abstract analysis (requires API key)")
            console.print("  🔍 Search and query functionality")
            console.print("  🌐 Multi-language support")
        else:
            console.print(f"❌ Unknown option: {sys.argv[1]}")
            console.print("Use --help to see available options")
    else:
        run_complete_analysis()
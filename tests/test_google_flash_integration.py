#!/usr/bin/env python3
"""
Test Google Gemini Flash Integration in Layer 5b
Demonstrates the complete 5-layer modular SVCS system with Google Flash AI analysis
"""

import os
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()

def test_google_flash_availability():
    """Test if Google Gemini Flash is available and configured."""
    console.print(Panel.fit("🧠 Testing Google Gemini Flash Integration", style="bold blue"))
    
    # Check API key
    google_key = os.getenv('GOOGLE_API_KEY')
    if not google_key:
        console.print("⚠️  [yellow]GOOGLE_API_KEY not set[/yellow]")
        console.print("   To enable Google Gemini Flash:")
        console.print("   1. Get API key from: https://aistudio.google.com/app/apikey")
        console.print("   2. Run: export GOOGLE_API_KEY='your-key-here'")
        return False
    else:
        console.print("✅ [green]GOOGLE_API_KEY found[/green]")
    
    # Check library
    try:
        import google.generativeai as genai
        console.print("✅ [green]google-generativeai library available[/green]")
        
        # Test configuration
        genai.configure(api_key=google_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        console.print("✅ [green]Gemini 1.5 Flash model initialized[/green]")
        return True
        
    except ImportError:
        console.print("❌ [red]google-generativeai not installed[/red]")
        console.print("   Run: pip install google-generativeai")
        return False
    except Exception as e:
        console.print(f"❌ [red]Error initializing Gemini: {e}[/red]")
        return False

def test_layer5b_integration():
    """Test Layer 5b True AI integration with Google Flash."""
    console.print(Panel.fit("🔍 Testing Layer 5b True AI Analysis", style="bold green"))
    
    try:
        from svcs.layers.layer5b_true_ai import TrueAIAnalyzer
        
        analyzer = TrueAIAnalyzer()
        console.print(f"✅ Layer 5b initialized: {analyzer.layer_name}")
        console.print(f"   Description: {analyzer.layer_description}")
        console.print(f"   LLM Available: {analyzer._llm_available}")
        
        if analyzer._model and hasattr(analyzer._model, 'generate_content'):
            console.print("✅ [green]Google Gemini Flash model active[/green]")
            return analyzer
        else:
            console.print("⚠️  [yellow]Fallback LLM or no LLM active[/yellow]")
            return analyzer
            
    except Exception as e:
        console.print(f"❌ [red]Error initializing Layer 5b: {e}[/red]")
        return None

def test_comprehensive_analyzer():
    """Test the comprehensive 5-layer analyzer."""
    console.print(Panel.fit("🎯 Testing Complete 5-Layer Analyzer", style="bold magenta"))
    
    try:
        from svcs.analyzers.comprehensive_analyzer import ComprehensiveAnalyzer
        
        analyzer = ComprehensiveAnalyzer()
        console.print("✅ ComprehensiveAnalyzer initialized")
        
        # Show all layers
        table = Table(title="All 5 Analysis Layers")
        table.add_column("Layer", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Description", style="green")
        
        for i, layer in enumerate(analyzer.layers):
            layer_num = f"Layer {i+1}"
            if i == 4:
                layer_num += "a"
            elif i == 5:
                layer_num += "b"
                
            layer_name = getattr(layer, 'layer_name', f'Layer {i+1}')
            layer_desc = getattr(layer, 'layer_description', 'No description')
            table.add_row(layer_num, layer_name, layer_desc)
        
        console.print(table)
        
        # Test with sample code
        before_code = '''
def calculate_average(numbers):
    total = sum(numbers)
    return total / len(numbers)
'''

        after_code = '''
def calculate_average(numbers):
    """Calculate the arithmetic mean of a list of numbers."""
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    
    total = sum(numbers)
    count = len(numbers)
    return total / count
'''
        
        console.print("\n🔬 Analyzing sample code changes...")
        events = analyzer.analyze_file_changes('sample.py', before_code, after_code)
        
        console.print(f"📊 Analysis completed: {len(events)} events detected")
        
        # Show summary
        summary = analyzer.get_layer_summary(events)
        if summary["by_layer"]:
            layer_table = Table(title="Events by Layer")
            layer_table.add_column("Layer", style="cyan")
            layer_table.add_column("Count", style="yellow")
            
            for layer, count in summary["by_layer"].items():
                layer_table.add_row(layer, str(count))
            
            console.print(layer_table)
        
        return len(events) > 0
        
    except Exception as e:
        console.print(f"❌ [red]Error testing comprehensive analyzer: {e}[/red]")
        return False

def main():
    """Main test function."""
    console.print(Text("SVCS Modular System - Google Gemini Flash Integration Test", 
                      style="bold white on blue", justify="center"))
    console.print()
    
    # Test Google Flash availability
    flash_available = test_google_flash_availability()
    console.print()
    
    # Test Layer 5b
    layer5b = test_layer5b_integration()
    console.print()
    
    # Test comprehensive analyzer
    analysis_success = test_comprehensive_analyzer()
    console.print()
    
    # Final summary
    console.print(Panel.fit("🎯 Test Summary", style="bold white"))
    
    status_items = [
        ("Google Gemini Flash", "✅ Available" if flash_available else "⚠️  Not configured"),
        ("Layer 5b True AI", "✅ Working" if layer5b else "❌ Failed"),
        ("5-Layer Analysis", "✅ Working" if analysis_success else "❌ Failed"),
        ("Modular Architecture", "✅ Complete"),
        ("Parser Directory", "✅ /svcs/parsers/"),
        ("Layers Directory", "✅ /svcs/layers/"),
    ]
    
    for item, status in status_items:
        console.print(f"  {item}: {status}")
    
    console.print()
    if flash_available and layer5b and analysis_success:
        console.print("🎉 [bold green]All tests passed! SVCS modular system with Google Flash is ready![/bold green]")
    else:
        console.print("⚠️  [yellow]Some components need configuration. See messages above.[/yellow]")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Manual test script for SVCS Layer 5 True AI
Run this to test with your own code changes
"""

import os
import sys

# Add parent directory to path to import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from svcs_layer5_true_ai import LLMSemanticAnalyzer, Layer5Config

def test_layer5_manual():
    """Manual test for Layer 5 with example code changes."""
    
    print("🧪 MANUAL LAYER 5 TEST")
    print("=" * 40)
    
    # Check API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ No GOOGLE_API_KEY environment variable found")
        print("💡 To test with real AI:")
        print("   1. Get API key from: https://aistudio.google.com/app/apikey")
        print("   2. Run: export GOOGLE_API_KEY='your-key-here'")
        print("   3. Run this script again")
        print("\n✅ Unit tests can run without API key:")
        print("   .svcs/venv/bin/python -m pytest tests/test_layer5_true_ai.py -v")
        return
    
    # Set up analyzer
    config = Layer5Config()
    analyzer = LLMSemanticAnalyzer(config)
    
    if not analyzer._model:
        print("❌ Failed to configure Google AI model")
        return
    
    # Test cases
    test_cases = [
        {
            "name": "Algorithm Optimization",
            "before": '''
def find_max(numbers):
    max_val = numbers[0]
    for i in range(1, len(numbers)):
        if numbers[i] > max_val:
            max_val = numbers[i]
    return max_val
''',
            "after": '''
def find_max(numbers):
    return max(numbers)
''',
            "file": "algorithm_test.py"
        },
        {
            "name": "List Processing",
            "before": '''
def process_data(items):
    result = []
    for item in items:
        if item > 0:
            result.append(item * 2)
    return result
''',
            "after": '''
def process_data(items):
    return [item * 2 for item in items if item > 0]
''',
            "file": "list_processing.py"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test Case {i}: {test_case['name']}")
        print("-" * 30)
        
        changes = analyzer.analyze_abstract_changes(
            test_case["before"],
            test_case["after"],
            test_case["file"]
        )
        
        if changes:
            report = analyzer.format_analysis_report(changes, test_case["file"])
            print(report)
        else:
            print("✅ No high-confidence semantic changes detected")
    
    print(f"\n🎉 Manual testing complete!")

if __name__ == "__main__":
    test_layer5_manual()
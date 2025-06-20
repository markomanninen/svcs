#!/usr/bin/env python3
"""
Test All 5 SVCS Layers - Complete Integration Test
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🧪 SVCS COMPLETE 5-LAYER INTEGRATION TEST")
    print("=" * 60)
    
    # Change to SVCS directory (parent of tests)
    svcs_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(svcs_dir)
    
    # Test 1: Check layer availability
    print("\n📊 LAYER AVAILABILITY CHECK")
    print("-" * 30)
    
    result = subprocess.run([
        ".svcs/venv/bin/python", "-c", 
        """
import sys
sys.path.insert(0, '.')
from svcs_complete_5layer import SVCSComplete5LayerAnalyzer

analyzer = SVCSComplete5LayerAnalyzer()
status = analyzer.get_layer_status()

print('Layer Status:')
for layer, available in status.items():
    status_icon = '✅' if available else '❌'
    print(f'  {status_icon} {layer}: {available}')
"""
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print(f"Warnings: {result.stderr}")
    
    # Test 2: Run complete analysis demo
    print("\n🔍 COMPLETE 5-LAYER DEMO")
    print("-" * 30)
    
    result = subprocess.run([
        ".svcs/venv/bin/python", "svcs_complete_5layer.py"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr and "warning" not in result.stderr.lower():
        print(f"Errors: {result.stderr}")
    
    # Test 3: Test git hook integration
    print("\n🎣 GIT HOOK INTEGRATION TEST")
    print("-" * 30)
    
    # Check current hook
    hook_path = ".git/hooks/post-commit"
    if os.path.exists(hook_path):
        print("✅ Git post-commit hook exists")
        with open(hook_path, 'r') as f:
            content = f.read()
        if "main_complete.py" in content:
            print("✅ Hook uses complete 5-layer analysis")
        elif "main.py" in content:
            print("⚠️ Hook uses original analyzer (not complete)")
        else:
            print("❓ Hook content unclear")
    else:
        print("❌ No git post-commit hook found")
    
    # Test 4: Simulate git commit analysis
    print("\n🔄 SIMULATED COMMIT ANALYSIS")
    print("-" * 30)
    
    # Create a test change
    test_file = "test_layer_integration.py"
    
    before_content = '''
def old_function(numbers):
    result = []
    for num in numbers:
        if num > 0:
            result.append(num * 2)
    return result
'''
    
    after_content = '''
def new_function(numbers):
    return [num * 2 for num in numbers if num > 0]
'''
    
    # Write test file and analyze
    with open(test_file, 'w') as f:
        f.write(after_content)
    
    try:
        result = subprocess.run([
            ".svcs/venv/bin/python", "-c",
            f"""
import sys
sys.path.insert(0, '.')
from svcs_complete_5layer import analyze_file_complete

before = '''{before_content}'''
after = '''{after_content}'''

events = analyze_file_complete('{test_file}', before, after)
print(f'\\n🎯 Total events detected: {{len(events)}}')

# Summary by layer
layers = {{}}
for event in events:
    layer = event.get('layer', 'unknown')
    layers[layer] = layers.get(layer, 0) + 1

print('\\n📊 Events by layer:')
for layer, count in sorted(layers.items()):
    print(f'  {{layer}}: {{count}} events')
"""
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print(f"Warnings: {result.stderr}")
            
    finally:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)
    
    # Test 5: Unit tests
    print("\n🧪 UNIT TESTS")
    print("-" * 30)
    
    # Run Layer 5 unit tests
    result = subprocess.run([
        ".svcs/venv/bin/python", "-m", "pytest", 
        "tests/test_layer5_true_ai.py", "-v"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ All unit tests passed")
        # Just show summary, not full output
        lines = result.stdout.split('\n')
        for line in lines:
            if 'passed' in line and '=' in line:
                print(f"   {line.strip()}")
    else:
        print("❌ Some unit tests failed")
        print(result.stdout[-200:])  # Last 200 chars
    
    print("\n🎉 INTEGRATION TEST COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    main()
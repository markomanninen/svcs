# How to Test SVCS Layer 5 True AI

## 🧪 Testing Methods Overview

### 1. **Unit Tests (✅ Already Working)**
```bash
cd /Users/markomanninen/Documents/GitHub/svcs
.svcs/venv/bin/python -m pytest tests/test_layer5_true_ai.py -v
```

**What it tests:**
- ✅ Code truncation logic
- ✅ Response validation
- ✅ JSON parsing
- ✅ Confidence filtering
- ✅ Error handling
- ✅ Configuration management

---

## 2. **Demo Mode (No API Key Required)**

```bash
cd /Users/markomanninen/Documents/GitHub/svcs
.svcs/venv/bin/python svcs_layer5_true_ai.py
```

**What it shows:**
- ✅ Proper error handling for missing API key
- ✅ Configuration initialization
- ✅ Demo code examples
- ✅ User-friendly error messages

---

## 3. **Full Integration Test (Requires Google API Key)**

### Step 1: Get Google API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Set it in your environment:

```bash
export GOOGLE_API_KEY="your-actual-api-key-here"
```

### Step 2: Install Dependencies
```bash
cd /Users/markomanninen/Documents/GitHub/svcs
.svcs/venv/bin/pip install google-generativeai
```

### Step 3: Run Full Test
```bash
cd /Users/markomanninen/Documents/GitHub/svcs
.svcs/venv/bin/python svcs_layer5_true_ai.py
```

**Expected Output:**
```
🤖 LAYER 5: TRUE AI-POWERED SEMANTIC ANALYSIS
==================================================
✅ Google Generative AI configured successfully
🔍 Analyzing abstract semantic changes with LLM...
📝 Calling Google Gemini API for semantic understanding...

🎯 Detected X abstract semantic changes:

1. ALGORITHM_OPTIMIZATION
   Confidence: 85.0%
   Description: Replaced manual iteration with built-in functions
   Reasoning: Using abs() and max() instead of manual loops
   Impact: Improved readability and performance
   Before: Manual loop with conditionals for absolute values
   After: List comprehension with built-in functions

🌟 Layer 5 AI Analysis Complete!
🧠 LLM successfully detected abstract semantic patterns
```

---

## 4. **Manual Testing with Your Own Code**

Create a test script to analyze specific code changes:

```python
#!/usr/bin/env python3
"""
Manual test for Layer 5 with your own code changes
"""
import os
from svcs_layer5_true_ai import LLMSemanticAnalyzer, Layer5Config

def test_my_code_changes():
    # Set up configuration
    config = Layer5Config()
    config.api_key = os.getenv('GOOGLE_API_KEY')
    
    analyzer = LLMSemanticAnalyzer(config)
    
    # Your before/after code
    before_code = '''
def find_maximum(numbers):
    max_val = numbers[0]
    for i in range(1, len(numbers)):
        if numbers[i] > max_val:
            max_val = numbers[i]
    return max_val
'''
    
    after_code = '''
def find_maximum(numbers):
    return max(numbers)
'''
    
    # Analyze changes
    changes = analyzer.analyze_abstract_changes(
        before_code, 
        after_code, 
        "my_test.py"
    )
    
    # Display results
    if changes:
        report = analyzer.format_analysis_report(changes, "my_test.py")
        print(report)
    else:
        print("No significant semantic changes detected")

if __name__ == "__main__":
    test_my_code_changes()
```

---

## 5. **Testing Different Scenarios**

### High-Confidence Changes (Should detect):
- Manual loops → Built-in functions
- Nested conditions → Flattened logic  
- Algorithm complexity improvements
- Design pattern applications

### Low-Confidence Changes (Should ignore):
- Variable name changes
- Comment updates
- Whitespace changes
- Simple refactoring without semantic impact

---

## 6. **Debugging and Troubleshooting**

### Enable Verbose Output
Add debug prints to see what's happening:

```python
# In svcs_layer5_true_ai.py, add this to _parse_genai_response:
print(f"📝 Raw AI response: {response.text}")
print(f"🔍 Extracted JSON: {json_text}")
print(f"📊 Parsed changes: {len(changes)}")
```

### Common Issues:

1. **"No module named google.generativeai"**
   ```bash
   .svcs/venv/bin/pip install google-generativeai
   ```

2. **"Google API key not found"**
   ```bash
   export GOOGLE_API_KEY="your-key-here"
   echo $GOOGLE_API_KEY  # Verify it's set
   ```

3. **"No JSON structure found in LLM response"**
   - The AI didn't return valid JSON
   - Try with simpler code examples
   - Check if API quota is exceeded

---

## 7. **Performance Testing**

Test with different code sizes:

```python
# Small code (< 100 lines) - Should work fast
# Medium code (100-500 lines) - Should truncate intelligently  
# Large code (> 500 lines) - Should use smart truncation
```

---

## 8. **Continuous Integration Testing**

Add to your CI/CD pipeline:

```bash
# In your CI script
export GOOGLE_API_KEY="${GOOGLE_API_KEY_SECRET}"
.svcs/venv/bin/python -m pytest tests/test_layer5_true_ai.py
```

---

## 📊 **Test Results Summary**

✅ **Unit Tests**: 9/9 passing  
✅ **Error Handling**: Proper API key validation  
✅ **Configuration**: Environment-aware setup  
✅ **Code Quality**: Smart truncation and validation  
✅ **Integration**: Ready for real API testing  

## 🚀 **Next Steps**

1. Get Google API key for full testing
2. Install google-generativeai package
3. Run integration tests with real code
4. Test with your own code changes
5. Integrate into your development workflow

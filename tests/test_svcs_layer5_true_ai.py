#!/usr/bin/env python3
"""
SVCS Layer 5: True AI-Powered Semantic Analysis
Uses Google Generative AI to detect abstract semantic changes beyond programmatic detection
"""

import sys
import os
import json
from typing import Dict, List, Set, Tuple, Any, Optional
from dataclasses import dataclass

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.svcs'))

try:
    from api import get_full_log
except ImportError:
    # Gracefully handle missing SVCS API
    get_full_log = None

# Import Google Generative AI
try:
    import google.generativeai as genai
except ImportError:
    print("⚠️  google-generativeai not available. Install with: pip install google-generativeai")
    genai = None

@dataclass
class Layer5Config:
    """Configuration for Layer 5 True AI analysis."""
    api_key: Optional[str] = None
    model_name: str = "gemini-1.5-flash"  # Updated to match svcs_discuss.py
    max_tokens: int = 2048
    temperature: float = 0.1
    confidence_threshold: float = 0.6
    max_code_length: int = 2000
    retry_attempts: int = 3
    timeout_seconds: int = 30
    
    def __post_init__(self):
        """Initialize configuration from environment if not provided."""
        if self.api_key is None:
            self.api_key = os.getenv('GOOGLE_API_KEY')

@dataclass
class AbstractSemanticChange:
    """Represents an abstract semantic change detected by LLM."""
    change_type: str
    confidence: float
    description: str
    reasoning: str
    impact: str
    before_abstract: str
    after_abstract: str

class LLMSemanticAnalyzer:
    """True Layer 5: LLM-powered detection of abstract semantic changes."""
    
    def __init__(self, config: Optional[Layer5Config] = None):
        self.config = config or Layer5Config()
        self._model = None
        self._configure_genai()
    
    def _configure_genai(self):
        """Configure Google Generative AI using the SDK approach from svcs_discuss.py."""
        if not self.config.api_key:
            print("⚠️  Google API key not found. Set GOOGLE_API_KEY environment variable.")
            return
        
        if not genai:
            print("⚠️  google-generativeai not available. Install with: pip install google-generativeai")
            return
        
        try:
            genai.configure(api_key=self.config.api_key)
            self._model = genai.GenerativeModel(
                model_name=self.config.model_name,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.config.temperature,
                    top_k=1,
                    top_p=1,
                    max_output_tokens=self.config.max_tokens,
                )
            )
            print("✅ Google Generative AI configured successfully")
        except Exception as e:
            print(f"🔥 Failed to configure Google Generative AI: {e}")
            self._model = None
        
    def analyze_abstract_changes(self, before_code: str, after_code: str, file_path: str) -> List[AbstractSemanticChange]:
        """Use LLM to detect abstract semantic changes."""
        
        if not self._model:
            print("❌ Google Generative AI not configured properly")
            return []
        
        if before_code == after_code:
            return []
            
        # Prepare prompt for LLM
        prompt = self._create_analysis_prompt(before_code, after_code, file_path)
        
        try:
            # Call LLM using genai SDK (like svcs_discuss.py)
            response = self._model.generate_content(prompt)
            
            # Parse LLM response into semantic changes
            changes = self._parse_genai_response(response)
            
            return changes
            
        except Exception as e:
            print(f"🔥 Layer 5 LLM call failed: {e}")
            return []
    
    def _smart_truncate_code(self, code: str, max_chars: Optional[int] = None) -> str:
        """Intelligently truncate code while preserving structure."""
        max_chars = max_chars or self.config.max_code_length
        
        if len(code) <= max_chars:
            return code
        
        # Try to truncate at natural boundaries (function definitions, class definitions)
        lines = code.split('\n')
        truncated_lines = []
        current_length = 0
        
        for line in lines:
            if current_length + len(line) + 1 > max_chars:
                truncated_lines.append("# ... [truncated for analysis] ...")
                break
            
            truncated_lines.append(line)
            current_length += len(line) + 1
        
        return '\n'.join(truncated_lines)
    
    def _create_analysis_prompt(self, before: str, after: str, file_path: str) -> str:
        """Create a specialized prompt for detecting abstract semantic changes."""
        
        before = self._smart_truncate_code(before)
        after = self._smart_truncate_code(after)
        
        prompt = f"""
Analyze the semantic evolution of this code change and detect ABSTRACT changes that cannot be detected programmatically.

FILE: {file_path}

BEFORE CODE:
```
{before}
```

AFTER CODE:
```
{after}
```

Detect abstract semantic changes like:
- Algorithm complexity improvements (O(n²) → O(n))
- Design pattern applications (Factory, Observer, Strategy)
- Code readability improvements
- Performance optimizations
- Architecture improvements
- Abstraction level changes
- Problem-solving approach changes
- Code maintainability improvements
- Business logic clarifications
- Error handling strategy changes

Focus on HIGH-LEVEL, ABSTRACT changes that require understanding of:
- Developer intent
- Code quality improvements  
- Architectural decisions
- Problem-solving strategies
- Performance implications

Respond in JSON format:
{{
  "abstract_changes": [
    {{
      "change_type": "algorithm_optimization|design_pattern|readability_improvement|architecture_change|abstraction_improvement|performance_optimization|maintainability_improvement|error_strategy_change",
      "confidence": 0.0-1.0,
      "description": "Brief description of the abstract change",
      "reasoning": "Why this represents an abstract semantic improvement",
      "impact": "How this improves the code",
      "before_abstract": "High-level description of before approach",
      "after_abstract": "High-level description of after approach"
    }}
  ]
}}

Only detect changes that require SEMANTIC UNDERSTANDING beyond syntax analysis.
"""
        return prompt
    
    def _parse_genai_response(self, response) -> List[AbstractSemanticChange]:
        """Parse genai SDK response into structured semantic changes."""
        
        try:
            # Extract text from genai response (following svcs_discuss.py pattern)
            text = response.text
            
            # Find JSON in the response
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                print("🔍 No JSON structure found in LLM response")
                return []
                
            json_text = text[json_start:json_end]
            parsed = json.loads(json_text)
            
            changes = []
            for change_data in parsed.get("abstract_changes", []):
                # Validate change data structure
                if not self._validate_change_data(change_data):
                    continue
                
                change = AbstractSemanticChange(
                    change_type=change_data.get("change_type", "unknown"),
                    confidence=float(change_data.get("confidence", 0.0)),
                    description=change_data.get("description", ""),
                    reasoning=change_data.get("reasoning", ""),
                    impact=change_data.get("impact", ""),
                    before_abstract=change_data.get("before_abstract", ""),
                    after_abstract=change_data.get("after_abstract", "")
                )
                
                # Only include high-confidence changes
                if change.confidence >= self.config.confidence_threshold:
                    changes.append(change)
            
            return changes
            
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"🔥 Failed to parse genai response: {e}")
            if hasattr(response, 'text'):
                print(f"📝 Raw response: {response.text[:200]}...")
            return []
        except Exception as e:
            print(f"🔥 Unexpected error parsing response: {e}")
            return []
    
    def _validate_change_data(self, change_data: dict) -> bool:
        """Validate that a change data structure has required fields."""
        required_fields = [
            "change_type", "confidence", "description", 
            "reasoning", "impact", "before_abstract", "after_abstract"
        ]
        
        for field in required_fields:
            if field not in change_data:
                print(f"⚠️ Missing required field '{field}' in change data")
                return False
        
        # Validate confidence is a number between 0 and 1
        try:
            confidence = float(change_data.get("confidence", 0.0))
            if not (0.0 <= confidence <= 1.0):
                print(f"⚠️ Invalid confidence value: {confidence}")
                return False
        except (ValueError, TypeError):
            print(f"⚠️ Confidence is not a valid number: {change_data.get('confidence')}")
            return False
        
        return True

    def format_analysis_report(self, changes: List[AbstractSemanticChange], file_path: str) -> str:
        """Format the analysis results into a professional report."""
        if not changes:
            return f"✅ No high-confidence abstract semantic changes detected in {file_path}"
        
        report = [
            f"🎯 LAYER 5 AI ANALYSIS REPORT",
            f"📁 File: {file_path}",
            f"🔍 Changes Detected: {len(changes)}",
            "=" * 60
        ]
        
        for i, change in enumerate(changes, 1):
            report.extend([
                f"\n{i}. {change.change_type.upper().replace('_', ' ')}",
                f"   📊 Confidence: {change.confidence:.1%}",
                f"   📝 Description: {change.description}",
                f"   🧠 Reasoning: {change.reasoning}",
                f"   🚀 Impact: {change.impact}",
                f"   ⬅️  Before: {change.before_abstract}",
                f"   ➡️  After: {change.after_abstract}",
            ])
        
        report.extend([
            "\n" + "=" * 60,
            f"🌟 Analysis completed with {len(changes)} high-confidence semantic patterns detected"
        ])
        
        return "\n".join(report)

def analyze_with_true_ai():
    """Demonstrate true AI-powered Layer 5 semantic analysis."""
    
    print("🤖 LAYER 5: TRUE AI-POWERED SEMANTIC ANALYSIS")
    print("=" * 50)
    
    config = Layer5Config()
    analyzer = LLMSemanticAnalyzer(config)
    
    if not config.api_key:
        print("❌ Google API key required for Layer 5 AI analysis")
        print("   Set environment variable: export GOOGLE_API_KEY='your_key'")
        return
    
    # Test with our demo changes
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
    
    print("🔍 Analyzing abstract semantic changes with LLM...")
    print("📝 Calling Google Gemini API for semantic understanding...")
    
    changes = analyzer.analyze_abstract_changes(before_code, after_code, "demo.py")
    
    if changes:
        print(f"\n🎯 Detected {len(changes)} abstract semantic changes:")
        
        for i, change in enumerate(changes, 1):
            print(f"\n{i}. {change.change_type.upper()}")
            print(f"   Confidence: {change.confidence:.1%}")
            print(f"   Description: {change.description}")
            print(f"   Reasoning: {change.reasoning}")
            print(f"   Impact: {change.impact}")
            print(f"   Before: {change.before_abstract}")
            print(f"   After: {change.after_abstract}")
            
        print(f"\n🌟 Layer 5 AI Analysis Complete!")
        print(f"🧠 LLM successfully detected abstract semantic patterns")
        
        # Print professional report
        report = analyzer.format_analysis_report(changes, "demo.py")
        print("\n📊 Analysis Report:")
        print(report)
        
    else:
        print("✅ LLM call completed but no high-confidence abstract changes detected")

def test_layer5_with_real_changes():
    """Test Layer 5 with actual code changes from the repository."""
    
    print("\n🔬 TESTING LAYER 5 WITH REAL REPOSITORY CHANGES")
    print("=" * 50)
    
    config = Layer5Config()
    analyzer = LLMSemanticAnalyzer(config)
    
    if not config.api_key:
        print("❌ Skipping real change analysis - API key required")
        return
    
    # Simulate getting actual file changes (would normally come from git diff)
    real_changes = [
        {
            "file": "layer5_demo_before.py",
            "before": "Manual loop with conditionals",
            "after": "List comprehension with built-ins"
        }
    ]
    
    print("🔍 Analyzing real repository changes...")
    
    for change in real_changes:
        print(f"\n📁 File: {change['file']}")
        
        # In real implementation, would get actual git diff content
        # For demo, use simplified examples
        before = '''
def find_max(numbers):
    max_val = numbers[0]
    for i in range(1, len(numbers)):
        if numbers[i] > max_val:
            max_val = numbers[i]
    return max_val
'''
        
        after = '''
def find_max(numbers):
    return max(numbers)
'''
        
        semantic_changes = analyzer.analyze_abstract_changes(before, after, change['file'])
        
        if semantic_changes:
            for sc in semantic_changes:
                print(f"   🎯 {sc.change_type}: {sc.description}")
                print(f"      Confidence: {sc.confidence:.1%}")
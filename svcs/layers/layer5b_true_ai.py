# SVCS Layer 5b: True AI Analysis
# Large Language Model powered semantic analysis

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json
import os
import re

@dataclass
class LLMChange:
    """Represents a semantic change detected by LLM analysis."""
    change_type: str
    description: str
    confidence: float
    reasoning: str
    impact: str
    node_id: str

class TrueAIAnalyzer:
    """Layer 5b: True AI Analysis - LLM-powered semantic understanding."""
    
    def __init__(self):
        self.layer_name = "Layer 5b: True AI"
        self.layer_description = "Large Language Model semantic analysis"
        self._llm_available = self._check_llm_availability()
        self._model = self._initialize_model()
    
    def analyze(self, filepath: str, before_content: str, after_content: str,
                nodes_before: dict, nodes_after: dict) -> List[Dict[str, Any]]:
        """Analyze semantic changes using LLM-powered analysis."""
        events = []
        
        if not self._llm_available or not self._model:
            return events
        
        # Skip identical content
        if before_content == after_content:
            return events
        
        # 🚀 INTELLIGENT FILTERING: Only call LLM for non-trivial changes
        if not self._is_change_worth_llm_analysis(before_content, after_content, filepath):
            # Skip LLM analysis for trivial changes to save API costs
            return events

        try:
            # Analyze abstract changes using LLM
            llm_changes = self.analyze_abstract_changes(before_content, after_content, filepath)
            
            # Convert to events
            for change in llm_changes:
                if change.confidence > 0.7:  # Only include high-confidence LLM detections
                    events.append({
                        "event_type": change.change_type,
                        "node_id": change.node_id,
                        "location": filepath,
                        "details": change.description,
                        "layer": "5b",
                        "layer_description": self.layer_description,
                        "confidence": change.confidence,
                        "reasoning": change.reasoning,
                        "impact": change.impact
                    })
        
        except Exception as e:
            print(f"Warning: LLM analysis failed: {e}")
        
        return events
    
    def analyze_abstract_changes(self, before_content: str, after_content: str, 
                                filepath: str) -> List[LLMChange]:
        """Analyze abstract semantic changes using LLM."""
        if not self._model:
            return []
        
        changes = []
        
        # Prepare the prompt for LLM analysis
        prompt = self._create_analysis_prompt(before_content, after_content, filepath)
        
        try:
            # Get LLM response
            response = self._query_llm(prompt)
            
            # Parse LLM response into structured changes
            parsed_changes = self._parse_llm_response(response, filepath)
            changes.extend(parsed_changes)
            
        except Exception as e:
            print(f"Warning: LLM query failed: {e}")
        
        return changes
    
    def _check_llm_availability(self) -> bool:
        """Check if LLM services are available."""
        # Check for Google Gemini API key (primary LLM as in legacy system)
        if os.getenv('GOOGLE_API_KEY'):
            try:
                import google.generativeai as genai
                return True
            except ImportError:
                pass
        
        # Check for OpenAI API key (fallback)
        if os.getenv('OPENAI_API_KEY'):
            try:
                import openai
                return True
            except ImportError:
                pass
        
        # Check for Anthropic API key (fallback)
        if os.getenv('ANTHROPIC_API_KEY'):
            try:
                import anthropic
                return True
            except ImportError:
                pass
        
        # Check for local LLM options (fallback)
        try:
            import ollama
            return True
        except ImportError:
            pass
        
        return False
    
    def _initialize_model(self) -> Optional[Any]:
        """Initialize the LLM model."""
        if not self._llm_available:
            return None
        
        # Try Google Gemini first (as in legacy system)
        if os.getenv('GOOGLE_API_KEY'):
            try:
                import google.generativeai as genai
                genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
                return genai.GenerativeModel('gemini-1.5-flash')
            except ImportError:
                pass
        
        # Try OpenAI as fallback
        if os.getenv('OPENAI_API_KEY'):
            try:
                import openai
                return openai
            except ImportError:
                pass
        
        # Try Anthropic as fallback
        if os.getenv('ANTHROPIC_API_KEY'):
            try:
                import anthropic
                return anthropic.Anthropic()
            except ImportError:
                pass
        
        # Try local Ollama as fallback
        try:
            import ollama
            return ollama
        except ImportError:
            pass
        
        return None
    
    def _create_analysis_prompt(self, before_content: str, after_content: str, filepath: str) -> str:
        """Create a prompt for LLM semantic analysis."""
        prompt = f"""You are an expert code analyzer. Analyze the semantic changes between these two versions of a {filepath} file.

BEFORE:
```
{before_content[:2000]}  # Truncate for token limits
```

AFTER:
```
{after_content[:2000]}  # Truncate for token limits
```

Please identify high-level semantic changes, focusing on:
1. Intent and purpose changes
2. Algorithm or approach changes  
3. Architectural modifications
4. Business logic alterations
5. Design pattern implementations/removals
6. Performance implications
7. Security implications
8. Maintainability impacts

For each change, provide:
- change_type: A descriptive type (e.g., "algorithm_optimization", "business_logic_change")
- description: What changed in natural language
- confidence: 0.0-1.0 confidence score
- reasoning: Why you identified this change
- impact: The implications of this change
- node_id: The affected function/class (if identifiable)

Respond in JSON format with an array of changes:
```json
[
  {{
    "change_type": "...",
    "description": "...", 
    "confidence": 0.0,
    "reasoning": "...",
    "impact": "...",
    "node_id": "..."
  }}
]
```

Only include changes with confidence >= 0.7. If no significant semantic changes are detected, return an empty array.
"""
        return prompt
    
    def _query_llm(self, prompt: str) -> str:
        """Query the LLM with the given prompt."""
        if not self._model:
            return "[]"
        
        # Try Google Gemini Flash (primary as in legacy system)
        if hasattr(self._model, 'generate_content'):
            try:
                response = self._model.generate_content(prompt)
                return response.text
            except Exception as e:
                print(f"Gemini query failed: {e}")
        
        # Try OpenAI (fallback)
        if hasattr(self._model, 'chat'):
            try:
                response = self._model.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert code analyzer."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.1
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"OpenAI query failed: {e}")
        
        # Try Anthropic (fallback)
        if hasattr(self._model, 'messages'):
            try:
                response = self._model.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=1000,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text
            except Exception as e:
                print(f"Anthropic query failed: {e}")
        
        # Try Ollama (fallback)
        if hasattr(self._model, 'generate'):
            try:
                response = self._model.generate(
                    model="llama2",
                    prompt=prompt
                )
                return response['response']
            except Exception as e:
                print(f"Ollama query failed: {e}")
        
        return "[]"
    
    def _parse_llm_response(self, response: str, filepath: str) -> List[LLMChange]:
        """Parse LLM response into structured changes."""
        changes = []
        
        try:
            # Extract JSON from response
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                
                for item in data:
                    if isinstance(item, dict):
                        change = LLMChange(
                            change_type=item.get('change_type', 'unknown_change'),
                            description=item.get('description', ''),
                            confidence=float(item.get('confidence', 0.0)),
                            reasoning=item.get('reasoning', ''),
                            impact=item.get('impact', ''),
                            node_id=item.get('node_id', f'ai_detected:{filepath}')
                        )
                        changes.append(change)
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Warning: Could not parse LLM response: {e}")
            
            # Fallback: try to extract key information with regex
            changes.extend(self._fallback_parse_response(response, filepath))
        
        return changes
    
    def _fallback_parse_response(self, response: str, filepath: str) -> List[LLMChange]:
        """Fallback parsing when JSON parsing fails."""
        changes = []
        
        # Simple pattern matching for common change descriptions
        change_patterns = [
            (r'algorithm.*optimization', 'algorithm_optimization'),
            (r'performance.*improvement', 'performance_improvement'),
            (r'security.*enhancement', 'security_enhancement'),
            (r'refactor', 'refactoring'),
            (r'business.*logic', 'business_logic_change'),
            (r'design.*pattern', 'design_pattern_change'),
            (r'error.*handling', 'error_handling_change'),
            (r'api.*change', 'api_modification')
        ]
        
        for pattern, change_type in change_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                changes.append(LLMChange(
                    change_type=change_type,
                    description=f"LLM detected {change_type.replace('_', ' ')}",
                    confidence=0.7,
                    reasoning="Pattern detected in LLM response",
                    impact="Semantic change detected",
                    node_id=f'ai_detected:{filepath}'
                ))
                break  # Only add one fallback change
        
        return changes
    
    def _is_change_worth_llm_analysis(self, before_code: str, after_code: str, file_path: str) -> bool:
        """
        Intelligent filtering to determine if a change is worth LLM analysis.
        Saves API costs by skipping trivial changes.
        """
        # Basic size filtering
        before_lines = before_code.count('\n') + 1 if before_code else 0
        after_lines = after_code.count('\n') + 1 if after_code else 0
        lines_changed = abs(after_lines - before_lines)
        
        # Skip LLM for very small files (likely trivial)
        if after_lines <= 5 and before_lines <= 5:
            return False
        
        # Check for trivial changes (only comments, whitespace, simple literals)
        if self._is_trivial_change(before_code, after_code):
            return False
        
        # Check minimum code complexity threshold
        if not self._meets_complexity_threshold(before_code, after_code):
            return False
        
        return True
    
    def _is_trivial_change(self, before_code: str, after_code: str) -> bool:
        """Check if the change is trivial (comments, literals, simple formatting)."""
        # Remove comments and whitespace for comparison
        def normalize_code(code):
            # Remove single-line comments
            code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
            # Remove multi-line strings/docstrings (basic detection)
            code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
            code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)
            # Remove extra whitespace
            code = re.sub(r'\s+', ' ', code).strip()
            return code
        
        normalized_before = normalize_code(before_code)
        normalized_after = normalize_code(after_code)
        
        # If normalized versions are very similar, it's likely trivial
        if normalized_before == normalized_after:
            return True
        
        # Check for only literal/constant changes
        literal_change_patterns = [
            r'return\s+\d+',  # Simple return values
            r'=\s*["\'].*?["\']',  # String literals
            r'=\s*\d+',  # Numeric literals
        ]
        
        # If change only involves simple literals, consider trivial
        diff_significant = False
        for line_before, line_after in zip(before_code.split('\n'), after_code.split('\n')):
            if line_before.strip() != line_after.strip():
                # Check if this is just a literal change
                is_literal_only = any(
                    re.search(pattern, line_before) and re.search(pattern, line_after)
                    for pattern in literal_change_patterns
                )
                if not is_literal_only:
                    diff_significant = True
                    break
        
        return not diff_significant
    
    def _meets_complexity_threshold(self, before_code: str, after_code: str) -> bool:
        """Check if the code meets minimum complexity for worthwhile LLM analysis."""
        
        # Check for complex constructs that might benefit from LLM analysis
        complex_patterns = [
            r'class\s+\w+',  # Class definitions
            r'def\s+\w+.*:',  # Function definitions (multiple)
            r'import\s+\w+',  # Import statements
            r'from\s+\w+\s+import',  # From imports
            r'async\s+def',  # Async functions
            r'@\w+',  # Decorators
            r'with\s+\w+',  # Context managers
            r'try:|except:|finally:',  # Error handling
            r'if\s+.*:\s*$',  # Control flow
            r'for\s+.*:\s*$',  # Loops
            r'while\s+.*:\s*$',  # While loops
            r'return\s+\w+\(',  # Recursive calls (function calls in return)
            r'range\(',  # Range usage (often algorithmic)
            r'enumerate\(',  # Enumeration patterns
        ]
        
        combined_code = before_code + '\n' + after_code
        
        # Count complex patterns
        complexity_score = 0
        for pattern in complex_patterns:
            matches = re.findall(pattern, combined_code, re.MULTILINE)
            complexity_score += len(matches)
        
        # Special check for algorithmic changes (iterative vs recursive patterns)
        algorithmic_change = False
        if ('for' in before_code and 'return' in after_code and 
            before_code.count('def') != after_code.count('def')):
            algorithmic_change = True
        
        # Require minimum complexity score for LLM analysis
        return complexity_score >= 2 or algorithmic_change

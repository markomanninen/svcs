# SVCS Layer 5a: AI Pattern Recognition
# AI-powered pattern detection and analysis

from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass
import re

class SemanticPattern(Enum):
    """Semantic patterns that can be detected by AI analysis."""
    REFACTORING_EXTRACT_METHOD = "refactoring_extract_method"
    REFACTORING_INLINE_METHOD = "refactoring_inline_method"
    OPTIMIZATION_ALGORITHM = "optimization_algorithm"
    OPTIMIZATION_DATA_STRUCTURE = "optimization_data_structure"
    DESIGN_PATTERN_IMPLEMENTATION = "design_pattern_implementation"
    DESIGN_PATTERN_REMOVAL = "design_pattern_removal"
    SECURITY_IMPROVEMENT = "security_improvement"
    SECURITY_VULNERABILITY = "security_vulnerability"
    PERFORMANCE_IMPROVEMENT = "performance_improvement"
    PERFORMANCE_REGRESSION = "performance_regression"
    API_BREAKING_CHANGE = "api_breaking_change"
    API_ENHANCEMENT = "api_enhancement"
    CODE_SIMPLIFICATION = "code_simplification"
    CODE_COMPLICATION = "code_complication"
    ERROR_HANDLING_IMPROVEMENT = "error_handling_improvement"
    CONCURRENCY_INTRODUCTION = "concurrency_introduction"
    MEMORY_OPTIMIZATION = "memory_optimization"
    ARCHITECTURE_CHANGE = "architecture_change"

@dataclass
class SemanticChange:
    """Represents a semantic change detected by AI analysis."""
    pattern: SemanticPattern
    node_id: str
    description: str
    confidence: float
    reasoning: str
    impact: str

class AIPatternAnalyzer:
    """Layer 5a: AI Pattern Recognition - Pattern-based semantic analysis."""
    
    def __init__(self):
        self.layer_name = "Layer 5a: AI Patterns"
        self.layer_description = "AI-powered pattern recognition and analysis"
    
    def analyze(self, filepath: str, before_content: str, after_content: str,
                nodes_before: dict, nodes_after: dict) -> List[Dict[str, Any]]:
        """Analyze semantic patterns using AI-powered detection."""
        events = []
        
        # Detect semantic changes
        semantic_changes = self.analyze_semantic_changes(before_content, after_content, filepath)
        
        # Convert to events
        for change in semantic_changes:
            if change.confidence > 0.6:  # Only include high-confidence detections
                events.append({
                    "event_type": change.pattern.value,
                    "node_id": change.node_id,
                    "location": filepath,
                    "details": change.description,
                    "layer": "5a",
                    "layer_description": self.layer_description,
                    "confidence": change.confidence,
                    "reasoning": change.reasoning,
                    "impact": change.impact
                })
        
        return events
    
    def analyze_semantic_changes(self, before_content: str, after_content: str, 
                                filepath: str) -> List[SemanticChange]:
        """Analyze semantic changes between code versions."""
        changes = []
        
        # Pattern-based analysis
        changes.extend(self._detect_refactoring_patterns(before_content, after_content, filepath))
        changes.extend(self._detect_optimization_patterns(before_content, after_content, filepath))
        changes.extend(self._detect_design_patterns(before_content, after_content, filepath))
        changes.extend(self._detect_security_patterns(before_content, after_content, filepath))
        changes.extend(self._detect_performance_patterns(before_content, after_content, filepath))
        changes.extend(self._detect_api_changes(before_content, after_content, filepath))
        changes.extend(self._detect_complexity_changes(before_content, after_content, filepath))
        changes.extend(self._detect_concurrency_patterns(before_content, after_content, filepath))
        
        return changes
    
    def _detect_refactoring_patterns(self, before: str, after: str, filepath: str) -> List[SemanticChange]:
        """Detect refactoring patterns."""
        changes = []
        
        # Extract method refactoring
        before_functions = self._extract_function_names(before)
        after_functions = self._extract_function_names(after)
        
        new_functions = after_functions - before_functions
        if new_functions and len(after) > len(before):
            # Possible extract method refactoring
            for func_name in new_functions:
                changes.append(SemanticChange(
                    pattern=SemanticPattern.REFACTORING_EXTRACT_METHOD,
                    node_id=f"func:{func_name}",
                    description=f"Possible method extraction: {func_name}",
                    confidence=0.7,
                    reasoning="New function detected with increased code size",
                    impact="Code organization improvement"
                ))
        
        # Inline method refactoring
        removed_functions = before_functions - after_functions
        if removed_functions and len(after) < len(before):
            for func_name in removed_functions:
                changes.append(SemanticChange(
                    pattern=SemanticPattern.REFACTORING_INLINE_METHOD,
                    node_id=f"func:{func_name}",
                    description=f"Possible method inlining: {func_name}",
                    confidence=0.7,
                    reasoning="Function removed with decreased code size",
                    impact="Code simplification"
                ))
        
        return changes
    
    def _detect_optimization_patterns(self, before: str, after: str, filepath: str) -> List[SemanticChange]:
        """Detect optimization patterns."""
        changes = []
        
        # List comprehension optimization
        if "for " in before and "[" in after and "for " in after:
            if before.count("for ") > after.count("for "):
                changes.append(SemanticChange(
                    pattern=SemanticPattern.OPTIMIZATION_ALGORITHM,
                    node_id=f"optimization:{filepath}",
                    description="Loop converted to list comprehension",
                    confidence=0.8,
                    reasoning="Reduced loop count with comprehension syntax",
                    impact="Performance and readability improvement"
                ))
        
        # Dictionary/set usage optimization
        if "in [" in before and "in {" in after:
            changes.append(SemanticChange(
                pattern=SemanticPattern.OPTIMIZATION_DATA_STRUCTURE,
                node_id=f"optimization:{filepath}",
                description="List membership check replaced with set/dict",
                confidence=0.9,
                reasoning="List membership replaced with O(1) lookup",
                impact="Significant performance improvement"
            ))
        
        return changes
    
    def _detect_design_patterns(self, before: str, after: str, filepath: str) -> List[SemanticChange]:
        """Detect design pattern implementations."""
        changes = []
        
        # Singleton pattern
        if "__new__" in after and "__new__" not in before:
            changes.append(SemanticChange(
                pattern=SemanticPattern.DESIGN_PATTERN_IMPLEMENTATION,
                node_id=f"pattern:{filepath}",
                description="Singleton pattern implementation detected",
                confidence=0.8,
                reasoning="__new__ method added for instance control",
                impact="Design pattern implementation"
            ))
        
        # Observer pattern
        if "notify" in after and "observe" in after and len(after.split("def ")) > len(before.split("def ")):
            changes.append(SemanticChange(
                pattern=SemanticPattern.DESIGN_PATTERN_IMPLEMENTATION,
                node_id=f"pattern:{filepath}",
                description="Observer pattern implementation detected",
                confidence=0.7,
                reasoning="Notify/observe methods with increased function count",
                impact="Improved decoupling and event handling"
            ))
        
        return changes
    
    def _detect_security_patterns(self, before: str, after: str, filepath: str) -> List[SemanticChange]:
        """Detect security-related changes."""
        changes = []
        
        # Input validation
        if "validate" in after and "validate" not in before:
            changes.append(SemanticChange(
                pattern=SemanticPattern.SECURITY_IMPROVEMENT,
                node_id=f"security:{filepath}",
                description="Input validation added",
                confidence=0.8,
                reasoning="Validation function introduced",
                impact="Security enhancement"
            ))
        
        # SQL injection prevention
        if "?" in after and "%" in before and "sql" in before.lower():
            changes.append(SemanticChange(
                pattern=SemanticPattern.SECURITY_IMPROVEMENT,
                node_id=f"security:{filepath}",
                description="SQL injection prevention - parameterized queries",
                confidence=0.9,
                reasoning="String formatting replaced with parameterized queries",
                impact="Critical security improvement"
            ))
        
        # Hardcoded secrets removal
        secret_patterns = [r'password\s*=\s*["\']', r'api_key\s*=\s*["\']', r'secret\s*=\s*["\']']
        for pattern in secret_patterns:
            if re.search(pattern, before, re.IGNORECASE) and not re.search(pattern, after, re.IGNORECASE):
                changes.append(SemanticChange(
                    pattern=SemanticPattern.SECURITY_IMPROVEMENT,
                    node_id=f"security:{filepath}",
                    description="Hardcoded secret removed",
                    confidence=0.9,
                    reasoning="Hardcoded credential pattern removed",
                    impact="Security vulnerability fixed"
                ))
        
        return changes
    
    def _detect_performance_patterns(self, before: str, after: str, filepath: str) -> List[SemanticChange]:
        """Detect performance-related changes."""
        changes = []
        
        # Caching implementation
        if "cache" in after and "cache" not in before:
            changes.append(SemanticChange(
                pattern=SemanticPattern.PERFORMANCE_IMPROVEMENT,
                node_id=f"performance:{filepath}",
                description="Caching mechanism implemented",
                confidence=0.8,
                reasoning="Cache-related code introduced",
                impact="Performance optimization"
            ))
        
        # Lazy loading
        if "lazy" in after and "lazy" not in before:
            changes.append(SemanticChange(
                pattern=SemanticPattern.PERFORMANCE_IMPROVEMENT,
                node_id=f"performance:{filepath}",
                description="Lazy loading pattern implemented",
                confidence=0.7,
                reasoning="Lazy loading pattern detected",
                impact="Memory and startup performance improvement"
            ))
        
        return changes
    
    def _detect_api_changes(self, before: str, after: str, filepath: str) -> List[SemanticChange]:
        """Detect API-related changes."""
        changes = []
        
        # Function signature changes that could break API
        before_sigs = re.findall(r'def\s+(\w+)\s*\([^)]*\)', before)
        after_sigs = re.findall(r'def\s+(\w+)\s*\([^)]*\)', after)
        
        for sig in before_sigs:
            before_params = self._extract_function_params(before, sig)
            after_params = self._extract_function_params(after, sig)
            
            if before_params and after_params and len(before_params) != len(after_params):
                changes.append(SemanticChange(
                    pattern=SemanticPattern.API_BREAKING_CHANGE,
                    node_id=f"func:{sig}",
                    description=f"Function {sig} parameter count changed",
                    confidence=0.9,
                    reasoning="Parameter count mismatch detected",
                    impact="Potential breaking change for callers"
                ))
        
        return changes
    
    def _detect_complexity_changes(self, before: str, after: str, filepath: str) -> List[SemanticChange]:
        """Detect complexity-related changes."""
        changes = []
        
        # Code simplification
        before_complexity = self._estimate_complexity(before)
        after_complexity = self._estimate_complexity(after)
        
        if after_complexity < before_complexity * 0.8:  # Significant reduction
            changes.append(SemanticChange(
                pattern=SemanticPattern.CODE_SIMPLIFICATION,
                node_id=f"complexity:{filepath}",
                description="Code complexity significantly reduced",
                confidence=0.8,
                reasoning=f"Complexity reduced from {before_complexity} to {after_complexity}",
                impact="Maintainability improvement"
            ))
        elif after_complexity > before_complexity * 1.2:  # Significant increase
            changes.append(SemanticChange(
                pattern=SemanticPattern.CODE_COMPLICATION,
                node_id=f"complexity:{filepath}",
                description="Code complexity significantly increased",
                confidence=0.8,
                reasoning=f"Complexity increased from {before_complexity} to {after_complexity}",
                impact="Potential maintainability concern"
            ))
        
        return changes
    
    def _detect_concurrency_patterns(self, before: str, after: str, filepath: str) -> List[SemanticChange]:
        """Detect concurrency-related changes."""
        changes = []
        
        # Async/await introduction
        if "async " in after and "async " not in before:
            changes.append(SemanticChange(
                pattern=SemanticPattern.CONCURRENCY_INTRODUCTION,
                node_id=f"concurrency:{filepath}",
                description="Asynchronous programming introduced",
                confidence=0.9,
                reasoning="Async/await keywords detected",
                impact="Concurrency and performance improvement"
            ))
        
        # Threading
        if "thread" in after.lower() and "thread" not in before.lower():
            changes.append(SemanticChange(
                pattern=SemanticPattern.CONCURRENCY_INTRODUCTION,
                node_id=f"concurrency:{filepath}",
                description="Threading introduced",
                confidence=0.8,
                reasoning="Threading-related code detected",
                impact="Parallel processing capability added"
            ))
        
        return changes
    
    def _extract_function_names(self, code: str) -> set:
        """Extract function names from code."""
        pattern = r'def\s+(\w+)\s*\('
        return set(re.findall(pattern, code))
    
    def _extract_function_params(self, code: str, func_name: str) -> Optional[List[str]]:
        """Extract parameters for a specific function."""
        pattern = rf'def\s+{func_name}\s*\(([^)]*)\)'
        match = re.search(pattern, code)
        if match:
            params_str = match.group(1)
            return [p.strip().split('=')[0].strip() for p in params_str.split(',') if p.strip()]
        return None
    
    def _estimate_complexity(self, code: str) -> int:
        """Estimate code complexity based on various metrics."""
        complexity = 0
        
        # Control flow statements
        complexity += code.count('if ')
        complexity += code.count('for ')
        complexity += code.count('while ')
        complexity += code.count('try:')
        complexity += code.count('except ')
        
        # Nested structures
        complexity += code.count('def ')
        complexity += code.count('class ')
        complexity += code.count('lambda ')
        
        # Logical operators
        complexity += code.count(' and ')
        complexity += code.count(' or ')
        
        return complexity

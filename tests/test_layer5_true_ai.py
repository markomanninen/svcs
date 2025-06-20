#!/usr/bin/env python3
"""
Unit tests for SVCS Layer 5 True AI semantic analysis
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add the parent directory to path to import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from svcs_layer5_true_ai import LLMSemanticAnalyzer, AbstractSemanticChange, Layer5Config


class TestLLMSemanticAnalyzer(unittest.TestCase):
    """Test cases for the LLM Semantic Analyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        config = Layer5Config()
        config.api_key = "test-api-key"  # Mock API key
        self.analyzer = LLMSemanticAnalyzer(config)
    
    def test_smart_truncate_code_short(self):
        """Test smart truncation with short code."""
        code = "def hello():\n    print('world')"
        result = self.analyzer._smart_truncate_code(code, max_chars=1000)
        self.assertEqual(result, code)
    
    def test_smart_truncate_code_long(self):
        """Test smart truncation with long code."""
        code = "def hello():\n    print('world')\n" * 100
        result = self.analyzer._smart_truncate_code(code, max_chars=50)
        self.assertIn("# ... [truncated for analysis] ...", result)
        self.assertLess(len(result), len(code))
    
    def test_validate_change_data_valid(self):
        """Test validation with valid change data."""
        valid_data = {
            "change_type": "algorithm_optimization",
            "confidence": 0.8,
            "description": "Test description",
            "reasoning": "Test reasoning",
            "impact": "Test impact",
            "before_abstract": "Before",
            "after_abstract": "After"
        }
        self.assertTrue(self.analyzer._validate_change_data(valid_data))
    
    def test_validate_change_data_missing_field(self):
        """Test validation with missing required field."""
        invalid_data = {
            "change_type": "algorithm_optimization",
            "confidence": 0.8,
            # Missing required fields
        }
        self.assertFalse(self.analyzer._validate_change_data(invalid_data))
    
    def test_validate_change_data_invalid_confidence(self):
        """Test validation with invalid confidence value."""
        invalid_data = {
            "change_type": "algorithm_optimization",
            "confidence": 1.5,  # Invalid confidence > 1.0
            "description": "Test description",
            "reasoning": "Test reasoning",
            "impact": "Test impact",
            "before_abstract": "Before",
            "after_abstract": "After"
        }
        self.assertFalse(self.analyzer._validate_change_data(invalid_data))
    
    def test_parse_genai_response_valid(self):
        """Test parsing a valid genai SDK response."""
        # Mock genai response object (similar to svcs_discuss.py pattern)
        class MockResponse:
            def __init__(self, text):
                self.text = text
        
        mock_response = MockResponse('''
        {
            "abstract_changes": [
                {
                    "change_type": "algorithm_optimization",
                    "confidence": 0.9,
                    "description": "Replaced manual loop with built-in function",
                    "reasoning": "Using max() instead of manual iteration",
                    "impact": "Improved readability and performance",
                    "before_abstract": "Manual iteration through list",
                    "after_abstract": "Built-in max function"
                }
            ]
        }
        ''')
        
        changes = self.analyzer._parse_genai_response(mock_response)
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0].change_type, "algorithm_optimization")
        self.assertEqual(changes[0].confidence, 0.9)
    
    def test_parse_genai_response_low_confidence(self):
        """Test that low confidence changes are filtered out."""
        class MockResponse:
            def __init__(self, text):
                self.text = text
        
        mock_response = MockResponse('''
        {
            "abstract_changes": [
                {
                    "change_type": "algorithm_optimization",
                    "confidence": 0.3,
                    "description": "Low confidence change",
                    "reasoning": "Uncertain improvement",
                    "impact": "Minimal impact",
                    "before_abstract": "Before",
                    "after_abstract": "After"
                }
            ]
        }
        ''')
        
        changes = self.analyzer._parse_genai_response(mock_response)
        self.assertEqual(len(changes), 0)  # Should be filtered out due to low confidence
    
    @patch('svcs_layer5_true_ai.genai')
    def test_analyze_abstract_changes_no_api_key(self, mock_genai):
        """Test behavior when no API key is provided."""
        config = Layer5Config()
        config.api_key = None
        analyzer = LLMSemanticAnalyzer(config)
        
        changes = analyzer.analyze_abstract_changes("before", "after", "test.py")
        self.assertEqual(changes, [])
    
    def test_analyze_abstract_changes_identical_code(self):
        """Test behavior when before and after code are identical."""
        config = Layer5Config()
        config.api_key = "test-key"
        analyzer = LLMSemanticAnalyzer(config)
        
        changes = analyzer.analyze_abstract_changes("same code", "same code", "test.py")
        self.assertEqual(changes, [])


if __name__ == '__main__':
    unittest.main()

# FILE: tests/test_discuss.py
#
# This file contains tests for the svcs_discuss.py conversational REPL.
# It uses the unittest.mock library to simulate the behavior of the
# Google Generative AI model, allowing us to test our script's logic
# without making actual API calls.
#
# Usage:
#   python3 tests/test_discuss.py

import unittest
from unittest.mock import patch, MagicMock, call
import os
import sys

# We need to add the root directory and the .svcs directory to the path
# so that our test file can import the modules we want to test.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.svcs')))

# Now we can import the modules
import svcs_discuss

class TestSVCSDiscuss(unittest.TestCase):

    @patch('svcs_discuss.find_dependency_changes')
    @patch('svcs_discuss.genai')
    @patch('svcs_discuss.console')
    def test_assistant_handles_dependency_question(self, mock_console, mock_genai, mock_find_dependency_changes):
        """
        Tests if the assistant correctly calls the 'find_dependency_changes'
        tool when asked about a library.
        """
        # --- Arrange ---
        mock_model = MagicMock()
        mock_chat_session = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        mock_model.start_chat.return_value = mock_chat_session

        def send_message_side_effect(prompt):
            if "math library" in prompt:
                mock_find_dependency_changes(dependency_name="math")
                return MagicMock(text="The `math` library was added in commit abc1234.")
            return MagicMock(text="I can't answer that.")

        mock_chat_session.send_message.side_effect = send_message_side_effect
        mock_console.input.side_effect = ["when was the math library added?", "exit"]

        # --- Act ---
        svcs_discuss.main()

        # --- Assert ---
        mock_find_dependency_changes.assert_called_once_with(dependency_name="math")
        final_print_call = mock_console.print.call_args_list[-3]
        rendered_markdown = final_print_call.args[0]
        self.assertIn("The `math` library was added", rendered_markdown.markup)


    # CORRECTED: This test now targets the 'get_node_evolution' tool.
    @patch('svcs_discuss.get_node_evolution')
    @patch('svcs_discuss.genai')
    @patch('svcs_discuss.console')
    def test_assistant_handles_node_evolution_question(self, mock_console, mock_genai, mock_get_node_evolution):
        """
        Tests if the assistant correctly calls the 'get_node_evolution'
        tool when asked about the history of a specific function.
        """
        # --- Arrange ---
        mock_model = MagicMock()
        mock_chat_session = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        mock_model.start_chat.return_value = mock_chat_session

        def send_message_side_effect(prompt):
            if "history for the greet function" in prompt:
                # Simulate the AI calling our tool
                mock_get_node_evolution(node_id="func:greet")
                # Simulate the AI's final text response
                return MagicMock(text="The function `greet` was created in commit xyz789.")
            return MagicMock(text="Unknown query.")

        mock_chat_session.send_message.side_effect = send_message_side_effect
        mock_console.input.side_effect = ["show me the history for the greet function", "exit"]

        # --- Act ---
        svcs_discuss.main()

        # --- Assert ---
        # 1. Was the correct API function called with the correct argument?
        mock_get_node_evolution.assert_called_once_with(node_id="func:greet")
        
        # 2. Was the final response printed?
        final_print_call = mock_console.print.call_args_list[-3]
        self.assertIn("The function `greet` was created", final_print_call.args[0].markup)


if __name__ == '__main__':
    # Make sure to configure a dummy API key for the test environment
    os.environ["GOOGLE_API_KEY"] = "test-key-for-unit-testing"
    unittest.main()

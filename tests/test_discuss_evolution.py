# FILE: tests/test_discuss_evolution.py
#
# This file contains tests for the enhanced narrative features of the
# svcs_discuss.py conversational REPL.
#
# Usage:
#   python3 tests/test_discuss_evolution.py

import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add the root and .svcs directories to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.svcs')))

# Import the script we want to test
import svcs_discuss

class TestSVCSDiscussEvolution(unittest.TestCase):

    @patch('svcs_discuss.get_node_evolution')
    @patch('svcs_discuss.genai')
    @patch('svcs_discuss.console')
    def test_assistant_tells_node_evolution_story(self, mock_console, mock_genai, mock_get_node_evolution):
        """
        Tests if the assistant correctly uses the get_node_evolution tool
        to summarize the history of a function.
        """
        # --- Arrange ---
        # 1. Mock the AI model and its chat session
        mock_model = MagicMock()
        mock_chat_session = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        mock_model.start_chat.return_value = mock_chat_session

        # 2. Mock the user's input
        mock_console.input.side_effect = ["tell me the story of func:greet", "exit"]

        # 3. Mock the data that our API tool will return when called
        mock_get_node_evolution.return_value = [
            {"event_type": "node_added", "commit_hash": "abc111"},
            {"event_type": "node_signature_changed", "commit_hash": "def222"},
            {"event_type": "internal_call_added", "commit_hash": "ghi333"},
        ]
        
        # 4. Simulate the AI's two-step thinking process
        def send_message_side_effect(prompt):
            if "story of func:greet" in prompt:
                # First, the AI decides to call our tool.
                # We simulate this by manually calling the mocked API function.
                mock_get_node_evolution(node_id="func:greet")
                # Then, the AI provides the final text response.
                return MagicMock(text="Here is the story of func:greet...")
            return MagicMock(text="I can't answer that.")

        mock_chat_session.send_message.side_effect = send_message_side_effect

        # --- Act ---
        # Run the main loop of the conversational assistant
        svcs_discuss.main()

        # --- Assert ---
        # 1. Was the get_node_evolution tool called correctly?
        mock_get_node_evolution.assert_called_once_with(node_id="func:greet")
        
        # 2. Did the assistant send the user's prompt to the AI?
        mock_chat_session.send_message.assert_called_once_with("tell me the story of func:greet")
        
        # 3. Was the final narrative response printed to the console?
        # Get the second-to-last print call (before the exit message)
        final_print_call = mock_console.print.call_args_list[-3]
        rendered_markdown = final_print_call.args[0]
        self.assertIn("Here is the story", rendered_markdown.markup)


if __name__ == '__main__':
    # Configure a dummy API key for the test environment
    os.environ["GOOGLE_API_KEY"] = "test-key-for-unit-testing"
    unittest.main()

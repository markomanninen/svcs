import sys
import os
# Add src to path to allow importing main
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from tests.commit_before_example import greet

def test_greet_default():
    """Tests the greet function with no arguments."""
    assert greet() == "Hello, world!"

def test_greet_with_name():
    """Tests the greet function with a name."""
    assert greet("Alice") == "Hello, Alice!"

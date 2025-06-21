#!/usr/bin/env python3
"""
Test the actual conversational interface with programmatic queries.
This will help us verify that the LLM improvements work correctly.
"""
import sys
import os

# Check if GOOGLE_API_KEY is set
if not os.getenv("GOOGLE_API_KEY"):
    print("❌ GOOGLE_API_KEY not set. Cannot test LLM interaction.")
    print("Set it with: export GOOGLE_API_KEY='your-api-key'")
    sys.exit(1)

# Change to parent directory so database paths work correctly
os.chdir('..')
sys.path.append('.svcs')

try:
    import google.generativeai as genai
    from api import (
        search_semantic_patterns,
        get_recent_activity, 
        search_events_advanced,
        debug_query_tools
    )
    from llm_logger import llm_logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all dependencies are installed in .svcs/venv")
    sys.exit(1)

def configure_llm():
    """Configure the LLM for testing."""
    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)

def test_llm_with_tools():
    """Test the LLM with the same tools and prompt as the conversational interface."""
    
    # Use the same system instruction as in svcs_discuss.py
    system_instruction = """
You are the SVCS Semantic VCS Assistant, an expert software archeologist. Your
purpose is to help developers understand the history of their codebase by telling
clear, concise stories about how the code evolved.

You have access to powerful search and analysis tools:

1. **search_events_advanced** - Comprehensive filtering by date, author, confidence, layers, etc.
2. **get_recent_activity** - Quick access to recent changes
3. **search_semantic_patterns** - Find specific AI-detected patterns
   IMPORTANT: For performance queries, use pattern_type="performance" which maps to "abstract_performance_optimization" events
4. **debug_query_tools** - Diagnostic tool when queries return no results

CRITICAL TOOL USAGE GUIDELINES:

For PERFORMANCE OPTIMIZATION queries:
- ALWAYS try search_semantic_patterns(pattern_type="performance") first
- If that returns no results, try search_events_advanced(event_types=["abstract_performance_optimization"])
- Consider lowering min_confidence to 0.5 or 0.6 to catch more results

TROUBLESHOOTING:
- If you get no results for a reasonable query, FIRST call debug_query_tools() to understand the data available
- Then try multiple approaches with lower confidence thresholds
- Always explain what you searched for and suggest alternatives if no results found
"""

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        tools=[
            search_events_advanced,
            get_recent_activity,
            search_semantic_patterns,
            debug_query_tools
        ],
        system_instruction=system_instruction
    )

    # Test queries
    test_queries = [
        "Show me performance optimizations from the last 7 days",
        "What performance improvements were made recently?",
        "Find any optimization changes with high confidence"
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*50}")
        print(f"TEST {i}: {query}")
        print('='*50)
        
        try:
            # Start chat session
            chat = model.start_chat(history=[])
            response = chat.send_message(query)
            
            # Handle function calls properly
            if response.parts:
                for part in response.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        # This is a function call
                        func_call = part.function_call
                        print(f"🔧 LLM called tool: {func_call.name}")
                        print(f"   Args: {dict(func_call.args)}")
                        
                        # Execute the function call
                        if func_call.name == "search_semantic_patterns":
                            args = dict(func_call.args)
                            result = search_semantic_patterns(**args)
                            print(f"   Result: Found {len(result)} results")
                            if result:
                                print(f"   Sample: {result[0].get('event_type')} in {result[0].get('location')}")
                        
                        elif func_call.name == "search_events_advanced":
                            args = dict(func_call.args)
                            result = search_events_advanced(**args)
                            print(f"   Result: Found {len(result)} results")
                        
                        elif func_call.name == "get_recent_activity":
                            args = dict(func_call.args)
                            result = get_recent_activity(**args)
                            print(f"   Result: Found {len(result)} results")
                        
                        elif func_call.name == "debug_query_tools":
                            args = dict(func_call.args)
                            result = debug_query_tools(**args)
                            print(f"   Result: Debug info - {result.get('performance_events', 0)} performance events")
                            
                    elif hasattr(part, 'text') and part.text:
                        # This is text response
                        print(f"LLM Response:")
                        print(part.text)
            
            # If no function calls were made, that might be the issue
            has_function_calls = any(hasattr(part, 'function_call') and part.function_call for part in response.parts)
            if not has_function_calls:
                print(f"\n❌ LLM did not call any tools! This may be why users get 'no results'.")
                print(f"   Response: {response.text if response.text else 'No text response'}")
                
        except Exception as e:
            print(f"❌ Error during LLM test: {e}")
            continue

if __name__ == "__main__":
    print("🤖 TESTING CONVERSATIONAL INTERFACE WITH ACTUAL LLM")
    print("=" * 60)
    
    configure_llm()
    test_llm_with_tools()
    
    print(f"\n{'='*60}")
    print("✅ LLM TESTING COMPLETED")
    print("=" * 60)

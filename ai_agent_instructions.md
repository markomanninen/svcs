## CLAUDE 4 specific misbehavings

- Claude 4 makes huge amount of test and doc files all over the places, and only occasionally removes them after task has been accomplished.
- Claude 4 uses timeout on bash command which is not available in macos
- Claude 4 leaves old code as fallbacks and legacy, even the library is in the development state. this piles up to huge files
- Claude 4 introduces fixes and patches to the code that it has created just few moments ago and which is not approved as tested and published feature, so it confuces development state and production ready maintainance code changes
- Claude 4 uses a lot of superlative and hype words which are naive in the code and documentation
- Claude 4 does not vaivaudu to factorize and modulirize code for smaller maintanable files, but create huge monith files which it cannot handle at the end
- modularize files exceeding 500-1000 lines
- Claude 4 often claims after doing a task with docs and tests that everything is tested perfectly and production ready, but at the same time bypasses errors as minor issues and completes the task as finished. It claims victory even though tests and feature implementation might be only partially succesful.
- Always look forward, whats next task, did we implement everything?
- Claude 4 sometimes mixes python and bash syntax, when working extensively with both environments
- Claude 4 sometimes modifies test so that they success leaving the core functionality, what is tested still failing
- Claude 4 gives timelines for developement and coding, but misses that AI Agents can do everything 100x faster.
- Claude 4 starts to talk about legacy code within a day of development - morning code, afternoon it is legacy already
- Claude 4 often starts answering the previous questions and repeating solutions again (maybe after summarizing the conversation?), which leads retrieving data again for context and slowing down and sometimes mixing the code
- Working an hour with ai agent halts VSC, consoles get red, and UI unsresponsive Must reboot.
- AttributeError: 'PythonParser' object has no attribute 'parse' -> parse_code !!!
  The parser uses parse_code method.
- Claude 4 overuses icons in docs and app, which is extremely naive
- 
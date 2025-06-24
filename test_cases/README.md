# SVCS Targeted Test Cases

This directory contains specialized test cases designed to trigger specific event types that were missing in our main test suite.

## Structure

```
test_cases/
├── python/
│   ├── comprehensions/        # Testing list/dict/generator comprehensions
│   ├── decorators/            # Testing decorator addition/removal
│   ├── lambdas_functional/    # Testing lambda usage and functional programming
│   └── augmented_assignment/  # Testing augmented assignments (+=, -=, etc.)
├── javascript/
│   └── functional/            # Testing functional programming patterns
└── php/
    └── inheritance/           # Testing inheritance hierarchy changes
```

## Running Tests

Use the `run_targeted_tests.py` script in the root directory to run all test cases:

```bash
python run_targeted_tests.py
```

## Event Types Detected

Our targeted test cases successfully detected the following previously missing event types:

1. `comprehension_usage_changed` - List, dictionary, and generator comprehensions
2. `decorator_added` - Addition of function and class decorators
3. `lambda_usage_changed` - Introduction and modification of lambda functions
4. `functional_programming_adopted` - Shift from imperative to functional paradigms
5. `augmented_assignment_changed` - Use of operators like +=, -=, *=, etc.

## Still Missing Event Types

Some event types remain undetected:

1. `decorator_removed` - Removing decorators from functions/classes
2. `inheritance_changed` - Changes to class inheritance hierarchies
3. `yield_pattern_changed` - Changes to generator yield statements

## Adding New Test Cases

To add a new test case:

1. Create a directory for the test case: `test_cases/{language}/{test_case}/`
2. Add `before.{ext}` and `after.{ext}` files
3. Update `run_targeted_tests.py` to include the new test case

## Results

The targeted test cases have significantly increased our event type coverage, with 26 unique event types detected across 145 total events. This confirms that our semantic analyzer is capable of detecting a wide range of semantic changes when provided with appropriate test cases.

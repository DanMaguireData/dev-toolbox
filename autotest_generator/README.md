# AutoTest Generator
An AI-powered tool that analyzes Python functions and automatically generates comprehensive pytest unit tests, complete with edge case coverage.

This tool uses a multi-agent graph built with LangGraph to orchestrate a sophisticated pipeline of code analysis, test planning, code generation, and iterative refinement.

### Features
* Automated Code Analysis: Uses Python's ast module to reliably parse function signatures, docstrings, and code.
* High-Quality Test Generation: Creates clean, readable pytest files that follow best practices.
* Edge Case and Error Coverage: Intelligently plans for and generates tests for typical inputs, edge cases (e.g., zero, large numbers), and expected error conditions (e.g., TypeError).
* Stateful, Iterative Refinement: A "Reviewer" agent critiques each generated test, forcing a "Coder" agent to retry until the code is correct, ensuring high quality.
* Mirrored Test Directory Structure: Automatically creates test files in a tests/ directory that mirrors your source code's structure for perfect organization.

### Prerequisites
* Python 3.9+
* An OpenAI API key.

Installation
1. Navigate to the Tool's Directory:
From the root of the dev-workbench repository, navigate here:
```bash
cd tools/autotest_generator
```

2. Create and Activate a Virtual Environment (Recommended):
```bash
python -m venv venv
source venv/bin/activate
# On Windows, use: venv\Scripts\activate
```

3. Install Dependencies:
This tool has its own set of requirements.
```bash
pip install -r requirements.txt
```

4. Set Up Your API Key:
Create a file named .env in this directory (tools/autotest_generator/). Add your OpenAI API key to it:
```bash
# In .env
OPENAI_API_KEY="sk-..."
```
### Usage
The tool is configured and run directly from the main.py script.
1. Configure the Target Function:
Open main.py and modify the initial_input dictionary at the bottom of the file to point to the Python file and function you want to test.
```python
# In main.py
if __name__ == "__main__":
    initial_input = {
        "file_path": "example_code/math.py",
        "function_name": "add"
    }
    # ... rest of the script
```
2. Run the Script:
```bash
python main.py
```

The script will print its progress and, upon completion, save the generated test file in the root tests/ directory, mirroring the path of the source file.

### How It Works
The tool operates as a state machine (a graph) with the following key steps:
1. Analyze: The input Python file is parsed to extract the target function's code and metadata.
2. Plan: An "Planner" agent receives the analysis and creates a structured TestSuite object, outlining all the happy path, edge, and error cases to test.
3. Generate & Refine Loop: For each test case in the plan:
a. A "Coder" agent writes a single pytest function.
b. A "Reviewer" agent critiques the generated code.
c. If the code is not perfect, it is sent back to the Coder with feedback for a retry.
d. Once the code is deemed "PERFECT", it's accepted.
4. Finalize: All the accepted test snippets are assembled into a single, complete test file and saved to the appropriate location.

### Example
Given this input file example_code/math.py:
```python
def add(a: int, b: int) -> int:
    """Adds two integers and returns the result."""
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError("Both inputs must be integers.")
    return a + b
```

The tool will generate a test file at tests/example_code/math/test_add.py:

```python
import pytest
from example_code.math import add

def test_add_positive_integers():
    """Tests adding two positive integers."""
    assert add(2, 3) == 5

def test_add_with_zero():
    """Tests adding an integer and zero."""
    assert add(7, 0) == 7

def test_add_with_string_input_raises_type_error():
    """Tests that adding a string raises a TypeError."""
    with pytest.raises(TypeError):
        add("a", 5)

# ... and many more test cases ...
```
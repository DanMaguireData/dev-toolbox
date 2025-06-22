"""Functions responsible for loading and parsing files."""

import ast
import os
from typing import List, Optional, TypedDict


class FunctionDetails(TypedDict):
    """Typing used for function details."""

    code: str
    docstring: Optional[str]
    signature: str


def get_file_contents(filename: str) -> str:
    """Function opens a file and returns contents as string."""
    with open(filename, "r", encoding="utf-8") as file:
        source_code = file.read()
    return source_code


def get_file_function_nodes(file_contents: str) -> List[ast.FunctionDef]:
    """Function takes the contents of a file before parsing out the function
    nodes.

    Args:
        file_contents (str):
            A string of the file contents of a .py file

    Returns:
        List of the function nodes from .py file
    """
    tree = ast.parse(file_contents)
    function_nodes = []
    for node in ast.walk(tree):
        # Walk the tree to find a function with the matching name.
        if isinstance(node, ast.FunctionDef):
            function_nodes.append(node)
    return function_nodes


def get_function_node_code(
    source_code: str, function_node: ast.FunctionDef
) -> FunctionDetails:
    """Function takes the contents of a .py file and a function node and parses
    out the code and docstring for that function.

    Args:
        source_code (str):
            A string of the file contents of a .py file
        function_node (ast.FunctionDef):
            A funtion node that has been extracted from the file

    Returns:
        A dictionary containing code and details of the function

     Throws:
        ValueError: The fucntion cannot be extracted
    """
    function_code = ast.get_source_segment(source_code, function_node)

    # If function cannot be extracted throw error
    if not function_code:
        raise ValueError(
            f"Function '{function_node.name}' could not be extracted."
        )
    docstring = ast.get_docstring(function_node)
    signature = f"def {function_node.name}({ast.unparse(function_node.args)}):"
    return {
        "code": function_code,
        "docstring": docstring,
        "signature": signature,
    }


def get_function_details(
    file_path: str, function_name: str
) -> FunctionDetails:
    """Function loads the contents of a .py file and extracts the pertinent
    infromation about the specified function from the code.

    Args:
        file_path (str):
            The location of the file
        function_name (str):
            The name of the function to be parsed

    Returns:
        A dictionary containing code and details of the function

    Throws:
        ValueError: The funciton cannot be found within the file
    """
    source_code = get_file_contents(file_path)
    function_nodes = get_file_function_nodes(source_code)
    function_node = None
    for node in function_nodes:
        if node.name == function_name:
            function_node = node
    if not function_node:
        raise ValueError(
            f"Function '{function_name}' not found in '{file_path}'."
        )
    return get_function_node_code(source_code, function_node)


def save_test_file(
    generated_code: str,
    source_file_path: str,
    function_name: str,
    base_test_dir: str = "tests",
) -> str:
    """Saves the generated test code to a file, mirroring the source directory
    structure.

    For a source file at 'src/utils/string_helpers.py' and function
    'format_title', it will create a test file at
    'tests/src/utils/string_helpers/test_format_title.py'.

    Args:
        generated_code:
            The string content of the test file.
        source_file_path:
            The relative path to the source Python file that was tested.
        function_name:
            The name of the function that was tested.
        base_test_dir:
            The root directory for all tests (e.g., 'tests').

    Returns:
        The full path to the newly created test file.
    """
    # 1. Get the directory part of the source path.
    source_dir = os.path.dirname(source_file_path)

    # 2. Get the name of the source file without its .py extension.
    # e.g., 'example_code/deeply/nested/code.py' -> 'code'
    module_name = os.path.splitext(os.path.basename(source_file_path))[0]

    # 3. Construct the target subdirectory by joining the base test directory,
    #    the source's directory path, and the module name. The module name
    #    becomes a directory itself to group tests for all functions in that
    #    file.
    test_subdirectory = os.path.join(base_test_dir, source_dir, module_name)

    # 4. Create the specific test filename based on the function name.
    # e.g., 'test_add.py'
    test_filename = f"test_{function_name}.py"

    # 5. Combine the subdirectory and filename into the full output path.
    output_path = os.path.join(test_subdirectory, test_filename)
    print(output_path)

    # 6. Ensure the entire directory path exists before writing the file.
    os.makedirs(test_subdirectory, exist_ok=True)

    # 7. Write the generated code to the new, specific file path.
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(generated_code)

    print(f"\n--- Test file saved to {output_path} ---")

    return output_path

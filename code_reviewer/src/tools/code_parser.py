"""Tools for pasring out python files."""

import ast
import os
from typing import Any, Dict, List, Tuple


def get_python_files(directory: str) -> List[str]:
    """Recursively find all Python files in a directory."""
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files


def parse_file_ast(file_path: str) -> Tuple[str, Dict[str, Any]]:
    """Parses a single Python file and returns its AST and a summary.

    This is a "tool" our agents can call.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        parsed_ast = ast.parse(content)

        summary = {
            "file_path": file_path,
            "imports": [
                node.names[0].name
                for node in ast.walk(parsed_ast)
                if isinstance(node, ast.Import)
            ],
            "functions": [
                node.name
                for node in ast.walk(parsed_ast)
                if isinstance(node, ast.FunctionDef)
            ],
            "classes": [
                node.name
                for node in ast.walk(parsed_ast)
                if isinstance(node, ast.ClassDef)
            ],
            "docstring": ast.get_docstring(parsed_ast) is not None,
        }
        return content, summary
    except Exception as e:
        return "", {"error": str(e), "file_path": file_path}

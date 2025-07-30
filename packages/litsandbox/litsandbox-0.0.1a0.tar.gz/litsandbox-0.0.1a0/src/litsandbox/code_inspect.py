import ast
import inspect
import textwrap
from typing import Callable, List


class UnsupportedCodeError(Exception):
    pass


def validate_python_code(code: str) -> None:
    """Validates Python code for syntax errors.

    Args:
        code: The Python code string to validate

    Raises:
        SyntaxError: If the code has syntax errors
        ValueError: If the code is empty or only whitespace
        IndentationError: If the code has improper indentation

    Note:
        This validation only catches syntax-level errors. Runtime errors like
        NameError or TypeError can only be caught when the code is actually executed.
    """
    if not code or not code.strip():
        raise ValueError("Code cannot be empty or only whitespace")

    try:
        ast.parse(code)
    except (SyntaxError, IndentationError) as e:
        error_type = type(e).__name__
        raise type(e)(f"Invalid Python {error_type.lower()}: {e}") from e


def get_imports(code: str) -> List[str]:
    """Get all the imports in a parsed source code."""
    tree = ast.parse(code)
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.append(node.names[0].name)
    return imports


def func_to_source(func: Callable) -> str:
    """Converts a function to a string of code.

    Args:
        func: The function to convert to code

    Returns:
        The code string

    Example:
        >>> def fn(a, b):
        ...     import numpy as np
        ...     print(a, b)
        >>> func_to_code(fn)
        'import numpy as np\nprint(a, b)'
    """
    source = inspect.getsource(func)
    if source.startswith(" "):
        raise UnsupportedCodeError("Code must be defined in global scope")
    source = textwrap.dedent(source)
    validate_python_code(source)
    return source

import ast
import os

def test_all_test_functions_have_docstrings():
    """
    Ensure all test functions in the tests directory have docstrings for maintainability.
    """
    test_dir = os.path.dirname(__file__)
    for fname in os.listdir(test_dir):
        if fname.startswith("test_") and fname.endswith(".py"):
            with open(os.path.join(test_dir, fname)) as f:
                tree = ast.parse(f.read(), filename=fname)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                    assert ast.get_docstring(node), f"{fname}:{node.name} is missing a docstring"

"""Unit tests for no static methods principle (NoStatic)."""

import ast

from flake8_elegant_objects.base import Source
from flake8_elegant_objects.no_static import NoStatic


class TestNoStatic:
    """Test cases for static method violations detection."""

    def _check_code(self, code: str) -> list[str]:
        """Helper to check code and return violation messages."""
        tree = ast.parse(code)
        checker = NoStatic()
        violations = []

        def visit(node: ast.AST, current_class: ast.ClassDef | None = None) -> None:
            if isinstance(node, ast.ClassDef):
                current_class = node
            source = Source(node, current_class, tree)
            violations.extend(checker.check(source))
            for child in ast.iter_child_nodes(node):
                visit(child, current_class)

        visit(tree)
        return [v.message for v in violations]

    def test_static_method_violation(self) -> None:
        """Test detection of static methods."""
        code = """
class Test:
    @staticmethod
    def process_data():
        pass

    @classmethod
    def create_instance(cls):
        pass
"""
        violations = self._check_code(code)
        static_violations = [v for v in violations if "EO009" in v]
        assert len(static_violations) == 2

    def test_regular_methods_valid(self) -> None:
        """Test that regular methods are valid."""
        code = """
class Example:
    def regular_method(self):
        return "regular"
"""
        violations = self._check_code(code)
        assert len(violations) == 0

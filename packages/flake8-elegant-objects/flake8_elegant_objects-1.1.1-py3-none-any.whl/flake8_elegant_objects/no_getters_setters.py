"""No getters/setters principle checker for Elegant Objects violations."""

import ast

from .base import ErrorCodes, Source, Violations, is_method, violation


class NoGettersSetters:
    """Checks for getter/setter methods (EO007)."""

    def check(self, source: Source) -> Violations:
        """Check source for getter/setter violations."""
        node = source.node
        if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            return []
        return self._check_getters_setters(node)

    def _check_getters_setters(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> Violations:
        """Check for getter/setter methods."""
        if not is_method(node) or node.name.startswith("_"):
            return []

        # Skip methods with @property decorator
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "property":
                return []

        name = node.name.lower()
        original_name = node.name

        # Check for getter patterns
        if (
            name.startswith("get_")
            or (
                name.startswith("get")
                and len(original_name) > 3
                and original_name[3].isupper()
            )
            or name == "get"
        ):
            return violation(node, ErrorCodes.EO007.format(name=node.name))

        # Check for setter patterns
        if (
            name.startswith("set_")
            or (
                name.startswith("set")
                and len(original_name) > 3
                and original_name[3].isupper()
            )
            or name == "set"
        ):
            return violation(node, ErrorCodes.EO007.format(name=node.name))

        return []

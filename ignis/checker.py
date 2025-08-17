from ast_nodes import *


class NodeVisitor:
    """Base class for visiting AST nodes."""

    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        # Recursively visit children of the node
        for field, value in node.__dict__.items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, AST):
                        self.visit(item)
            elif isinstance(value, AST):
                self.visit(value)


class Checker(NodeVisitor):
    def __init__(self, file_path, source_lines):
        self.file_path = file_path
        self.source_lines = source_lines
        self.warnings = []

    def _add_warning(self, code, message, node):
        # This can be expanded later to show code context for warnings too
        print(f"Warning ({code}): {message}")

    def check(self, tree):
        self.visit(tree)

    def _has_break(self, node):
        """Recursively search for a BreakStmt in an AST subtree."""
        if isinstance(node, BreakStmt):
            return True
        # Check children
        for field, value in node.__dict__.items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, AST) and self._has_break(item):
                        return True
            elif isinstance(value, AST) and self._has_break(value):
                return True
        return False

    def visit_LoopStmt(self, node):
        if not self._has_break(node.body):
            self._add_warning("W001", "'loop' statement has no 'break' and may run forever.\n", node)

        # Continue checking the rest of the tree
        self.generic_visit(node)

    def visit_WhileStmt(self, node):
        """Check for 'while(true)' style loops without a break."""
        # Check if the condition is a non-zero integer literal
        is_constant_true = isinstance(node.condition, Num) and node.condition.value != 0

        if is_constant_true:
            if not self._has_break(node.body):
                self._add_warning("W002", "'while' loop with a constant condition has no 'break' and may run forever.\n", node)

        # Continue checking the rest of the tree
        self.generic_visit(node)

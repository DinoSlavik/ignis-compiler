from ast_nodes import *

class NodeVisitor:
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        for field, value in node.__dict__.items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, AST): self.visit(item)
            elif isinstance(value, AST): self.visit(value)

class Checker(NodeVisitor):
    def __init__(self, reporter):
        self.reporter = reporter

    def _get_token_from_node(self, node):
        if hasattr(node, 'token'): return node.token
        if hasattr(node, 'op'): return node.op
        if hasattr(node, 'name_node'): return node.name_node.token
        if hasattr(node, 'var_node'): return node.var_node.token
        if isinstance(node, MemberAccess): return self._get_token_from_node(node.left)
        if isinstance(node, LoopStmt):
            # Try to get a token from the body for better location
            if node.body and node.body.children:
                return self._get_token_from_node(node.body.children[0])
        return None

    def check(self, tree):
        self.visit(tree)

    def _has_break(self, node):
        if isinstance(node, BreakStmt): return True
        for field, value in node.__dict__.items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, AST) and self._has_break(item): return True
            elif isinstance(value, AST) and self._has_break(value): return True
        return False

    def visit_LoopStmt(self, node):
        if not self._has_break(node.body):
            self.reporter.warning("W001", "'loop' statement has no 'break' and may run forever.", self._get_token_from_node(node))
        self.generic_visit(node)

    def visit_WhileStmt(self, node):
        is_constant_true = isinstance(node.condition, Num) and node.condition.value != 0
        if is_constant_true:
            if not self._has_break(node.body):
                self.reporter.warning("W002", "'while' loop with a constant true condition has no 'break' and may run forever.", self._get_token_from_node(node))
        self.generic_visit(node)

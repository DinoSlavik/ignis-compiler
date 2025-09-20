from ast_nodes import *
from lexer import TokenType, Token


class NodeVisitor:
    def visit(self, node, *args, **kwargs):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node, *args, **kwargs)

    def generic_visit(self, node, *args, **kwargs):
        # Поки що ми не будемо видавати помилку, а просто ігноруватимемо невідомі вузли
        # self.error("E003", f"Unsupported AST node '{type(node).__name__}'", node)
        pass


class CodeGeneratorCpp(NodeVisitor):
    def __init__(self, reporter):
        self.reporter = reporter
        self.cpp_code = []

    def error(self, code, message, node):
        # У майбутньому тут буде логіка для отримання токена з вузла
        self.reporter.error(code, message, None)

    def generate(self, tree):
        # Тут буде основна логіка генерації
        self.visit(tree)
        # Поки що повертаємо порожній рядок
        return "\n".join(self.cpp_code)

    def visit_Program(self, node):
        # На наступному кроці ми почнемо додавати сюди логіку
        pass
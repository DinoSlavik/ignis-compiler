from ast_nodes import *
from lexer import TokenType, Token


class SymbolTable:
    def __init__(self):
        # Стек областей видимості. Кожен елемент - це словник {ім'я_символу: інформація}.
        # Починаємо з глобальної області видимості.
        self.scopes = [{}]

    def enter_scope(self):
        """Входимо в нову область видимості (наприклад, тіло функції або блок)."""
        self.scopes.append({})

    def exit_scope(self):
        """Виходимо з поточної області видимості."""
        assert len(self.scopes) > 1, "Cannot exit the global scope."
        self.scopes.pop()

    # ### MODIFIED ###: Замість фіксованих параметрів (is_mutable),
    # ми приймаємо словник 'properties'. Це робить систему гнучкою
    # для майбутнього додавання властивостей, таких як 'bits', 'encoding' тощо.
    def add_symbol(self, name, symbol_type, properties=None):
        """
        Додає новий символ до поточної (найглибшої) області видимості.
        Повертає True, якщо символ успішно додано, і False, якщо він вже існує.
        """
        if properties is None:
            properties = {}

        if name in self.scopes[-1]:
            return False  # Символ вже оголошено в цій області
        self.scopes[-1][name] = {'type': symbol_type, 'properties': properties}
        return True

    def lookup_symbol(self, name):
        """
        Шукає символ, починаючи з поточної області видимості і рухаючись до глобальної.
        Повертає інформацію про символ або None, якщо його не знайдено.
        """
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

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
        self.symbol_table = SymbolTable()
        self.struct_info = {}

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

    # Реалізує двопрохідний аналіз: спочатку збираємо всі структури,
    # а потім перевіряємо решту коду.
    def visit_Program(self, node):
        for decl in node.declarations:
            if isinstance(decl, StructDef):
                self.visit(decl)

        # Другий прохід: перевіряємо решту оголошень (функції, глобальні змінні)
        for decl in node.declarations:
            if not isinstance(decl, StructDef):
                self.visit(decl)

    def visit_StructDef(self, node: StructDef):
        struct_name = node.name
        if struct_name in self.struct_info:
            self.reporter.error(
                "SE001", f"Struct '{struct_name}' is already defined.",
                self._get_token_from_node(node)
            )
            return

        struct_type = Type(Token(TokenType.IDENTIFIER, struct_name))
        self.symbol_table.add_symbol(struct_name, struct_type, properties={'is_type': True})

        fields = {}
        for field in node.fields:
            field_name = field.var_node.value
            if field_name in fields:
                self.reporter.error(
                    "SE002", f"Duplicate field '{field_name}' in struct '{struct_name}'.",
                    self._get_token_from_node(field.var_node)
                )
            else:
                fields[field_name] = field.type_node

        self.struct_info[struct_name] = {'fields': fields}

    def visit_Block(self, node):
        self.symbol_table.enter_scope()
        for child in node.children:
            self.visit(child)
        self.symbol_table.exit_scope()

    def visit_LoopStmt(self, node):
        if not self._has_break(node.body):
            self.reporter.warning(
                "W001", "'loop' statement has no 'break' and may run forever.",
                self._get_token_from_node(node)
            )
        self.symbol_table.enter_scope()
        self.generic_visit(node)
        self.symbol_table.exit_scope()

    def visit_WhileStmt(self, node):
        is_constant_true = isinstance(node.condition, Num) and node.condition.value != 0
        if is_constant_true:
            if not self._has_break(node.body):
                self.reporter.warning(
                    "W002", "'while' loop with a constant true condition has no 'break' and may run forever.",
                    self._get_token_from_node(node)
                )
        self.symbol_table.enter_scope()
        self.generic_visit(node)
        self.symbol_table.exit_scope()

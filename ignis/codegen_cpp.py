from ast_nodes import *
from lexer import TokenType, Token


class CppWriter:
    def __init__(self):
        self.code = []
        self.indent_level = 0

    def enter_block(self):
        self.add_line('{')
        self.indent_level += 1

    def exit_block(self):
        self.indent_level -= 1
        self.add_line('}')

    def add_line(self, line):
        indent = '    ' * self.indent_level
        self.code.append(f"{indent}{line}")

    def get_code(self):
        return "\n".join(self.code)


class NodeVisitor:
    def visit(self, node, *args, **kwargs):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node, *args, **kwargs)

    def generic_visit(self, node, writer):
        print(f"Warning: C++ code generation for {type(node).__name__} is not implemented yet.")
        return f"/* {type(node).__name__} not implemented */"


class CodeGeneratorCpp(NodeVisitor):
    def __init__(self, reporter):
        self.reporter = reporter

    def _get_token_from_node(self, node):
        if hasattr(node, 'token'): return node.token
        if hasattr(node, 'op'): return node.op
        if hasattr(node, 'var_node'): return node.var_node.token
        return None

    def error(self, code, message, node):
        self.reporter.error(code, message, self._get_token_from_node(node))

    def _map_type(self, type_node, is_const=False):
        base_type = type_node.value
        cpp_type = {'int': 'int64_t', 'char': 'char'}.get(base_type, base_type)
        const_prefix = "const " if is_const else ""
        type_str = f"{const_prefix}{cpp_type}"
        if type_node.pointer_level > 0:
            type_str += ' '
        return type_str + '*' * type_node.pointer_level

    def generate(self, tree):
        writer = CppWriter()
        self.visit(tree, writer)
        return writer.get_code()

    # --- Global Scope Visitors ---
    def visit_Program(self, node: Program, writer: CppWriter):
        writer.add_line('#include "ignis_runtime.h"')
        writer.add_line('#include <cstdint>')
        writer.add_line('')
        for decl in node.declarations:
            self.visit(decl, writer)
            writer.add_line('')

    def visit_FunctionDecl(self, node: FunctionDecl, writer: CppWriter):
        return_type = "int" if node.func_name == "main" else self._map_type(node.type_node)
        func_name = node.func_name
        params_list = []
        for param in node.params:
            param_type = self._map_type(param.type_node)
            if param_type == "char *":
                param_type = "const char *"
            param_name = param.var_node.value
            params_list.append(f"{param_type} {param_name}")
        params = ", ".join(params_list)
        writer.add_line(f"{return_type} {func_name}({params})")
        self.visit(node.body, writer)

    # --- Statement Visitors (add lines to writer) ---
    def visit_Block(self, node: Block, writer: CppWriter):
        writer.enter_block()
        for child in node.children:
            if isinstance(child, FunctionCall):
                # Якщо виклик функції стоїть окремо, він є інструкцією
                expr_code = self.visit_expr(child, writer)
                writer.add_line(f"{expr_code};")
            else:
                self.visit(child, writer)
        writer.exit_block()

    def visit_VarDecl(self, node: VarDecl, writer: CppWriter):
        is_const_string = isinstance(node.assign_node, StringLiteral)
        var_type = self._map_type(node.type_node, is_const=is_const_string)
        var_name = node.var_node.value
        if node.assign_node:
            value_expr = self.visit_expr(node.assign_node, writer)
            writer.add_line(f"{var_type} {var_name} = {value_expr};")
        else:
            writer.add_line(f"{var_type} {var_name};")

    def visit_Assign(self, node: Assign, writer: CppWriter):
        left_expr = self.visit_expr(node.left, writer)
        right_expr = self.visit_expr(node.right, writer)
        writer.add_line(f"{left_expr} = {right_expr};")

    def visit_Return(self, node: Return, writer: CppWriter):
        if node.value:
            return_value = self.visit_expr(node.value, writer)
            writer.add_line(f"return {return_value};")
        else:
            writer.add_line("return;")

    def visit_LoopStmt(self, node: LoopStmt, writer: CppWriter):
        writer.add_line("for (;;)")
        self.visit(node.body, writer)

    def visit_IfExpr(self, node: IfExpr, writer: CppWriter):
        condition = self.visit_expr(node.condition, writer)
        writer.add_line(f"if ({condition})")
        self.visit(node.if_block, writer)
        if node.else_block:
            writer.add_line("else")
            self.visit(node.else_block, writer)

    def visit_BreakStmt(self, node: BreakStmt, writer: CppWriter):
        writer.add_line("break;")

    # --- Expression Visitors (return a string) ---
    def visit_expr(self, node, writer):
        return self.visit(node, writer)

    def visit_Num(self, node: Num, writer: CppWriter):
        return str(node.value)

    def visit_CharLiteral(self, node: CharLiteral, writer: CppWriter):
        val = node.value
        if val == 10: return "'\\n'"
        if val == 9: return "'\\t'"
        if val == 13: return "'\\r'"
        if val == 39: return "'\\''"
        if val == 92: return "'\\\\'"
        return f"'{chr(val)}'"

    def visit_StringLiteral(self, node: StringLiteral, writer: CppWriter):
        result = ""
        for char in node.value:
            if char == '\n':
                result += '\\n'
            elif char == '\t':
                result += '\\t'
            elif char == '\r':
                result += '\\r'
            elif char == '"':
                result += '\\"'
            elif char == '\\':
                result += '\\\\'
            else:
                result += char
        return f'"{result}"'

    def visit_Var(self, node: Var, writer: CppWriter):
        return node.value

    def visit_BinOp(self, node: BinOp, writer: CppWriter):
        left_expr = self.visit_expr(node.left, writer)
        right_expr = self.visit_expr(node.right, writer)
        op = node.op.value
        return f"({left_expr} {op} {right_expr})"

    def visit_UnaryOp(self, node: UnaryOp, writer: CppWriter):
        op_type = node.op.type
        expr = self.visit_expr(node.expr, writer)
        if op_type == TokenType.KW_DEREF:
            return f"(*{expr})"
        if op_type == TokenType.KW_ADDR:
            return f"(&{expr})"
        return f"/* UnaryOp {node.op.value} not implemented */"

    def visit_FunctionCall(self, node: FunctionCall, writer: CppWriter):
        func_name = node.name_node.value
        if func_name == 'print':
            func_name = 'print_int'
        elif func_name == 'putchar':
            func_name = 'ignis_putchar'
        elif func_name == 'getchar':
            func_name = 'ignis_getchar'

        arg_list = [self.visit_expr(arg, writer) for arg in node.args]
        args_str = ", ".join(arg_list)

        return f"{func_name}({args_str})"
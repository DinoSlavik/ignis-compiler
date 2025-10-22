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
        self.symbol_table = {}
        self.struct_info = {}

    def _get_token_from_node(self, node):
        if hasattr(node, 'token'): return node.token
        if hasattr(node, 'op'): return node.op
        if hasattr(node, 'var_node'): return node.var_node.token
        return None

    def error(self, code, message, node):
        self.reporter.error(code, message, self._get_token_from_node(node))

    def _map_type(self, type_node, is_const=False):
        if type_node is None: return "void"
        base_type = type_node.value
        cpp_type = {'int': 'int64_t', 'char': 'char'}.get(base_type, base_type)
        const_prefix = "const " if is_const else ""
        type_str = f"{const_prefix}{cpp_type}"
        if type_node.pointer_level > 0: type_str += ' '
        return type_str + '*' * type_node.pointer_level

    def _get_node_type(self, node):
        if isinstance(node, Num): return Type(Token(TokenType.KW_INT, 'int'))
        if isinstance(node, CharLiteral): return Type(Token(TokenType.KW_CHAR, 'char'))
        if isinstance(node, StringLiteral): return Type(Token(TokenType.KW_CHAR, 'char'), pointer_level=1)
        if isinstance(node, Var):
            if node.value in self.symbol_table:
                return self.symbol_table[node.value]
            self.error("E004", f"Undeclared variable '{node.value}'", node)
        if isinstance(node, BinOp):
            left_type = self._get_node_type(node.left)
            right_type = self._get_node_type(node.right)
            if left_type.pointer_level > 0: return left_type
            if right_type.pointer_level > 0: return right_type
            return left_type
        if isinstance(node, UnaryOp):
            base_type = self._get_node_type(node.expr)
            if node.op.type == TokenType.KW_ADDR:
                return Type(base_type.token, base_type.pointer_level + 1)
            if node.op.type == TokenType.KW_DEREF:
                if base_type.pointer_level == 0: self.error("E005", "Cannot dereference a non-pointer type.", node)
                return Type(base_type.token, base_type.pointer_level - 1)
        if isinstance(node, MemberAccess):
            struct_type = self._get_node_type(node.left)
            struct_name = struct_type.value
            if struct_name not in self.struct_info: self.error("E006", f"Unknown struct type '{struct_name}'", node)
            field_name = node.right.value
            if field_name not in self.struct_info[struct_name]: self.error("E007",
                                                                           f"Struct '{struct_name}' has no field '{field_name}'",
                                                                           node)
            return self.struct_info[struct_name][field_name]
        return Type(Token(TokenType.KW_INT, 'int'))

    def generate(self, tree):
        writer = CppWriter()
        self.visit(tree, writer)
        return writer.get_code()

    def visit_Program(self, node: Program, writer: CppWriter):
        writer.add_line('#include "ignis_runtime.h"')
        writer.add_line('#include <cstdint>')
        writer.add_line('#include <typeinfo>')
        writer.add_line('')
        for decl in node.declarations:
            if isinstance(decl, StructDef):
                self.struct_info[decl.name_token.value] = {field.var_node.value: field.type_node for field in decl.fields}
                writer.add_line(f"struct {decl.name_token.value};")
        writer.add_line('')
        for decl in node.declarations:
            self.visit(decl, writer)
            writer.add_line('')

    def visit_FunctionDecl(self, node: FunctionDecl, writer: CppWriter):
        self.symbol_table = {}
        for param in node.params:
            self.symbol_table[param.var_node.value] = param.type_node

        is_void_func = node.type_node == Type(TokenType.KW_VOID)

        if is_void_func:
            return_type = "void"
        else:
            return_type = "int" if node.func_name == "main" else self._map_type(node.type_node)

        func_name = node.func_name
        params_list = []
        for param in node.params:
            param_type = self._map_type(param.type_node)
            if param_type == "char *": param_type = "const char *"
            param_name = param.var_node.value
            params_list.append(f"{param_type} {param_name}")
        params = ", ".join(params_list)
        writer.add_line(f"{return_type} {func_name}({params})")

        self.visit(node.body, writer, is_function_body=True, is_void=is_void_func)

    def visit_Block(self, node: Block, writer: CppWriter, is_function_body=False, is_void=False, is_expr_context=False):
        old_symbol_table = self.symbol_table.copy()
        writer.enter_block()
        for child in node.children[:-1]:
            self.visit_statement(child, writer)
        if node.children:
            last_child = node.children[-1]
            if (is_function_body or is_expr_context) and not is_void and not isinstance(last_child, Return):
                expr_code = self.visit_expr(last_child)
                writer.add_line(f"return {expr_code};")
            else:
                self.visit_statement(last_child, writer)
        writer.exit_block()
        self.symbol_table = old_symbol_table

    def visit_statement(self, node, writer):
        if isinstance(node, (FunctionCall, Assign, Free, BinOp, UnaryOp, Var, Num, CharLiteral, StringLiteral)):
            expr_code = self.visit_expr(node)
            writer.add_line(f"{expr_code};")
        else:
            self.visit(node, writer)

    def visit_VarDecl(self, node: VarDecl, writer: CppWriter):
        var_name = node.var_node.value
        if var_name in self.symbol_table:
            self.error("E008", f"Variable '{var_name}' is already declared in this scope.", node)
        self.symbol_table[var_name] = node.type_node
        is_const_string = isinstance(node.assign_node, StringLiteral)
        is_mut = node.is_mutable
        var_type = self._map_type(node.type_node, is_const=is_const_string and not is_mut)
        if node.assign_node:
            value_expr = self.visit_expr(node.assign_node)

            if isinstance(node.assign_node, (Alloc, New)):
                pointer_type_str = self._map_type(node.type_node).strip()
                if isinstance(node.assign_node, Alloc):
                    value_expr = f"reinterpret_cast<{pointer_type_str}>({value_expr})"

            writer.add_line(f"{var_type} {var_name} = {value_expr};")
        else:
            writer.add_line(f"{var_type} {var_name};")

    def visit_BinOp(self, node: BinOp, *args, **kwargs):
        if node.op.type == TokenType.TYPE_EQUAL:
            left_type = self._get_node_type(node.left)
            right_type = self._get_node_type(node.right)
            if left_type.value == right_type.value and left_type.pointer_level == right_type.pointer_level:
                return "true"
            else:
                return "false"
        left_expr = self.visit_expr(node.left)
        right_expr = self.visit_expr(node.right)
        op_type = node.op.type

        op_map = {
            TokenType.KW_OR: '||', TokenType.KW_AND: '&&',
            TokenType.KW_BOR: '|', TokenType.KW_BAND: '&', TokenType.KW_BXOR: '^',

            TokenType.EQUAL: '==', TokenType.NOT_EQUAL: '!=',
            TokenType.LESS: '<', TokenType.LESS_EQUAL: '<=',
            TokenType.GREATER: '>', TokenType.GREATER_EQUAL: '>=',

            TokenType.PLUS: '+', TokenType.MINUS: '-', TokenType.MULTIPLY: '*', TokenType.DIVIDE: '/'
        }

        if op_type in op_map:
            return f"({left_expr} {op_map[op_type]} {right_expr})"

        # For some reason cpp doesn't support xor by default...
        if op_type == TokenType.KW_XOR: return f"(!{left_expr} != !{right_expr})"
        if op_type == TokenType.KW_XNOR: return f"(!{left_expr} == !{right_expr})"

        if op_type == TokenType.KW_NAND: return f"(!({left_expr} && {right_expr}))"
        if op_type == TokenType.KW_NOR:  return f"(!({left_expr} || {right_expr}))"

        if op_type == TokenType.KW_NBAND: return f"(~({left_expr} & {right_expr}))"
        if op_type == TokenType.KW_NBOR:  return f"(~({left_expr} | {right_expr}))"
        if op_type == TokenType.KW_NBXOR: return f"(~({left_expr} ^ {right_expr}))"

        # Using typeid() from typeinfo because cpp doesn't support dedicated type comparison operator
        if op_type == TokenType.TYPE_EQUAL: return f"(typeid(left_expr) == typeid(right_expr))"

        return f"/* Binary Operator '{op_type}' C++ generation not implemented */"

    def visit_MemberAccess(self, node: MemberAccess):
        left_expr_str = self.visit_expr(node.left)
        left_type = self._get_node_type(node.left)
        op = "->" if left_type.pointer_level > 0 else "."
        return f"{left_expr_str}{op}{node.right.value}"

    def visit_ConstDecl(self, node: ConstDecl, writer: CppWriter):
        var_type = self._map_type(node.type_node, is_const=True)
        var_name = node.var_node.value
        value_expr = self.visit_expr(node.assign_node)
        writer.add_line(f"constexpr {var_type} {var_name} = {value_expr};")

    def visit_StructDef(self, node: StructDef, writer: CppWriter):
        writer.add_line(f"struct {node.name_token.value}")
        writer.enter_block()
        for field in node.fields:
            field_type = self._map_type(field.type_node)
            field_name = field.var_node.value
            writer.add_line(f"{field_type} {field_name};")
        writer.exit_block()
        writer.add_line(";")

    def visit_Return(self, node: Return, writer: CppWriter):
        if node.value:
            writer.add_line(f"return {self.visit_expr(node.value)};")
        else:
            writer.add_line("return;")

    def visit_WhileStmt(self, node: WhileStmt, writer: CppWriter):
        writer.add_line(f"while ({self.visit_expr(node.condition)})")
        self.visit(node.body, writer)

    def visit_LoopStmt(self, node: LoopStmt, writer: CppWriter):
        writer.add_line("for (;;)")
        self.visit(node.body, writer)

    def visit_ForStmt(self, node: ForStmt, writer: CppWriter):
        init_part, cond_part, inc_part = "", "", ""
        if node.init:
            if isinstance(node.init, VarDecl):
                is_const = isinstance(node.init.assign_node, StringLiteral)
                var_type = self._map_type(node.init.type_node, is_const=is_const and not node.init.is_mutable)
                var_name = node.init.var_node.value
                value_expr = self.visit_expr(node.init.assign_node)
                init_part = f"{var_type} {var_name} = {value_expr}"
            else:
                init_part = self.visit_expr(node.init)
        if node.condition: cond_part = self.visit_expr(node.condition)
        if node.increment: inc_part = self.visit_expr(node.increment)
        writer.add_line(f"for ({init_part}; {cond_part}; {inc_part})")
        self.visit(node.body, writer)

    def visit_BreakStmt(self, node: BreakStmt, writer: CppWriter):
        writer.add_line("break;")

    def visit_ContinueStmt(self, node: ContinueStmt, writer: CppWriter):
        writer.add_line("continue;")

    def visit_Alloc(self, node: Alloc):
        """Генерує виклик ignis_alloc(size)."""
        size_code = self.visit_expr(node.size_expr)
        return f"ignis_alloc({size_code})"

    def visit_New(self, node: New):
        """Генерує виділення пам'яті для нового об'єкта та приводить тип."""
        # Отримуємо C++ назву типу (напр., "MyStruct")
        cpp_type = self._map_type(node.type_node).strip()  # strip() для видалення зайвих пробілів

        # Генеруємо фінальний рядок згідно з планом
        # f"reinterpret_cast<{cpp_type}*> (ignis_alloc(sizeof({cpp_type})))"
        return f"reinterpret_cast<{cpp_type}*>(ignis_alloc(sizeof({cpp_type})))"

    def visit_Free(self, node: Free):
        """Генерує виклик ignis_free(pointer)."""
        # Free є інструкцією, тому ми не повертаємо рядок, а додаємо його до writer'а.
        # Однак, щоб вписатись в існуючу архітектуру, де visit_statement
        # очікує на рядок, ми повернемо його.
        pointer_code = self.visit_expr(node.expr)
        return f"ignis_free({pointer_code})"

    def visit_expr(self, node):
        if isinstance(node, IfExpr): return self.visit_IfExpr_expr(node)
        if isinstance(node, Block): return self.visit_Block_expr(node)
        return self.visit(node)

    # def visit_IfExpr_expr(self, node: IfExpr):
    #     writer = CppWriter()
    #     writer.add_line("[&]{")
    #     writer.indent_level += 1
    #     condition = self.visit_expr(node.condition)
    #     writer.add_line(f"if ({condition})")
    #     writer.enter_block()
    #     ret_val = self.visit_expr(node.if_block.children[0])
    #     writer.add_line(f"return {ret_val};")
    #     writer.exit_block()
    #     if node.else_block:
    #         writer.add_line("else")
    #         if isinstance(node.else_block, IfExpr):
    #             ret_val = self.visit_expr(node.else_block)
    #             writer.enter_block()
    #             writer.add_line(f"return {ret_val};")
    #             writer.exit_block()
    #         else:
    #             writer.enter_block()
    #             ret_val = self.visit_expr(node.else_block.children[0])
    #             writer.add_line(f"return {ret_val};")
    #             writer.exit_block()
    #     writer.indent_level -= 1
    #     writer.add_line("}()")
    #     return writer.get_code()

    def visit_IfExpr_expr(self, node: IfExpr):
        writer = CppWriter()
        writer.add_line("([&]() {")
        writer.indent_level += 1
        # Просто викликаємо стандартний візитор, але з прапорцем is_expr_context=True
        self.visit_IfExpr(node, writer, is_expr_context=True)
        writer.indent_level -= 1
        writer.add_line("}())")
        return writer.get_code()

    def visit_Block_expr(self, node: Block):
        writer = CppWriter()
        writer.add_line("[&]{")
        writer.indent_level += 1
        temp_writer = CppWriter()
        temp_writer.indent_level = writer.indent_level
        self.visit_Block(node, temp_writer, is_function_body=True)
        for line in temp_writer.code:
            writer.code.append(line)
        writer.indent_level -= 1
        writer.add_line("}()")
        return writer.get_code()

    def visit_IfExpr(self, node: IfExpr, writer: CppWriter, is_expr_context=False):
        condition = self.visit_expr(node.condition)
        writer.add_line(f"if ({condition})")
        self.visit(node.if_block, writer, is_expr_context=is_expr_context)
        if node.else_block:
            writer.add_line("else")
            self.visit(node.else_block, writer, is_expr_context=is_expr_context)

    def visit_Assign(self, node: Assign):
        left_expr = self.visit_expr(node.left)
        right_expr = self.visit_expr(node.right)

        if isinstance(node.right, (Alloc, New)):
            left_type = self._get_node_type(node.left)
            pointer_type_str = self._map_type(left_type).strip()

            right_expr = f"reinterpret_cast<{pointer_type_str}>({right_expr})"

        return f"{left_expr} = {right_expr}"

    def visit_Num(self, node: Num):
        return str(node.value)

    def visit_CharLiteral(self, node: CharLiteral):
        val = node.value
        if val == 10: return "'\\n'"
        if val == 9: return "'\\t'"
        return f"'{chr(val)}'"

    def visit_StringLiteral(self, node: StringLiteral):
        return f'"{node.value.encode("unicode_escape").decode("utf-8")}"'

    def visit_Var(self, node: Var):
        return node.value

    def visit_UnaryOp(self, node: UnaryOp):
        expr = self.visit_expr(node.expr)
        op_type = node.op.type

        # Це дозволяє писати речі аля
        #   deref my_struct.a = 10;
        # Я ще не певен, наскільки такий синтаксис потрібно пробачати,
        # враховуючи, що оригінально його не мало бути (`.` є "розумним" оператором).
        # QUES: Тож це потрібно буде обдумати.
        # ANSV1: Можливо це потрібно додати, однак також додати ворнінг,
        # котрий казатиме, що такий код є надлишковим та небажаним.
        # if op_type == TokenType.KW_DEREF:
        #     # Якщо розіменовуємо доступ до поля (my_struct.a),
        #     # то C++ оператор -> вже виконує розіменування.
        #     # Додатковий * не потрібен.
        #     if isinstance(node.expr, MemberAccess):
        #         return expr
        #     return f"(*{expr})"

        op_map = {
            TokenType.KW_DEREF: '(*{expr})', TokenType.KW_ADDR: '(&{expr})',
            TokenType.KW_NOT: '(!{expr})', TokenType.KW_BNOT: '(~{expr})',
            TokenType.MINUS: '(-{expr})', TokenType.PLUS: '(+{expr})'
        }

        if op_type in op_map:
            return op_map[node.op.type].format(expr=expr)

        if op_type == TokenType.KW_NNOT: return f"(({expr}) != 0)"

        if op_type == TokenType.KW_NBNOT: return f"({expr})"

        return f"/* UnaryOp {node.op.value} not implemented */"

    def visit_FunctionCall(self, node: FunctionCall):
        func_map = {'print': 'print_int', 'putchar': 'ignis_putchar', 'getchar': 'ignis_getchar'}
        func_name = func_map.get(node.name_node.value, node.name_node.value)
        args_str = ", ".join([self.visit_expr(arg) for arg in node.args])
        return f"{func_name}({args_str})"
from ast_nodes import *
from lexer import TokenType, Token


class NodeVisitor:
    def visit(self, node, *args, **kwargs):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node, *args, **kwargs)

    def generic_visit(self, node, *args, **kwargs): self.error("E003", f"Unsupported AST node '{type(node).__name__}'", node)

class CodeGenerator(NodeVisitor):
    def __init__(self, reporter):
        self.reporter = reporter
        self.assembly_code = []
        self.data_section = []
        self.symbol_table = {}
        self.struct_table = {}
        self.current_function = None
        self.stack_index = 0
        self.label_counter = 0
        self.loop_labels_stack = []
        self.string_literal_counter = 0

    def error(self, code, message, node):
        self.reporter.error(code, message, self._get_token_from_node(node))

    def warning(self, code, message, node):
        self.reporter.warning(code, message, self._get_token_from_node(node))

    def _get_token_from_node(self, node):
        if hasattr(node, 'token'): return node.token
        if hasattr(node, 'op'): return node.op
        if hasattr(node, 'name_node'): return node.name_node.token
        if hasattr(node, 'var_node'): return node.var_node.token
        if isinstance(node, MemberAccess): return self._get_token_from_node(node.left)
        return None

    def _new_label(self):
        self.label_counter += 1
        return self.label_counter

    def _get_type_size(self, type_node):
        if type_node.pointer_level > 0: return 8
        if type_node.value == 'int': return 8
        if type_node.value == 'char': return 1
        if type_node.value in self.struct_table:
            return self.struct_table[type_node.value]['size']
        self.error("E006", f"Unknown type '{type_node.value}'", type_node.token)

    def _get_node_type(self, node):
        if isinstance(node, Num): return Type(Token(TokenType.KW_INT, 'int'))
        if isinstance(node, Var):
            var_name = node.value
            if var_name in self.symbol_table: return self.symbol_table[var_name]['type']
            self.error("E004", f"Undeclared variable '{var_name}'", node)
        if isinstance(node, UnaryOp):
            base_type = self._get_node_type(node.expr)
            if node.op.type == TokenType.KW_ADDR: return Type(base_type.token, base_type.pointer_level + 1)
            if node.op.type == TokenType.KW_DEREF:
                if base_type.pointer_level == 0: self.error("E005", "Cannot dereference a non-pointer type", node)
                return Type(base_type.token, base_type.pointer_level - 1)
        if isinstance(node, BinOp):
            left_type = self._get_node_type(node.left)
            right_type = self._get_node_type(node.right)
            if left_type.pointer_level > 0 and right_type.pointer_level == 0:
                return left_type  # ptr + int -> ptr
            if right_type.pointer_level > 0 and left_type.pointer_level == 0:
                return right_type  # int + ptr -> ptr
        if isinstance(node, MemberAccess):
            struct_type = self._get_node_type(node.left)
            is_ptr = struct_type.pointer_level > 0
            struct_name = struct_type.token.value if is_ptr else struct_type.value
            if struct_name not in self.struct_table: self.error("E006", f"Unknown struct type '{struct_name}'", node)
            field_name = node.right.value
            if field_name not in self.struct_table[struct_name]['fields']: self.error("E007",
                                                                                      f"Struct '{struct_name}' has no field '{field_name}'",
                                                                                      node)
            return self.struct_table[struct_name]['fields'][field_name]['type']
        return Type(Token(TokenType.KW_INT, 'int'))

    def generate(self, tree):
        self.visit(tree)
        full_asm = []
        if self.data_section: full_asm.append('section .data'); full_asm.extend(self.data_section)
        full_asm.append('section .bss')
        full_asm.append('  print_buf resb 32\n')
        full_asm.append('section .text')
        full_asm.append('global _start')
        self._add_print_function()
        self._add_putchar_function()
        self._add_getchar_function()
        full_asm.extend(self.assembly_code)
        return '\n'.join(full_asm)

    def visit_Program(self, node):
        for decl in node.declarations:
            if isinstance(decl, StructDef): self.visit(decl)
        for decl in node.declarations:
            if not isinstance(decl, StructDef): self.visit(decl)

    def visit_StructDef(self, node):
        offset = 0
        fields = {}
        for field in node.fields:
            field_name = field.var_node.value
            field_type = field.type_node
            size = self._get_type_size(field_type)
            fields[field_name] = {'type': field_type, 'offset': offset}
            offset += size
        self.struct_table[node.name] = {'fields': fields, 'size': offset}

    def visit_FunctionDecl(self, node):
        self.current_function = node.func_name
        func_label = '_start' if node.func_name == 'main' else node.func_name
        self.assembly_code.append(f'{func_label}:')
        self.assembly_code.append('  push rbp')
        self.assembly_code.append('  mov rbp, rsp')
        local_vars_space = 256
        self.assembly_code.append(f'  sub rsp, {local_vars_space}')
        self.symbol_table = {}
        self.stack_index = 0
        arg_registers = ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9']
        for i, param in enumerate(node.params):
            param_name = param.var_node.value
            self.stack_index -= 8
            self.symbol_table[param_name] = {'type': param.type_node, 'offset': self.stack_index}
            self.assembly_code.append(f'  mov [rbp{self.stack_index}], {arg_registers[i]}')
        self.visit(node.body)
        if not node.body.children or not isinstance(node.body.children[-1], Return):
            self.assembly_code.append('  pop rax')
        self.assembly_code.append(f'.L_ret_{node.func_name}:')
        self.assembly_code.append('  mov rsp, rbp')
        self.assembly_code.append('  pop rbp')
        if node.func_name == 'main':
            self.assembly_code.append('  mov rdi, rax')
            self.assembly_code.append('  mov rax, 60')
            self.assembly_code.append('  syscall')
        else:
            self.assembly_code.append('  ret')

    def visit_Block(self, node):
        old_symbol_table = self.symbol_table.copy()
        old_stack_index = self.stack_index
        for child in node.children:
            self.visit(child)
            if isinstance(child, FunctionCall):
                self.assembly_code.append('  add rsp, 8 ; Discard unused function call return value')
        self.symbol_table = old_symbol_table
        self.stack_index = old_stack_index

    def visit_VarDecl(self, node):
        var_name = node.var_node.value
        if var_name in self.symbol_table: self.error("E008", f"Variable '{var_name}' already declared.", node)
        var_type = node.type_node
        type_size = self._get_type_size(var_type)

        # --- FIX: Always allocate 8 bytes for local variables to ensure stack alignment ---
        alloc_size = 8
        self.stack_index -= alloc_size
        self.symbol_table[var_name] = {'type': var_type, 'offset': self.stack_index}

        if node.assign_node:
            self.visit(node.assign_node)
            right_type = self._get_node_type(node.assign_node)
            if right_type.value not in ('int', 'char') and right_type.pointer_level == 0:
                self.assembly_code.append('  pop rsi');
                self.assembly_code.append(f'  lea rdi, [rbp{self.stack_index}]')
                self.assembly_code.append(f'  mov rcx, {type_size}'); # Use actual type_size for movsb
                self.assembly_code.append('  rep movsb')
            else:
                self.assembly_code.append('  pop rax');
                # Use the actual type size to determine the register (al vs rax)
                if type_size == 1:
                    self.assembly_code.append(f"  mov [rbp{self.stack_index}], al")
                else:
                    self.assembly_code.append(f"  mov [rbp{self.stack_index}], rax")

    def visit_Assign(self, node):
        left_type = self._get_node_type(node.left)
        right_type = self._get_node_type(node.right)
        if left_type.value not in ('int', 'char') and left_type.pointer_level == 0:
            if repr(left_type) != repr(right_type): self.error("E009", "Type mismatch in struct assignment", node)
            self.visit(node.right, is_lvalue=True)
            self.visit(node.left, is_lvalue=True)
            self.assembly_code.append('  pop rdi')
            self.assembly_code.append('  pop rsi')
            self.assembly_code.append(f'  mov rcx, {self.struct_table[left_type.value]["size"]}')
            self.assembly_code.append('  rep movsb')
        else:
            self.visit(node.right)
            if isinstance(node.left, MemberAccess):
                self.visit(node.left, is_lvalue=True)
                self.assembly_code.append('  pop rbx')
                self.assembly_code.append('  pop rax')
                if self._get_type_size(left_type) == 1:
                    self.assembly_code.append('  mov [rbx], al')
                else:
                    self.assembly_code.append('  mov [rbx], rax')
            elif isinstance(node.left, UnaryOp) and node.left.op.type == TokenType.KW_DEREF:
                self.visit(node.left.expr)
                self.assembly_code.append('  pop rbx')
                self.assembly_code.append('  pop rax')
                if self._get_type_size(left_type) == 1:
                     self.assembly_code.append('  mov [rbx], al')
                else:
                     self.assembly_code.append('  mov [rbx], rax')
            elif isinstance(node.left, Var):
                var_name = node.left.value
                if var_name not in self.symbol_table: self.error("E004", f"Undeclared variable '{var_name}'", node.left)
                offset = self.symbol_table[var_name]['offset']
                self.assembly_code.append('  pop rax')
                if self._get_type_size(left_type) == 1:
                    self.assembly_code.append(f'  mov [rbp{offset}], al')
                else:
                    self.assembly_code.append(f'  mov [rbp{offset}], rax')
            else:
                self.error("E010", "Invalid left-hand side in assignment", node)

    def visit_MemberAccess(self, node, is_lvalue=False):
        struct_type = self._get_node_type(node.left)
        is_ptr = struct_type.pointer_level > 0
        struct_name = struct_type.token.value if is_ptr else struct_type.value
        field_name = node.right.value
        field_info = self.struct_table[struct_name]['fields'][field_name]
        offset = field_info['offset']
        self.visit(node.left, is_lvalue=not is_ptr)
        self.assembly_code.append('  pop rax')
        self.assembly_code.append(f'  add rax, {offset}')
        if is_lvalue:
            self.assembly_code.append('  push rax')
        else:
            field_type = field_info['type']
            if self._get_type_size(field_type) == 1:
                self.assembly_code.append('  movzx rax, byte [rax]')
            else:
                self.assembly_code.append('  mov rax, [rax]')
            self.assembly_code.append('  push rax')

    def visit_Var(self, node, is_lvalue=False):
        var_name = node.value
        if var_name not in self.symbol_table: self.error("E004", f"Undeclared variable '{var_name}'", node)
        offset = self.symbol_table[var_name]['offset']
        var_type = self.symbol_table[var_name]['type']
        is_struct_like = var_type.value not in ('int', 'char') and var_type.pointer_level == 0
        if is_lvalue or is_struct_like:
            self.assembly_code.append(f'  lea rax, [rbp{offset}]')
        else:
            self.assembly_code.append(f'  mov rax, [rbp{offset}]')
        self.assembly_code.append('  push rax')

    def visit_FunctionCall(self, node):
        arg_registers = ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9']
        if len(node.args) > len(arg_registers): self.error("E012", "Too many arguments in function call", node)
        # We push arguments in reverse for the stack, but for registers it's easier to just load them directly.
        # Let's evaluate them in order and pop into registers.
        for i, arg in enumerate(reversed(node.args)):
             self.visit(arg)

        for i in range(len(node.args)):
             self.assembly_code.append(f'  pop {arg_registers[i]}')

        func_name = node.name_node.value
        # Special handling for built-in functions
        if func_name in ('print', 'putchar', 'getchar'):
             self.assembly_code.append(f'  call {func_name}')
        else:
             self.assembly_code.append(f'  call {func_name}')
        self.assembly_code.append('  push rax')

    def visit_CharLiteral(self, node):
        self.assembly_code.append(f'  push {node.value}')

    def visit_StringLiteral(self, node):
        label = f'L_str_{self.string_literal_counter}'
        self.string_literal_counter += 1
        # Add string to .data section. db is 'define byte'. 0 is the null terminator.
        self.data_section.append(f'  {label} db "{node.value}", 0')
        # Push the address of the string onto the stack
        self.assembly_code.append(f'  push {label}')

    def _add_putchar_function(self):
        self.assembly_code.extend([
            'putchar:',
            '  push rbp',
            '  mov rbp, rsp',
            '  sub rsp, 8',  # Make space for the character
            '  mov [rbp-8], dil ; Save argument (the character, just the low byte)',
            '  mov rax, 1 ; syscall write',
            '  mov rdi, 1 ; stdout',
            '  lea rsi, [rbp-8] ; address of the character on the stack',
            '  mov rdx, 1 ; length is 1 byte',
            '  syscall',
            '  mov rsp, rbp',  # Clean up stack
            '  pop rbp',
            '  ret', ''
        ])

    def _add_getchar_function(self):
        self.assembly_code.extend([
            'getchar:',
            '  push rbp',
            '  mov rbp, rsp',
            '  sub rsp, 8 ; Make space for one character',
            '  mov rax, 0 ; syscall read',
            '  mov rdi, 0 ; stdin',
            '  lea rsi, [rbp-8] ; buffer to read into',
            '  mov rdx, 1 ; read 1 byte',
            '  syscall',
            '  movzx rax, byte [rbp-8] ; Move the character into RAX, zero-extending',
            '  mov rsp, rbp',
            '  pop rbp',
            '  ret', ''
        ])

    def visit_Return(self, node):
        self.visit(node.value)
        self.assembly_code.append('  pop rax')
        self.assembly_code.append(f'  jmp .L_ret_{self.current_function}')

    def visit_UnaryOp(self, node):
        op_type = node.op.type
        if op_type == TokenType.KW_ADDR:
            if not isinstance(node.expr, (Var, MemberAccess)):
                self.error("E011", "'addr' can only be used on variables or struct members", node)
            self.visit(node.expr, is_lvalue=True)
            return
        if op_type == TokenType.KW_DEREF:
            self.visit(node.expr)
            self.assembly_code.append('  pop rax')
            ptr_type = self._get_node_type(node.expr)
            if ptr_type.pointer_level == 1 and ptr_type.value == 'char':
                self.assembly_code.append('  movzx rax, byte [rax]')
            else:
                self.assembly_code.append('  mov rax, [rax]')
            self.assembly_code.append('  push rax')
            return

        self.visit(node.expr)
        self.assembly_code.append('  pop rax')
        if op_type == TokenType.KW_BNOT:
            self.assembly_code.append('  not rax')
        elif op_type == TokenType.KW_NOT:
            self.assembly_code.append('  cmp rax, 0')
            self.assembly_code.append('  sete al')
            self.assembly_code.append('  movzx rax, al')
        elif op_type == TokenType.KW_NBNOT:
            pass
        elif op_type == TokenType.KW_NNOT:
            self.assembly_code.append('  cmp rax, 0')
            self.assembly_code.append('  setne al')
            self.assembly_code.append('  movzx rax, al')
        self.assembly_code.append('  push rax')

    def visit_BinOp(self, node):
        op_type = node.op.type
        if op_type in (TokenType.KW_AND, TokenType.KW_NAND):
            label_num = self._new_label()
            end_label = f"L_logic_end_{label_num}"
            self.visit(node.left)
            self.assembly_code.append('  pop rax')
            self.assembly_code.append('  cmp rax, 0')
            self.assembly_code.append(f'  je L_logic_false_{label_num}')
            self.visit(node.right)
            self.assembly_code.append('  pop rax')
            self.assembly_code.append('  cmp rax, 0')
            self.assembly_code.append(f'  je L_logic_false_{label_num}')
            self.assembly_code.append(f'  mov rax, {0 if op_type == TokenType.KW_NAND else 1}')
            self.assembly_code.append(f'  jmp {end_label}')
            self.assembly_code.append(f'L_logic_false_{label_num}:')
            self.assembly_code.append(f'  mov rax, {1 if op_type == TokenType.KW_NAND else 0}')
            self.assembly_code.append(f'{end_label}:')
            self.assembly_code.append('  push rax')
            return
        if op_type in (TokenType.KW_OR, TokenType.KW_NOR):
            label_num = self._new_label()
            end_label = f"L_logic_end_{label_num}"
            self.visit(node.left)
            self.assembly_code.append('  pop rax')
            self.assembly_code.append('  cmp rax, 0')
            self.assembly_code.append(f'  jne L_logic_true_{label_num}')
            self.visit(node.right)
            self.assembly_code.append('  pop rax')
            self.assembly_code.append('  cmp rax, 0')
            self.assembly_code.append(f'  jne L_logic_true_{label_num}')
            self.assembly_code.append(f'  mov rax, {1 if op_type == TokenType.KW_NOR else 0}')
            self.assembly_code.append(f'  jmp {end_label}')
            self.assembly_code.append(f'L_logic_true_{label_num}:')
            self.assembly_code.append(f'  mov rax, {0 if op_type == TokenType.KW_NOR else 1}')
            self.assembly_code.append(f'{end_label}:')
            self.assembly_code.append('  push rax')
            return
        if op_type in (TokenType.KW_XOR, TokenType.KW_XNOR):
            self.visit(node.left)
            self.assembly_code.append('  pop rax')
            self.assembly_code.append('  cmp rax, 0')
            self.assembly_code.append('  setne cl')
            self.visit(node.right)
            self.assembly_code.append('  pop rax')
            self.assembly_code.append('  cmp rax, 0')
            self.assembly_code.append('  setne dl')
            self.assembly_code.append('  xor cl, dl')
            if op_type == TokenType.KW_XNOR: self.assembly_code.append('  xor cl, 1')
            self.assembly_code.append('  movzx rax, cl')
            self.assembly_code.append('  push rax')
            return
        if op_type == TokenType.TYPE_EQUAL:
            left_type = self._get_node_type(node.left)
            right_type = self._get_node_type(node.right)
            result = 1 if repr(left_type) == repr(right_type) else 0
            self.assembly_code.append(f'  ; Compile-time type check: {left_type} === {right_type}')
            self.assembly_code.append(f'  push {result}')
            return

        left_type = self._get_node_type(node.left)
        right_type = self._get_node_type(node.right)

        self.visit(node.left)
        self.visit(node.right)
        self.assembly_code.append('  ; Binary Operation')
        self.assembly_code.append('  pop rbx')
        self.assembly_code.append('  pop rax')

        if left_type.pointer_level > 0 and right_type.pointer_level == 0:  # ptr + int
            size = self._get_type_size(Type(left_type.token, left_type.pointer_level - 1))
            if size > 1: self.assembly_code.append(f'  imul rbx, {size}')
        elif right_type.pointer_level > 0 and left_type.pointer_level == 0:  # int + ptr
            size = self._get_type_size(Type(right_type.token, right_type.pointer_level - 1))
            if size > 1: self.assembly_code.append(f'  imul rax, {size}')

        if op_type == TokenType.PLUS:
            self.assembly_code.append('  add rax, rbx')
        elif op_type == TokenType.MINUS:
            self.assembly_code.append('  sub rax, rbx')
        elif op_type == TokenType.MULTIPLY:
            self.assembly_code.append('  imul rax, rbx')
        elif op_type == TokenType.DIVIDE:
            self.assembly_code.append('  cqo'); self.assembly_code.append('  idiv rbx')
        elif op_type in (TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL, TokenType.GREATER,
                         TokenType.GREATER_EQUAL):
            self.assembly_code.append('  cmp rax, rbx')
            if op_type == TokenType.EQUAL:
                self.assembly_code.append('  sete al')
            elif op_type == TokenType.NOT_EQUAL:
                self.assembly_code.append('  setne al')
            elif op_type == TokenType.LESS:
                self.assembly_code.append('  setl al')
            elif op_type == TokenType.LESS_EQUAL:
                self.assembly_code.append('  setle al')
            elif op_type == TokenType.GREATER:
                self.assembly_code.append('  setg al')
            elif op_type == TokenType.GREATER_EQUAL:
                self.assembly_code.append('  setge al')
            self.assembly_code.append('  movzx rax, al')
        elif op_type in (TokenType.KW_BAND, TokenType.KW_NBAND):
            self.assembly_code.append('  and rax, rbx')
        elif op_type in (TokenType.KW_BOR, TokenType.KW_NBOR):
            self.assembly_code.append('  or rax, rbx')
        elif op_type in (TokenType.KW_BXOR, TokenType.KW_NBXOR):
            self.assembly_code.append('  xor rax, rbx')
        if op_type in (TokenType.KW_NBAND, TokenType.KW_NBOR, TokenType.KW_NBXOR):
            self.assembly_code.append('  not rax')
        self.assembly_code.append('  push rax')

    def visit_IfExpr(self, node):
        label_num = self._new_label()
        else_label = f"L_else_{label_num}"
        endif_label = f"L_endif_{label_num}"
        self.visit(node.condition)
        self.assembly_code.append('  pop rax')
        self.assembly_code.append('  cmp rax, 0')
        self.assembly_code.append(f'  je {else_label}')
        self.visit(node.if_block)
        self.assembly_code.append(f'  jmp {endif_label}')
        self.assembly_code.append(f'{else_label}:')
        self.visit(node.else_block)
        self.assembly_code.append(f'{endif_label}:')

    def visit_WhileStmt(self, node):
        label_num = self._new_label()
        start_label = f"L_while_start_{label_num}"
        end_label = f"L_while_end_{label_num}"
        self.loop_labels_stack.append((start_label, end_label))
        self.assembly_code.append(f'{start_label}:')
        self.visit(node.condition)
        self.assembly_code.append('  pop rax')
        self.assembly_code.append('  cmp rax, 0')
        self.assembly_code.append(f'  je {end_label}')
        self.visit(node.body)
        self.assembly_code.append(f'  jmp {start_label}')
        self.assembly_code.append(f'{end_label}:')
        self.loop_labels_stack.pop()

    def visit_LoopStmt(self, node):
        label_num = self._new_label()
        start_label = f"L_loop_start_{label_num}"
        end_label = f"L_loop_end_{label_num}"
        self.loop_labels_stack.append((start_label, end_label))
        self.assembly_code.append(f'{start_label}:')
        self.visit(node.body)
        self.assembly_code.append(f'  jmp {start_label}')
        self.assembly_code.append(f'{end_label}:')
        self.loop_labels_stack.pop()

    def visit_ForStmt(self, node):
        old_symbol_table = self.symbol_table.copy()
        label_num = self._new_label()
        start_label = f"L_for_start_{label_num}"
        continue_label = f"L_for_continue_{label_num}"
        end_label = f"L_for_end_{label_num}"
        if node.init: self.visit(node.init)
        self.assembly_code.append(f'{start_label}:')
        if node.condition:
            self.visit(node.condition)
            self.assembly_code.append('  pop rax')
            self.assembly_code.append('  cmp rax, 0')
            self.assembly_code.append(f'  je {end_label}')
        self.loop_labels_stack.append((continue_label, end_label))
        self.visit(node.body)
        self.loop_labels_stack.pop()
        self.assembly_code.append(f'{continue_label}:')
        if node.increment: self.visit(node.increment)
        self.assembly_code.append(f'  jmp {start_label}')
        self.assembly_code.append(f'{end_label}:')
        self.symbol_table = old_symbol_table

    def visit_BreakStmt(self, node):
        if not self.loop_labels_stack: self.error("E013", "'break' outside of a loop", node)
        _, end_label = self.loop_labels_stack[-1]
        self.assembly_code.append(f'  jmp {end_label}')

    def visit_ContinueStmt(self, node):
        if not self.loop_labels_stack: self.error("E014", "'continue' outside of a loop", node)
        continue_label, _ = self.loop_labels_stack[-1]
        self.assembly_code.append(f'  jmp {continue_label}')

    def visit_Num(self, node):
        self.assembly_code.append(f'  ; Pushing number {node.value}')
        self.assembly_code.append(f'  push {node.value}')

    def visit_ConstDecl(self, node):
        pass

    def _add_print_function(self):
        self.assembly_code.extend([
            'print_int:', '  mov rax, rdi', '  lea rdi, [rel print_buf + 31]', '  mov byte [rdi], 10', '  mov r10, 10',
            '  mov r9, 1',
            'print_int_loop:', '  xor rdx, rdx', '  div r10', '  add dl, \'0\'', '  dec rdi', '  mov [rdi], dl',
            '  inc r9', '  test rax, rax', '  jnz print_int_loop',
            'print_int_write:', '  mov rax, 1', '  mov rsi, rdi', '  mov rdx, r9', '  mov rdi, 1', '  syscall', '  ret',
            ''])

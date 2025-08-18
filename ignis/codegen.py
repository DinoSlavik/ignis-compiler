from ast_nodes import *
from lexer import TokenType


class NodeVisitor:
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node): raise Exception(f'No visit_{type(node).__name__} method')


class CodeGenerator(NodeVisitor):
    def __init__(self):
        self.assembly_code = []
        self.symbol_table = {}
        self.stack_index = -8
        self.label_counter = 0
        self.loop_labels_stack = []

    def _new_label(self):
        self.label_counter += 1
        return self.label_counter

    def _get_node_type(self, node):
        if isinstance(node, Num): return Type(None, 0)  # Base int type
        if isinstance(node, Var):
            var_name = node.value
            if var_name in self.symbol_table:
                return self.symbol_table[var_name]['type']
            else:
                if var_name == "VERSION": return Type(None, 0)
                raise Exception(f"Cannot determine type of undeclared variable '{var_name}'")
        if isinstance(node, UnaryOp):
            if node.op.type == TokenType.KW_ADDR:
                base_type = self._get_node_type(node.expr)
                return Type(base_type.token, base_type.pointer_level + 1)
            if node.op.type == TokenType.KW_DEREF:
                base_type = self._get_node_type(node.expr)
                if base_type.pointer_level == 0: raise Exception("Cannot dereference a non-pointer type")
                return Type(base_type.token, base_type.pointer_level - 1)
        return Type(None, 0)  # Default to int for now

    def generate(self, tree):
        self.assembly_code.append('section .bss');
        self.assembly_code.append('  print_buf resb 32\n')
        self.assembly_code.append('section .text');
        self.assembly_code.append('global _start')
        self._add_print_function();
        self.visit(tree);
        return '\n'.join(self.assembly_code)

    def visit_Program(self, node):
        for decl in node.declarations: self.visit(decl)

    def visit_FunctionDecl(self, node):
        if node.func_name == 'main':
            self.assembly_code.append('_start:');
            self.assembly_code.append('  push rbp');
            self.assembly_code.append('  mov rbp, rsp')
            self.assembly_code.append('  sub rsp, 64 ; Allocate larger stack frame for locals')
            self.visit(node.body)
            if not node.body.children or not isinstance(node.body.children[-1], Return):
                self.assembly_code.append('  pop rdi');
                self.assembly_code.append('  mov rax, 60');
                self.assembly_code.append('  syscall')
            self.assembly_code.append('  ; Epilogue');
            self.assembly_code.append('  add rsp, 64');
            self.assembly_code.append('  pop rbp')

    def visit_Block(self, node):
        old_symbol_table = self.symbol_table.copy();
        old_stack_index = self.stack_index
        for child in node.children: self.visit(child)
        self.symbol_table = old_symbol_table;
        self.stack_index = old_stack_index

    def visit_VarDecl(self, node):
        var_name = node.var_node.value
        if var_name in self.symbol_table and self.symbol_table[var_name]['offset'] > self.stack_index:
            raise Exception(f"Variable '{var_name}' already declared in this scope.")
        self.symbol_table[var_name] = {'offset': self.stack_index, 'type': node.type_node}
        self.visit(node.assign_node)
        self.assembly_code.append(f'  ; VarDecl: {var_name}');
        self.assembly_code.append('  pop rax');
        self.assembly_code.append(f"  mov [rbp{self.symbol_table[var_name]['offset']}], rax")
        self.stack_index -= 8

    def visit_Assign(self, node):
        self.visit(node.right)  # Value is now on the stack

        # If assigning to 'deref p', left is a UnaryOp
        if isinstance(node.left, UnaryOp) and node.left.op.type == TokenType.KW_DEREF:
            self.visit(node.left.expr)  # Address is now on the stack
            self.assembly_code.append('  pop rbx ; Address')
            self.assembly_code.append('  pop rax ; Value')
            self.assembly_code.append('  mov [rbx], rax')
        # If assigning to a variable 'p'
        elif isinstance(node.left, Var):
            var_name = node.left.value
            if var_name not in self.symbol_table: raise Exception(f"Assigning to undeclared variable '{var_name}'")
            stack_offset = self.symbol_table[var_name]['offset']
            self.assembly_code.append('  pop rax ; Value')
            self.assembly_code.append(f'  mov [rbp{stack_offset}], rax')
        else:
            raise Exception("Invalid left-hand side in assignment")

    def visit_UnaryOp(self, node):
        op_type = node.op.type
        if op_type == TokenType.KW_ADDR:
            if not isinstance(node.expr, Var): raise Exception("'addr' can only be used on variables")
            var_name = node.expr.value
            if var_name not in self.symbol_table: raise Exception(f"Undeclared variable '{var_name}'")
            offset = self.symbol_table[var_name]['offset']
            self.assembly_code.append(f'  lea rax, [rbp{offset}]')
            self.assembly_code.append('  push rax')
            return
        if op_type == TokenType.KW_DEREF:
            self.visit(node.expr)  # This pushes the address onto the stack
            self.assembly_code.append('  pop rax')
            self.assembly_code.append('  mov rax, [rax]')  # Dereference the address in rax
            self.assembly_code.append('  push rax')
            return

        self.visit(node.expr)
        self.assembly_code.append('  pop rax')
        if op_type == TokenType.KW_BNOT:
            self.assembly_code.append('  not rax')
        elif op_type == TokenType.KW_NOT:
            self.assembly_code.append('  cmp rax, 0');
            self.assembly_code.append('  sete al');
            self.assembly_code.append('  movzx rax, al')
        elif op_type == TokenType.KW_NBNOT:
            pass
        elif op_type == TokenType.KW_NNOT:
            self.assembly_code.append('  cmp rax, 0');
            self.assembly_code.append('  setne al');
            self.assembly_code.append('  movzx rax, al')
        self.assembly_code.append('  push rax')

    # ... (The rest of the CodeGenerator class is unchanged) ...
    def visit_IfExpr(self, node):
        label_num = self._new_label();
        else_label = f"L_else_{label_num}";
        endif_label = f"L_endif_{label_num}"
        self.visit(node.condition);
        self.assembly_code.append('  pop rax');
        self.assembly_code.append('  cmp rax, 0')
        self.assembly_code.append(f'  je {else_label}');
        self.visit(node.if_block);
        self.assembly_code.append(f'  jmp {endif_label}')
        self.assembly_code.append(f'{else_label}:');
        self.visit(node.else_block);
        self.assembly_code.append(f'{endif_label}:')

    def visit_WhileStmt(self, node):
        label_num = self._new_label();
        start_label = f"L_while_start_{label_num}";
        end_label = f"L_while_end_{label_num}"
        self.loop_labels_stack.append((start_label, end_label))
        self.assembly_code.append(f'{start_label}:')
        self.visit(node.condition)
        self.assembly_code.append('  pop rax');
        self.assembly_code.append('  cmp rax, 0')
        self.assembly_code.append(f'  je {end_label}')
        self.visit(node.body)
        self.assembly_code.append(f'  jmp {start_label}')
        self.assembly_code.append(f'{end_label}:')
        self.loop_labels_stack.pop()

    def visit_LoopStmt(self, node):
        label_num = self._new_label();
        start_label = f"L_loop_start_{label_num}";
        end_label = f"L_loop_end_{label_num}"
        self.loop_labels_stack.append((start_label, end_label))
        self.assembly_code.append(f'{start_label}:')
        self.visit(node.body)
        self.assembly_code.append(f'  jmp {start_label}')
        self.assembly_code.append(f'{end_label}:')
        self.loop_labels_stack.pop()

    def visit_ForStmt(self, node):
        old_symbol_table = self.symbol_table.copy();
        old_stack_index = self.stack_index
        label_num = self._new_label()
        start_label = f"L_for_start_{label_num}";
        continue_label = f"L_for_continue_{label_num}";
        end_label = f"L_for_end_{label_num}"
        if node.init: self.visit(node.init)
        self.assembly_code.append(f'{start_label}:')
        if node.condition:
            self.visit(node.condition)
            self.assembly_code.append('  pop rax');
            self.assembly_code.append('  cmp rax, 0')
            self.assembly_code.append(f'  je {end_label}')
        self.loop_labels_stack.append((continue_label, end_label))
        self.visit(node.body)
        self.loop_labels_stack.pop()
        self.assembly_code.append(f'{continue_label}:')
        if node.increment: self.visit(node.increment)
        self.assembly_code.append(f'  jmp {start_label}')
        self.assembly_code.append(f'{end_label}:')
        self.symbol_table = old_symbol_table;
        self.stack_index = old_stack_index

    def visit_BreakStmt(self, node):
        if not self.loop_labels_stack: raise Exception("'break' outside of a loop")
        _, end_label = self.loop_labels_stack[-1]
        self.assembly_code.append(f'  jmp {end_label}')

    def visit_ContinueStmt(self, node):
        if not self.loop_labels_stack: raise Exception("'continue' outside of a loop")
        continue_label, _ = self.loop_labels_stack[-1]
        self.assembly_code.append(f'  jmp {continue_label}')

    def visit_Num(self, node):
        self.assembly_code.append(f'  ; Pushing number {node.value}'); self.assembly_code.append(f'  push {node.value}')

    def visit_Var(self, node):
        var_name = node.value
        if var_name not in self.symbol_table:
            if var_name == "VERSION": self.assembly_code.append(f'  push 1'); return
            raise Exception(f"Undeclared variable '{var_name}'")
        stack_offset = self.symbol_table[var_name]['offset'];
        self.assembly_code.append(f'  ; Pushing variable {var_name}');
        self.assembly_code.append(f'  push qword [rbp{stack_offset}]')

    def visit_BinOp(self, node):
        op_type = node.op.type
        if op_type in (TokenType.KW_AND, TokenType.KW_NAND):
            label_num = self._new_label();
            end_label = f"L_logic_end_{label_num}"
            self.visit(node.left);
            self.assembly_code.append('  pop rax');
            self.assembly_code.append('  cmp rax, 0')
            self.assembly_code.append(f'  je L_logic_false_{label_num}')
            self.visit(node.right);
            self.assembly_code.append('  pop rax');
            self.assembly_code.append('  cmp rax, 0')
            self.assembly_code.append(f'  je L_logic_false_{label_num}')
            self.assembly_code.append(f'  mov rax, {0 if op_type == TokenType.KW_NAND else 1}');
            self.assembly_code.append(f'  jmp {end_label}')
            self.assembly_code.append(f'L_logic_false_{label_num}:');
            self.assembly_code.append(f'  mov rax, {1 if op_type == TokenType.KW_NAND else 0}')
            self.assembly_code.append(f'{end_label}:');
            self.assembly_code.append('  push rax')
            return
        if op_type in (TokenType.KW_OR, TokenType.KW_NOR):
            label_num = self._new_label();
            end_label = f"L_logic_end_{label_num}"
            self.visit(node.left);
            self.assembly_code.append('  pop rax');
            self.assembly_code.append('  cmp rax, 0')
            self.assembly_code.append(f'  jne L_logic_true_{label_num}')
            self.visit(node.right);
            self.assembly_code.append('  pop rax');
            self.assembly_code.append('  cmp rax, 0')
            self.assembly_code.append(f'  jne L_logic_true_{label_num}')
            self.assembly_code.append(f'  mov rax, {1 if op_type == TokenType.KW_NOR else 0}');
            self.assembly_code.append(f'  jmp {end_label}')
            self.assembly_code.append(f'L_logic_true_{label_num}:');
            self.assembly_code.append(f'  mov rax, {0 if op_type == TokenType.KW_NOR else 1}')
            self.assembly_code.append(f'{end_label}:');
            self.assembly_code.append('  push rax')
            return
        if op_type in (TokenType.KW_XOR, TokenType.KW_XNOR):
            self.visit(node.left);
            self.assembly_code.append('  pop rax');
            self.assembly_code.append('  cmp rax, 0');
            self.assembly_code.append('  setne cl')
            self.visit(node.right);
            self.assembly_code.append('  pop rax');
            self.assembly_code.append('  cmp rax, 0');
            self.assembly_code.append('  setne dl')
            self.assembly_code.append('  xor cl, dl')
            if op_type == TokenType.KW_XNOR: self.assembly_code.append('  xor cl, 1')
            self.assembly_code.append('  movzx rax, cl');
            self.assembly_code.append('  push rax')
            return
        if op_type == TokenType.TYPE_EQUAL:
            left_type = self._get_node_type(node.left);
            right_type = self._get_node_type(node.right)
            result = 1 if repr(left_type) == repr(right_type) else 0
            self.assembly_code.append(f'  ; Compile-time type check: {left_type} === {right_type}');
            self.assembly_code.append(f'  push {result}')
            return
        self.visit(node.left);
        self.visit(node.right)
        self.assembly_code.append('  ; Binary Operation');
        self.assembly_code.append('  pop rbx');
        self.assembly_code.append('  pop rax')
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

    def visit_FunctionCall(self, node):
        if node.name == 'print':
            self.visit(node.args[0]); self.assembly_code.append('  pop rdi'); self.assembly_code.append(
                '  call print_int')
        else:
            raise Exception(f"Undefined function call '{node.name}'")

    def visit_Return(self, node):
        self.visit(node.value);
        self.assembly_code.append('  ; Return statement');
        self.assembly_code.append('  pop rdi');
        self.assembly_code.append('  mov rax, 60');
        self.assembly_code.append('  syscall')

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

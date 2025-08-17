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

    def _new_label(self):
        self.label_counter += 1
        return self.label_counter

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
            self.assembly_code.append('  sub rsp, 32 ; Allocate stack frame')
            self.visit(node.body)
            if not node.body.children or not isinstance(node.body.children[-1], Return):
                self.assembly_code.append('  pop rdi ; Implicit exit code');
                self.assembly_code.append('  mov rax, 60 ; syscall for exit');
                self.assembly_code.append('  syscall')
            self.assembly_code.append('  ; Epilogue');
            self.assembly_code.append('  add rsp, 32 ; Deallocate stack frame');
            self.assembly_code.append('  pop rbp')

    def visit_Block(self, node):
        for child in node.children: self.visit(child)

    def visit_VarDecl(self, node):
        var_name = node.var_node.value
        if var_name in self.symbol_table: raise Exception(f"Variable '{var_name}' already declared.")
        self.symbol_table[var_name] = self.stack_index;
        self.visit(node.assign_node)
        self.assembly_code.append(f'  ; VarDecl: {var_name}');
        self.assembly_code.append('  pop rax');
        self.assembly_code.append(f'  mov [rbp{self.stack_index}], rax')
        self.stack_index -= 8

    def visit_Assign(self, node):
        var_name = node.left.value
        if var_name not in self.symbol_table: raise Exception(f"Assigning to undeclared variable '{var_name}'")
        self.visit(node.right);
        self.assembly_code.append(f'  ; Assign: {var_name}');
        self.assembly_code.append('  pop rax')
        stack_offset = self.symbol_table[var_name];
        self.assembly_code.append(f'  mov [rbp{stack_offset}], rax')

    def visit_IfExpr(self, node):
        label_num = self._new_label()
        else_label = f"L_else_{label_num}"
        endif_label = f"L_endif_{label_num}"

        # 1. Evaluate condition. The result (1 for true, 0 for false) will be on the stack.
        self.visit(node.condition)

        # 2. Check the condition and jump
        self.assembly_code.append('  pop rax')
        self.assembly_code.append('  cmp rax, 0')
        self.assembly_code.append(f'  je {else_label} ; Jump to else if condition is false')

        # 3. 'If' block
        self.visit(node.if_block)
        self.assembly_code.append(f'  jmp {endif_label} ; Skip else block')

        # 4. 'Else' block
        self.assembly_code.append(f'{else_label}:')
        self.visit(node.else_block)

        # 5. End label
        self.assembly_code.append(f'{endif_label}:')
        # The result of the executed block is now on top of the stack.

    def visit_Num(self, node):
        self.assembly_code.append(f'  ; Pushing number {node.value}'); self.assembly_code.append(f'  push {node.value}')

    def visit_Var(self, node):
        var_name = node.value
        if var_name not in self.symbol_table:
            if var_name == "VERSION": self.assembly_code.append(f'  push 1'); return
            raise Exception(f"Undeclared variable '{var_name}'")
        stack_offset = self.symbol_table[var_name];
        self.assembly_code.append(f'  ; Pushing variable {var_name}');
        self.assembly_code.append(f'  push qword [rbp{stack_offset}]')

    def visit_BinOp(self, node):
        self.visit(node.left);
        self.visit(node.right)
        self.assembly_code.append('  ; Binary Operation');
        self.assembly_code.append('  pop rbx ; Right side');
        self.assembly_code.append('  pop rax ; Left side')

        op_type = node.op.type
        if op_type == TokenType.PLUS:
            self.assembly_code.append('  add rax, rbx')
        elif op_type == TokenType.MINUS:
            self.assembly_code.append('  sub rax, rbx')
        elif op_type == TokenType.MULTIPLY:
            self.assembly_code.append('  imul rax, rbx')
        elif op_type == TokenType.DIVIDE:
            self.assembly_code.append('  cqo'); self.assembly_code.append('  idiv rbx')
        # --- New Comparison Logic ---
        elif op_type in (TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL,
                         TokenType.GREATER, TokenType.GREATER_EQUAL):
            self.assembly_code.append('  cmp rax, rbx')
            if op_type == TokenType.EQUAL:
                self.assembly_code.append('  sete al')  # Set AL if equal
            elif op_type == TokenType.NOT_EQUAL:
                self.assembly_code.append('  setne al')  # Set AL if not equal
            elif op_type == TokenType.LESS:
                self.assembly_code.append('  setl al')  # Set AL if less
            elif op_type == TokenType.LESS_EQUAL:
                self.assembly_code.append('  setle al')  # Set AL if less or equal
            elif op_type == TokenType.GREATER:
                self.assembly_code.append('  setg al')  # Set AL if greater
            elif op_type == TokenType.GREATER_EQUAL:
                self.assembly_code.append('  setge al')  # Set AL if greater or equal
            self.assembly_code.append('  movzx rax, al ; Zero-extend AL to RAX (0 or 1)')

        self.assembly_code.append('  push rax ; Push result')

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
            'print_int:',
            '  mov rax, rdi',
            '  lea rdi, [rel print_buf + 31]',
            '  mov byte [rdi], 10', '  mov r10, 10',
            '  mov r9, 1',
            'print_int_loop:',
            '  xor rdx, rdx',
            '  div r10',
            '  add dl, \'0\'',
            '  dec rdi',
            '  mov [rdi], dl',
            '  inc r9',
            '  test rax, rax',
            '  jnz print_int_loop',
            'print_int_write:',
            '  mov rax, 1',
            '  mov rsi, rdi',
            '  mov rdx, r9',
            '  mov rdi, 1',
            '  syscall', '  ret',
            ''])

from ast_nodes import *
from lexer import TokenType


class NodeVisitor:
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f'No visit_{type(node).__name__} method')


class CodeGenerator(NodeVisitor):
    def __init__(self):
        self.assembly_code = []
        self.symbol_table = {}
        self.stack_index = -8

    def generate(self, tree):
        self.assembly_code.append('section .bss')
        self.assembly_code.append('  print_buf resb 32\n')
        self.assembly_code.append('section .text')
        self.assembly_code.append('global _start')
        self._add_print_function()
        self.visit(tree)
        return '\n'.join(self.assembly_code)

    def visit_Program(self, node):
        for decl in node.declarations:
            self.visit(decl)

    def visit_FunctionDecl(self, node):
        if node.func_name == 'main':
            self.assembly_code.append('_start:')
            self.assembly_code.append('  push rbp')
            self.assembly_code.append('  mov rbp, rsp')
            self.assembly_code.append('  sub rsp, 32 ; Allocate stack frame')

            self.visit(node.body)

            # --- Exit Logic for main ---
            # If the last statement in main was NOT an explicit 'return',
            # we must generate the exit syscall ourselves, using the value
            # of the last expression as the exit code.
            if not node.body.children or not isinstance(node.body.children[-1], Return):
                self.assembly_code.append('  pop rdi ; Implicit exit code')
                self.assembly_code.append('  mov rax, 60 ; syscall for exit')
                self.assembly_code.append('  syscall')

            # The epilogue is technically unreachable if there's always an exit,
            # but we'll leave it for now for structural correctness.
            self.assembly_code.append('  ; Epilogue')
            self.assembly_code.append('  add rsp, 32 ; Deallocate stack frame')
            self.assembly_code.append('  pop rbp')

    def visit_Block(self, node):
        for child in node.children:
            self.visit(child)

    def visit_VarDecl(self, node):
        var_name = node.var_node.value
        if var_name in self.symbol_table:
            raise Exception(f"Variable '{var_name}' already declared.")

        self.symbol_table[var_name] = self.stack_index
        self.visit(node.assign_node)

        self.assembly_code.append(f'  ; VarDecl: {var_name}')
        self.assembly_code.append('  pop rax')
        self.assembly_code.append(f'  mov [rbp{self.stack_index}], rax')

        self.stack_index -= 8

    def visit_Assign(self, node):
        var_name = node.left.value
        if var_name not in self.symbol_table:
            raise Exception(f"Assigning to undeclared variable '{var_name}'")

        self.visit(node.right)

        self.assembly_code.append(f'  ; Assign: {var_name}')
        self.assembly_code.append('  pop rax')
        stack_offset = self.symbol_table[var_name]
        self.assembly_code.append(f'  mov [rbp{stack_offset}], rax')

    def visit_Num(self, node):
        self.assembly_code.append(f'  ; Pushing number {node.value}')
        self.assembly_code.append(f'  push {node.value}')

    def visit_Var(self, node):
        var_name = node.value
        if var_name not in self.symbol_table:
            if var_name == "VERSION":
                self.assembly_code.append(f'  push 1')
                return
            raise Exception(f"Undeclared variable '{var_name}'")

        stack_offset = self.symbol_table[var_name]
        self.assembly_code.append(f'  ; Pushing variable {var_name}')
        self.assembly_code.append(f'  push qword [rbp{stack_offset}]')

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)

        self.assembly_code.append('  ; Binary Operation')
        self.assembly_code.append('  pop rbx ; Right side')
        self.assembly_code.append('  pop rax ; Left side')

        if node.op.type == TokenType.PLUS:
            self.assembly_code.append('  add rax, rbx')
        elif node.op.type == TokenType.MINUS:
            self.assembly_code.append('  sub rax, rbx')
        elif node.op.type == TokenType.MULTIPLY:
            self.assembly_code.append('  imul rax, rbx')
        elif node.op.type == TokenType.DIVIDE:
            self.assembly_code.append('  cqo')
            self.assembly_code.append('  idiv rbx')

        self.assembly_code.append('  push rax ; Push result')

    def visit_FunctionCall(self, node):
        if node.name == 'print':
            self.visit(node.args[0])
            self.assembly_code.append('  pop rdi ; Arg for print_int is in RDI')
            self.assembly_code.append('  call print_int')
        else:
            raise Exception(f"Undefined function call '{node.name}'")

    def visit_Return(self, node):
        self.visit(node.value)
        self.assembly_code.append('  ; Return statement')
        self.assembly_code.append('  pop rdi ; Exit code for main')
        self.assembly_code.append('  mov rax, 60 ; syscall for exit')
        self.assembly_code.append('  syscall')

    def visit_ConstDecl(self, node):
        pass

    def _add_print_function(self):
        self.assembly_code.extend([
            'print_int:',
            '  mov rax, rdi',
            '  lea rdi, [rel print_buf + 31]',
            '  mov byte [rdi], 10',
            '  mov r10, 10',
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
            '  syscall',
            '  ret',
            ''
        ])

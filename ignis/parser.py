from lexer import TokenType
from ast_nodes import *

class Parser:
    def __init__(self, lexer, reporter):
        self.lexer = lexer
        self.reporter = reporter
        self.current_token = self.lexer.get_next_token()
        self.peek_token = self.lexer.get_next_token()

    def _format_token_type(self, token_type):
        if token_type.value.startswith('KW_'): return f"keyword '{token_type.name[3:].lower()}'"
        if len(token_type.value) <= 2 and not token_type.value.isalnum(): return f"'{token_type.value}'"
        return token_type.name

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.peek_token
            self.peek_token = self.lexer.get_next_token()
        else:
            expected_str = self._format_token_type(token_type)
            got_str = self._format_token_type(self.current_token.type)
            self.reporter.error("E001", f"Unexpected token: expected {expected_str}, but got {got_str}", self.current_token)

    # ... (The rest of the parser is unchanged from the last working version) ...
    def type_spec(self):
        pointer_level = 0
        while self.current_token.type == TokenType.KW_PTR:
            pointer_level += 1
            self.eat(TokenType.KW_PTR)
        token = self.current_token
        if token.type == TokenType.KW_INT or token.type == TokenType.IDENTIFIER:
            self.eat(token.type)
            return Type(token, pointer_level)
        self.reporter.error("E017", "Expected a base type specifier (e.g., 'int' or a struct name)", token)
    def factor(self):
        token = self.current_token
        if token.type == TokenType.INTEGER: self.eat(TokenType.INTEGER); return Num(token)
        elif token.type == TokenType.LPAREN: self.eat(TokenType.LPAREN); node = self.expr(); self.eat(TokenType.RPAREN); return node
        elif token.type == TokenType.LBRACE: return self.block()
        elif token.type == TokenType.KW_IF: return self.if_expression()
        node = None
        if token.type == TokenType.IDENTIFIER:
            if self.peek_token.type == TokenType.LPAREN: node = self.function_call()
            else: self.eat(TokenType.IDENTIFIER); node = Var(token)
        else: self.reporter.error("E018", "Invalid factor in expression", token)
        while self.current_token.type == TokenType.DOT:
            self.eat(TokenType.DOT)
            field_node = Var(self.current_token)
            self.eat(TokenType.IDENTIFIER)
            node = MemberAccess(left=node, right=field_node)
        return node
    def unary_expr(self):
        token = self.current_token
        UNARY_OPS = (TokenType.KW_NOT, TokenType.KW_BNOT, TokenType.KW_NNOT, TokenType.KW_NBNOT, TokenType.KW_ADDR, TokenType.KW_DEREF)
        if token.type in UNARY_OPS:
            self.eat(token.type)
            return UnaryOp(op=token, expr=self.unary_expr())
        return self.factor()
    def term(self):
        node = self.unary_expr()
        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            token = self.current_token
            if token.type == TokenType.MULTIPLY: self.eat(TokenType.MULTIPLY)
            elif token.type == TokenType.DIVIDE: self.eat(TokenType.DIVIDE)
            node = BinOp(left=node, op=token, right=self.unary_expr())
        return node
    def additive_expr(self):
        node = self.term()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            if token.type == TokenType.PLUS: self.eat(TokenType.PLUS)
            elif token.type == TokenType.MINUS: self.eat(TokenType.MINUS)
            node = BinOp(left=node, op=token, right=self.term())
        return node
    def comparison_expr(self):
        node = self.additive_expr()
        COMPARISON_OPS = (TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.TYPE_EQUAL)
        if self.current_token.type in COMPARISON_OPS:
            op = self.current_token; self.eat(op.type); right = self.additive_expr()
            node = BinOp(left=node, op=op, right=right)
        return node
    def logical_and_expr(self):
        node = self.comparison_expr()
        LOGICAL_AND_OPS = (TokenType.KW_AND, TokenType.KW_NAND)
        while self.current_token.type in LOGICAL_AND_OPS:
            op = self.current_token; self.eat(op.type)
            node = BinOp(left=node, op=op, right=self.comparison_expr())
        return node
    def logical_or_expr(self):
        node = self.logical_and_expr()
        LOGICAL_OR_OPS = (TokenType.KW_OR, TokenType.KW_NOR, TokenType.KW_XOR, TokenType.KW_XNOR)
        while self.current_token.type in LOGICAL_OR_OPS:
            op = self.current_token; self.eat(op.type)
            node = BinOp(left=node, op=op, right=self.logical_and_expr())
        return node
    def expr(self):
        node = self.logical_or_expr()
        if self.current_token.type == TokenType.KW_IF:
            self.eat(TokenType.KW_IF); condition = self.expr(); self.eat(TokenType.KW_ELSE)
            else_expr = self.expr(); if_block = Block(); if_block.children.append(node)
            else_block = Block(); else_block.children.append(else_expr)
            return IfExpr(condition=condition, if_block=if_block, else_block=else_block)
        return node
    def if_expression(self):
        if self.current_token.type == TokenType.KW_IF: self.eat(TokenType.KW_IF)
        elif self.current_token.type == TokenType.KW_ELIF: self.eat(TokenType.KW_ELIF)
        self.eat(TokenType.LPAREN); condition = self.expr(); self.eat(TokenType.RPAREN)
        if_block = self.block(); else_block = None
        if self.current_token.type == TokenType.KW_ELIF: else_block = self.if_expression()
        elif self.current_token.type == TokenType.KW_ELSE: self.eat(TokenType.KW_ELSE); else_block = self.block()
        else: self.reporter.error("E019", "Expected 'else' or 'elif' for if-expression", self.current_token)
        return IfExpr(condition, if_block, else_block)
    def while_statement(self):
        self.eat(TokenType.KW_WHILE)
        self.eat(TokenType.LPAREN); condition = self.expr(); self.eat(TokenType.RPAREN)
        body = self.block()
        return WhileStmt(condition, body)
    def loop_statement(self):
        self.eat(TokenType.KW_LOOP)
        body = self.block()
        return LoopStmt(body)
    def for_statement(self):
        self.eat(TokenType.KW_FOR); self.eat(TokenType.LPAREN)
        init_node = None
        if self.current_token.type != TokenType.SEMICOLON:
            if self.current_token.type in (TokenType.KW_INT, TokenType.KW_MUT, TokenType.KW_PTR, TokenType.IDENTIFIER): init_node = self.variable_declaration()
            else: init_node = self.assignment_statement(self.expr())
        self.eat(TokenType.SEMICOLON)
        condition_node = None
        if self.current_token.type != TokenType.SEMICOLON: condition_node = self.expr()
        self.eat(TokenType.SEMICOLON)
        increment_node = None
        if self.current_token.type != TokenType.RPAREN: increment_node = self.assignment_statement(self.expr())
        self.eat(TokenType.RPAREN)
        body_node = self.block()
        return ForStmt(init_node, condition_node, increment_node, body_node)
    def break_statement(self): self.eat(TokenType.KW_BREAK); return BreakStmt()
    def continue_statement(self): self.eat(TokenType.KW_CONTINUE); return ContinueStmt()
    def variable_declaration(self):
        is_mutable = False
        if self.current_token.type == TokenType.KW_MUT: is_mutable = True; self.eat(TokenType.KW_MUT)
        type_node = self.type_spec(); var_token = self.current_token; self.eat(TokenType.IDENTIFIER)
        var_node = Var(var_token); assign_node = None
        if self.current_token.type == TokenType.ASSIGN:
            self.eat(TokenType.ASSIGN); assign_node = self.expr()
        return VarDecl(type_node, var_node, assign_node, is_mutable)
    def constant_declaration(self):
        self.eat(TokenType.KW_CONST); type_node = self.type_spec(); var_token = self.current_token
        self.eat(TokenType.IDENTIFIER); var_node = Var(var_token); self.eat(TokenType.ASSIGN)
        assign_node = self.expr(); return ConstDecl(type_node, var_node, assign_node)
    def return_statement(self): self.eat(TokenType.KW_RETURN); value = self.expr(); return Return(value)
    def assignment_statement(self, left_node):
        op = self.current_token; self.eat(TokenType.ASSIGN); right = self.expr()
        return Assign(left_node, op, right)
    def statement(self):
        token_type = self.current_token.type
        if token_type == TokenType.KW_WHILE: return self.while_statement()
        if token_type == TokenType.KW_LOOP: return self.loop_statement()
        if token_type == TokenType.KW_FOR: return self.for_statement()
        if token_type in (TokenType.KW_INT, TokenType.KW_MUT, TokenType.KW_PTR, TokenType.IDENTIFIER) and self.peek_token.type == TokenType.IDENTIFIER:
            node = self.variable_declaration()
        elif token_type == TokenType.KW_RETURN: node = self.return_statement()
        elif token_type == TokenType.KW_BREAK: node = self.break_statement()
        elif token_type == TokenType.KW_CONTINUE: node = self.continue_statement()
        else:
            node = self.expr()
            if self.current_token.type == TokenType.ASSIGN:
                if not isinstance(node, (Var, UnaryOp, MemberAccess)): self.reporter.error("E010", "Invalid assignment target.", self._get_token_from_node(node))
                node = self.assignment_statement(left_node=node)
        self.eat(TokenType.SEMICOLON)
        return node
    def block(self):
        self.eat(TokenType.LBRACE); nodes = []
        while self.current_token.type != TokenType.RBRACE:
            if self.peek_token.type == TokenType.RBRACE: nodes.append(self.expr())
            else: nodes.append(self.statement())
        self.eat(TokenType.RBRACE)
        root = Block();
        for node in nodes: root.children.append(node)
        return root
    def parameter_list(self):
        params = []
        if self.current_token.type == TokenType.RPAREN: return params
        type_node = self.type_spec(); var_node = Var(self.current_token); self.eat(TokenType.IDENTIFIER)
        params.append(Param(type_node, var_node))
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            type_node = self.type_spec(); var_node = Var(self.current_token); self.eat(TokenType.IDENTIFIER)
            params.append(Param(type_node, var_node))
        return params
    def struct_definition(self):
        self.eat(TokenType.KW_STRUCT); name_token = self.current_token; self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.LBRACE); fields = []
        while self.current_token.type != TokenType.RBRACE:
            type_node = self.type_spec(); var_node = Var(self.current_token); self.eat(TokenType.IDENTIFIER)
            self.eat(TokenType.SEMICOLON)
            fields.append(Field(type_node, var_node))
        self.eat(TokenType.RBRACE)
        return StructDef(name_token.value, fields)
    def declaration(self):
        if self.current_token.type == TokenType.KW_CONST:
            node = self.constant_declaration(); self.eat(TokenType.SEMICOLON); return node
        if self.current_token.type == TokenType.KW_STRUCT:
            return self.struct_definition()
        type_node = self.type_spec(); func_name = self.current_token.value; self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.LPAREN); params = self.parameter_list(); self.eat(TokenType.RPAREN)
        body = self.block()
        return FunctionDecl(type_node, func_name, params, body)
    def parse(self):
        declarations = [];
        while self.current_token.type != TokenType.EOF: declarations.append(self.declaration())
        if not declarations: self.reporter.error("E020", "Source file contains no code (or no 'main' function).", self.current_token)
        return Program(declarations)
    def function_call(self):
        name_node = Var(self.current_token); self.eat(TokenType.IDENTIFIER); self.eat(TokenType.LPAREN)
        args = [];
        if self.current_token.type != TokenType.RPAREN:
            args.append(self.expr())
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                args.append(self.expr())
        self.eat(TokenType.RPAREN)
        return FunctionCall(name_node, args)
    def _get_token_from_node(self, node):
        if hasattr(node, 'token'): return node.token
        if hasattr(node, 'op'): return node.op
        if hasattr(node, 'name_node'): return node.name_node.token
        if hasattr(node, 'var_node'): return node.var_node.token
        if isinstance(node, MemberAccess): return self._get_token_from_node(node.left)
        return None


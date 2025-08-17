from lexer import TokenType
from ast_nodes import *


class Parser:
    def __init__(self, lexer, source_code):
        self.lexer = lexer
        self.source_lines = source_code.split('\n')
        self.current_token = self.lexer.get_next_token()
        self.peek_token = self.lexer.get_next_token()

    def error(self, message, token=None):
        token = token or self.current_token
        line_num, col_num = token.line, token.col
        header = f"E001: {message}";
        location = f"--> {self.lexer.file_path}:{line_num}:{col_num}"
        snippet = "";
        start_line = max(0, line_num - 3);
        end_line = min(len(self.source_lines), line_num + 2)
        for i in range(start_line, end_line):
            line = self.source_lines[i];
            line_number_str = f"{i + 1:4} | ";
            snippet += f"{line_number_str}{line}\n"
            if i + 1 == line_num: pointer_padding = ' ' * (
                        len(line_number_str) + col_num - 1); snippet += f"{pointer_padding}^\n"
        hint = ""
        if "expected SEMICOLON" in message: hint = "Hint: Did you forget a ';' at the end of a statement?"
        full_error = f"{header}\n{location}\n\n{snippet}"
        if hint: full_error += f"\n{hint}"
        raise Exception(f'Parser error:\n{full_error}')

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.peek_token
            self.peek_token = self.lexer.get_next_token()
        else:
            self.error(f"Unexpected token: expected {token_type.name}, but got {self.current_token.type.name}")

    def type_spec(self):
        token = self.current_token
        if token.type == TokenType.KW_INT: self.eat(TokenType.KW_INT); return Type(token)
        self.error("Expected a type specifier")

    def factor(self):
        token = self.current_token
        if token.type == TokenType.INTEGER:
            self.eat(TokenType.INTEGER); return Num(token)
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN); node = self.expr(); self.eat(TokenType.RPAREN); return node
        elif token.type == TokenType.LBRACE:
            return self.block()
        elif token.type == TokenType.KW_IF:
            return self.if_expression()
        elif token.type == TokenType.IDENTIFIER:
            if self.peek_token.type == TokenType.LPAREN:
                return self.function_call()
            else:
                self.eat(TokenType.IDENTIFIER); return Var(token)
        self.error(f"Invalid factor in expression")

    def term(self):
        node = self.factor()
        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            token = self.current_token
            if token.type == TokenType.MULTIPLY:
                self.eat(TokenType.MULTIPLY)
            elif token.type == TokenType.DIVIDE:
                self.eat(TokenType.DIVIDE)
            node = BinOp(left=node, op=token, right=self.factor())
        return node

    def additive_expr(self):
        node = self.term()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            if token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
            elif token.type == TokenType.MINUS:
                self.eat(TokenType.MINUS)
            node = BinOp(left=node, op=token, right=self.term())
        return node

    def comparison_expr(self):
        node = self.additive_expr()
        COMPARISON_OPS = (TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL, TokenType.GREATER,
                          TokenType.GREATER_EQUAL, TokenType.TYPE_EQUAL)
        if self.current_token.type in COMPARISON_OPS:
            op = self.current_token;
            self.eat(op.type);
            right = self.additive_expr()
            node = BinOp(left=node, op=op, right=right)
        return node

    def expr(self):
        node = self.comparison_expr()
        if self.current_token.type == TokenType.KW_IF:
            self.eat(TokenType.KW_IF);
            condition = self.comparison_expr();
            self.eat(TokenType.KW_ELSE)
            else_expr = self.expr();
            if_block = Block();
            if_block.children.append(node)
            else_block = Block();
            else_block.children.append(else_expr)
            return IfExpr(condition=condition, if_block=if_block, else_block=else_block)
        return node

    def if_expression(self):
        if self.current_token.type == TokenType.KW_IF:
            self.eat(TokenType.KW_IF)
        elif self.current_token.type == TokenType.KW_ELIF:
            self.eat(TokenType.KW_ELIF)
        self.eat(TokenType.LPAREN);
        condition = self.expr();
        self.eat(TokenType.RPAREN)
        if_block = self.block();
        else_block = None
        if self.current_token.type == TokenType.KW_ELIF:
            else_block = self.if_expression()
        elif self.current_token.type == TokenType.KW_ELSE:
            self.eat(TokenType.KW_ELSE); else_block = self.block()
        else:
            self.error("Expected 'else' or 'elif' for if-expression.")
        return IfExpr(condition, if_block, else_block)

    def while_statement(self):
        self.eat(TokenType.KW_WHILE)
        self.eat(TokenType.LPAREN);
        condition = self.expr();
        self.eat(TokenType.RPAREN)
        body = self.block()
        return WhileStmt(condition, body)

    def loop_statement(self):
        self.eat(TokenType.KW_LOOP)
        body = self.block()
        return LoopStmt(body)

    def break_statement(self):
        self.eat(TokenType.KW_BREAK)
        return BreakStmt()

    def continue_statement(self):
        self.eat(TokenType.KW_CONTINUE)
        return ContinueStmt()

    def variable_declaration(self):
        is_mutable = False
        if self.current_token.type == TokenType.KW_MUT: is_mutable = True; self.eat(TokenType.KW_MUT)
        type_node = self.type_spec();
        var_token = self.current_token;
        self.eat(TokenType.IDENTIFIER)
        var_node = Var(var_token);
        self.eat(TokenType.ASSIGN);
        assign_node = self.expr()
        return VarDecl(type_node, var_node, assign_node, is_mutable)

    def constant_declaration(self):
        self.eat(TokenType.KW_CONST);
        type_node = self.type_spec();
        var_token = self.current_token
        self.eat(TokenType.IDENTIFIER);
        var_node = Var(var_token);
        self.eat(TokenType.ASSIGN)
        assign_node = self.expr();
        return ConstDecl(type_node, var_node, assign_node)

    def return_statement(self):
        self.eat(TokenType.KW_RETURN);
        value = self.expr();
        return Return(value)

    def statement(self):
        token_type = self.current_token.type

        if token_type == TokenType.KW_WHILE: return self.while_statement()
        if token_type == TokenType.KW_LOOP: return self.loop_statement()

        node = None
        if token_type in (TokenType.KW_INT, TokenType.KW_MUT):
            node = self.variable_declaration()
        elif token_type == TokenType.IDENTIFIER and self.peek_token.type == TokenType.ASSIGN:
            node = self.assignment_statement()
        elif token_type == TokenType.KW_RETURN:
            node = self.return_statement()
        elif token_type == TokenType.KW_BREAK:
            node = self.break_statement()
        elif token_type == TokenType.KW_CONTINUE:
            node = self.continue_statement()
        else:
            node = self.expr()

        self.eat(TokenType.SEMICOLON)
        return node

    def block(self):
        self.eat(TokenType.LBRACE);
        nodes = []
        while self.current_token.type != TokenType.RBRACE:
            if self.peek_token.type == TokenType.RBRACE:
                nodes.append(self.expr())
            else:
                nodes.append(self.statement())
        self.eat(TokenType.RBRACE)
        root = Block();
        for node in nodes: root.children.append(node)
        return root

    def declaration(self):
        if self.current_token.type == TokenType.KW_CONST:
            node = self.constant_declaration();
            self.eat(TokenType.SEMICOLON);
            return node
        if self.current_token.type == TokenType.KW_INT:
            type_node = self.type_spec();
            func_name = self.current_token.value;
            self.eat(TokenType.IDENTIFIER)
            self.eat(TokenType.LPAREN);
            self.eat(TokenType.RPAREN);
            body = self.block()
            return FunctionDecl(type_node, func_name, body)
        self.error(f"Invalid top-level declaration")

    def parse(self):
        declarations = [];
        while self.current_token.type != TokenType.EOF: declarations.append(self.declaration())
        if not declarations: self.error("Source file contains no code (or no 'main' function).")
        return Program(declarations)

    def assignment_statement(self):
        left = Var(self.current_token);
        self.eat(TokenType.IDENTIFIER);
        op = self.current_token
        self.eat(TokenType.ASSIGN);
        right = self.expr();
        return Assign(left, op, right)

    def function_call(self):
        name_token = self.current_token;
        self.eat(TokenType.IDENTIFIER);
        self.eat(TokenType.LPAREN)
        args = [];
        if self.current_token.type != TokenType.RPAREN: args.append(self.expr())
        self.eat(TokenType.RPAREN);
        return FunctionCall(name_token.value, args)

from lexer import TokenType
from ast_nodes import *


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        # Initialize two tokens for lookahead
        self.current_token = self.lexer.get_next_token()
        self.peek_token = self.lexer.get_next_token()

    def error(self, message):
        raise Exception(f'Parser error: {message}')

    def eat(self, token_type):
        """
        Consume the current token if it matches the expected type and advance.
        If it doesn't match, raise an error.
        """
        if self.current_token.type == token_type:
            self.current_token = self.peek_token
            self.peek_token = self.lexer.get_next_token()
        else:
            self.error(f"Unexpected token: expected {token_type}, got {self.current_token.type}")

    def factor(self):
        """
        Parses the highest-priority parts of an expression.
        factor : INTEGER | IDENTIFIER | ( expr ) | function_call
        """
        token = self.current_token
        if token.type == TokenType.INTEGER:
            self.eat(TokenType.INTEGER)
            return Num(token)
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node
        elif token.type == TokenType.IDENTIFIER:
            # Use peek_token to decide if it's a function call or a variable
            if self.peek_token.type == TokenType.LPAREN:
                return self.function_call()
            else:
                self.eat(TokenType.IDENTIFIER)
                return Var(token)
        self.error(f"Invalid factor in expression. Current token: {token}")

    def term(self):
        """
        Parses multiplication and division.
        term : factor ((MULTIPLY | DIVIDE) factor)*
        """
        node = self.factor()
        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            token = self.current_token
            if token.type == TokenType.MULTIPLY:
                self.eat(TokenType.MULTIPLY)
            elif token.type == TokenType.DIVIDE:
                self.eat(TokenType.DIVIDE)
            node = BinOp(left=node, op=token, right=self.factor())
        return node

    def expr(self):
        """
        Parses addition and subtraction.
        expr : term ((PLUS | MINUS) term)*
        """
        node = self.term()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            if token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
            elif token.type == TokenType.MINUS:
                self.eat(TokenType.MINUS)
            node = BinOp(left=node, op=token, right=self.term())
        return node

    def type_spec(self):
        """Parses a type specifier like 'int'."""
        token = self.current_token
        if token.type == TokenType.KW_INT:
            self.eat(TokenType.KW_INT)
            return Type(token)
        self.error("Expected a type specifier")

    def variable_declaration(self):
        """
        Parses a variable declaration.
        var_declaration : (KW_MUT)? type_spec IDENTIFIER ASSIGN expr
        """
        is_mutable = False
        if self.current_token.type == TokenType.KW_MUT:
            is_mutable = True
            self.eat(TokenType.KW_MUT)

        type_node = self.type_spec()
        var_token = self.current_token
        self.eat(TokenType.IDENTIFIER)
        var_node = Var(var_token)

        self.eat(TokenType.ASSIGN)
        assign_node = self.expr()

        return VarDecl(type_node, var_node, assign_node, is_mutable)

    def constant_declaration(self):
        """
        Parses a constant declaration.
        const_declaration : KW_CONST type_spec IDENTIFIER ASSIGN expr
        """
        self.eat(TokenType.KW_CONST)
        type_node = self.type_spec()
        var_token = self.current_token
        self.eat(TokenType.IDENTIFIER)
        var_node = Var(var_token)

        self.eat(TokenType.ASSIGN)
        assign_node = self.expr()

        return ConstDecl(type_node, var_node, assign_node)

    def assignment_statement(self):
        """
        Parses an assignment to an existing variable.
        assignment_statement : variable ASSIGN expr
        """
        left = Var(self.current_token)
        self.eat(TokenType.IDENTIFIER)
        op = self.current_token
        self.eat(TokenType.ASSIGN)
        right = self.expr()
        return Assign(left, op, right)

    def function_call(self):
        """
        Parses a function call.
        function_call: IDENTIFIER LPAREN (expr)? RPAREN
        """
        name_token = self.current_token
        self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.LPAREN)
        args = []
        if self.current_token.type != TokenType.RPAREN:
            args.append(self.expr())
        self.eat(TokenType.RPAREN)
        return FunctionCall(name_token.value, args)

    def return_statement(self):
        """Parses a return statement."""
        self.eat(TokenType.KW_RETURN)
        value = self.expr()
        return Return(value)

    def statement(self):
        """Parses a single statement."""
        token_type = self.current_token.type

        if token_type in (TokenType.KW_INT, TokenType.KW_MUT):
            node = self.variable_declaration()
        elif token_type == TokenType.IDENTIFIER and self.peek_token.type == TokenType.ASSIGN:
            node = self.assignment_statement()
        elif token_type == TokenType.IDENTIFIER and self.peek_token.type == TokenType.LPAREN:
            node = self.function_call()
        elif token_type == TokenType.KW_RETURN:
            node = self.return_statement()
        else:
            self.error(f"Invalid statement. Current token: {self.current_token}")

        self.eat(TokenType.SEMICOLON)
        return node

    def compound_statement(self):
        """Parses a block of statements { ... }"""
        self.eat(TokenType.LBRACE)
        nodes = []
        while self.current_token.type != TokenType.RBRACE:
            nodes.append(self.statement())
        self.eat(TokenType.RBRACE)

        root = Compound()
        for node in nodes:
            root.children.append(node)
        return root

    def declaration(self):
        """Parses any top-level declaration."""
        if self.current_token.type == TokenType.KW_CONST:
            node = self.constant_declaration()
            self.eat(TokenType.SEMICOLON)
            return node

        if self.current_token.type == TokenType.KW_INT:
            type_node = self.type_spec()
            func_name = self.current_token.value
            self.eat(TokenType.IDENTIFIER)
            self.eat(TokenType.LPAREN)
            self.eat(TokenType.RPAREN)
            body = self.compound_statement()
            return FunctionDecl(type_node, func_name, body)

        self.error(f"Invalid top-level declaration. Unexpected token: {self.current_token}")

    def parse(self):
        """Main entry point. Parses the entire program."""
        declarations = []
        while self.current_token.type != TokenType.EOF:
            declarations.append(self.declaration())

        return Program(declarations)

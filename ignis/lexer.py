from enum import Enum

class TokenType(Enum):
    # Single-character tokens
    PLUS          = '+'
    MINUS         = '-'
    MULTIPLY      = '*'
    DIVIDE        = '/'
    LPAREN        = '('
    RPAREN        = ')'
    LBRACE        = '{'
    RBRACE        = '}'
    SEMICOLON     = ';'
    ASSIGN        = '='
    LESS          = '<'
    GREATER       = '>'

    # Multi-character tokens
    EQUAL   = '=='
    NOT_EQUAL     = '!='
    LESS_EQUAL    = '<='
    GREATER_EQUAL = '>='

    # Keywords
    KW_INT        = 'int'
    KW_MUT        = 'mut'
    KW_CONST      = 'const'
    KW_RETURN     = 'return'
    KW_IF         = 'if'
    KW_ELSE       = 'else'

    # Literals and identifiers
    IDENTIFIER    = 'IDENTIFIER'
    INTEGER       = 'INTEGER'

    # End of File
    EOF           = 'EOF'

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value
    def __str__(self):
        return f'Token({self.type.name}, {repr(self.value)})'
    def __repr__(self):
        return self.__str__()

RESERVED_KEYWORDS = {
    'int': Token(TokenType.KW_INT, 'int'),
    'mut': Token(TokenType.KW_MUT, 'mut'),
    'const': Token(TokenType.KW_CONST, 'const'),
    'return': Token(TokenType.KW_RETURN, 'return'),
    'if': Token(TokenType.KW_IF, 'if'),
    'else': Token(TokenType.KW_ELSE, 'else'),
}

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def error(self, message):
        raise Exception(f'Lexer error: {message}')

    def advance(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        if self.current_char == '/' and self.peek() == '/':
            while self.current_char is not None and self.current_char != '\n':
                self.advance()
            return

        if self.current_char == '/' and self.peek() == '*':
            self.advance(); self.advance()
            nesting_level = 1
            while nesting_level > 0:
                if self.current_char is None: self.error("Unterminated multi-line comment.")
                elif self.current_char == '/' and self.peek() == '*': self.advance(); self.advance(); nesting_level += 1
                elif self.current_char == '*' and self.peek() == '/': self.advance(); self.advance(); nesting_level -= 1
                else: self.advance()
            return

    def number(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def identifier(self):
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        token = RESERVED_KEYWORDS.get(result, Token(TokenType.IDENTIFIER, result))
        return token

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace(): self.skip_whitespace(); continue
            if self.current_char == '/' and (self.peek() == '/' or self.peek() == '*'): self.skip_comment(); continue
            if self.current_char.isdigit(): return Token(TokenType.INTEGER, self.number())
            if self.current_char.isalpha() or self.current_char == '_': return self.identifier()

            # Handle multi-character operators first
            if self.current_char == '=' and self.peek() == '=': self.advance(); self.advance(); return Token(TokenType.EQUAL_EQUAL, '==')
            if self.current_char == '!' and self.peek() == '=': self.advance(); self.advance(); return Token(TokenType.NOT_EQUAL, '!=')
            if self.current_char == '<' and self.peek() == '=': self.advance(); self.advance(); return Token(TokenType.LESS_EQUAL, '<=')
            if self.current_char == '>' and self.peek() == '=': self.advance(); self.advance(); return Token(TokenType.GREATER_EQUAL, '>=')

            # Handle single-character tokens
            try:
                token_type = TokenType(self.current_char)
                token = Token(token_type, token_type.value)
                self.advance()
                return token
            except ValueError:
                self.error(f"Invalid character '{self.current_char}'")

        return Token(TokenType.EOF, None)

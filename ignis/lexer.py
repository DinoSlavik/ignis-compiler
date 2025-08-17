from enum import Enum


class TokenType(Enum):
    # Single-character tokens
    PLUS = '+'
    MINUS = '-'
    MULTIPLY = '*'
    DIVIDE = '/'
    LPAREN = '('
    RPAREN = ')'
    LBRACE = '{'
    RBRACE = '}'
    SEMICOLON = ';'
    ASSIGN = '='
    LESS = '<'
    GREATER = '>'

    # Multi-character tokens
    EQUAL = '=='
    NOT_EQUAL = '!='
    LESS_EQUAL = '<='
    GREATER_EQUAL = '>='
    TYPE_EQUAL = '==='

    # Keywords
    KW_INT = 'int'
    KW_MUT = 'mut'
    KW_CONST = 'const'
    KW_RETURN = 'return'
    KW_IF = 'if'
    KW_ELSE = 'else'
    KW_ELIF = 'elif'
    KW_WHILE = 'while'
    KW_LOOP = 'loop'
    KW_FOR = 'for'
    KW_BREAK = 'break'
    KW_CONTINUE = 'continue'

    # Literals and identifiers
    IDENTIFIER = 'IDENTIFIER'
    INTEGER = 'INTEGER'
    EOF = 'EOF'


class Token:
    def __init__(self, type, value, line=None, col=None):
        self.type = type
        self.value = value
        self.line = line
        self.col = col

    def __str__(self):
        return f'Token({self.type.name}, {repr(self.value)}, line={self.line}, col={self.col})'

    def __repr__(self):
        return self.__str__()


RESERVED_KEYWORDS = {
    'int': TokenType.KW_INT,
    'mut': TokenType.KW_MUT,
    'const': TokenType.KW_CONST,
    'return': TokenType.KW_RETURN,
    'if': TokenType.KW_IF,
    'else': TokenType.KW_ELSE,
    'elif': TokenType.KW_ELIF,
    'while': TokenType.KW_WHILE,
    'loop': TokenType.KW_LOOP,
    'for': TokenType.KW_FOR,
    'break': TokenType.KW_BREAK,
    'continue': TokenType.KW_CONTINUE,
}


class Lexer:
    def __init__(self, text, file_path='<stdin>'):
        self.text = text
        self.file_path = file_path # New field
        self.pos = 0
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
        self.line = 1
        self.col = 1

    def error(self, message):
        raise Exception(f'Lexer error: {message}')

    def advance(self):
        if self.current_char == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1

        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def peek(self, offset=1):
        peek_pos = self.pos + offset
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
            self.advance()
            self.advance()
            nesting_level = 1
            while nesting_level > 0:
                if self.current_char is None:
                    self.error("Unterminated multi-line comment.")
                elif self.current_char == '/' and self.peek() == '*':
                    self.advance()
                    self.advance()
                    nesting_level += 1
                elif self.current_char == '*' and self.peek() == '/':
                    self.advance()
                    self.advance()
                    nesting_level -= 1
                else:
                    self.advance()
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

        token_type = RESERVED_KEYWORDS.get(result, TokenType.IDENTIFIER)
        # Note: The line/col are from the *start* of the identifier, which is correct.
        # We pass them back to get_next_token to create the final Token object.
        return token_type, result

    def get_next_token(self):
        while self.current_char is not None:
            # Capture position at the beginning of the token
            line, col = self.line, self.col

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == '/' and (self.peek() == '/' or self.peek() == '*'):
                self.skip_comment()
                continue

            if self.current_char.isdigit():
                return Token(TokenType.INTEGER, self.number(), line, col)

            if self.current_char.isalpha() or self.current_char == '_':
                token_type, value = self.identifier()
                return Token(token_type, value, line, col)

            # Multi-character operators
            if self.current_char == '=' and self.peek() == '=' and self.peek(2) == '=':
                self.advance();
                self.advance();
                self.advance()
                return Token(TokenType.TYPE_EQUAL, '===', line, col)
            if self.current_char == '=' and self.peek() == '=':
                self.advance();
                self.advance()
                return Token(TokenType.EQUAL, '==', line, col)
            if self.current_char == '!' and self.peek() == '=':
                self.advance();
                self.advance()
                return Token(TokenType.NOT_EQUAL, '!=', line, col)
            if self.current_char == '<' and self.peek() == '=':
                self.advance();
                self.advance()
                return Token(TokenType.LESS_EQUAL, '<=', line, col)
            if self.current_char == '>' and self.peek() == '=':
                self.advance();
                self.advance()
                return Token(TokenType.GREATER_EQUAL, '>=', line, col)

            # Single-character operators
            try:
                token_type = TokenType(self.current_char)
                token = Token(token_type, token_type.value, line, col)
                self.advance()
                return token
            except ValueError:
                self.error(f"Invalid character '{self.current_char}' at line {line}, col {col}")

        return Token(TokenType.EOF, None, self.line, self.col)

from enum import Enum
from error import ErrorReporter

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
    COMMA = ','
    DOT = '.'

    # Multi-character tokens
    EQUAL = '=='
    NOT_EQUAL = '!='
    LESS_EQUAL = '<='
    GREATER_EQUAL = '>='
    TYPE_EQUAL = '==='

    # Keywords
    KW_INT = 'int'
    KW_CHAR = 'char'
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
    KW_PTR = 'ptr'
    KW_ADDR = 'addr'
    KW_DEREF = 'deref'
    KW_STRUCT = 'struct'

    # Logical and bitwise keywords
    ## Logical
    KW_OR = 'or'
    KW_AND = 'and'
    KW_NOT = 'not'
    KW_XOR = 'xor'
    ## Bitwise
    KW_BOR = 'bor'
    KW_BAND = 'band'
    KW_BNOT = 'bnot'
    KW_BXOR = 'bxor'
    ## Inverted logical
    KW_NOR = 'nor'
    KW_NAND = 'nand'
    KW_NNOT = 'nnot' # Kek
    KW_XNOR = 'xnor'
    ## Inverted bitwise
    KW_NBOR = 'nbor'
    KW_NBAND = 'nband'
    KW_NBNOT = 'nbnot' # Kek
    KW_NBXOR = 'nbxor'

    # Literals and identifiers
    IDENTIFIER = 'IDENTIFIER'
    INTEGER = 'INTEGER'
    CHAR = 'CHAR'
    STRING = 'STRING'
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
    'char': TokenType.KW_CHAR,
    'mut': TokenType.KW_MUT,
    'const': TokenType.KW_CONST,
    'return': TokenType.KW_RETURN,
    'struct': TokenType.KW_STRUCT,

    # Ifs
    'if': TokenType.KW_IF,
    'else': TokenType.KW_ELSE,
    'elif': TokenType.KW_ELIF,

    # Loops
    'while': TokenType.KW_WHILE,
    'loop': TokenType.KW_LOOP,
    'for': TokenType.KW_FOR,
    'break': TokenType.KW_BREAK,
    'continue': TokenType.KW_CONTINUE,

    # Pointers
    'ptr': TokenType.KW_PTR,
    'addr': TokenType.KW_ADDR,
    'deref': TokenType.KW_DEREF,

    # Logical and bitwise
    'or': TokenType.KW_OR,
    'and': TokenType.KW_AND,
    'not': TokenType.KW_NOT,
    'xor': TokenType.KW_XOR,
    'bor': TokenType.KW_BOR,
    'band': TokenType.KW_BAND,
    'bnot': TokenType.KW_BNOT,
    'bxor': TokenType.KW_BXOR,
    'nor': TokenType.KW_NOR,
    'nand': TokenType.KW_NAND,
    'nnot': TokenType.KW_NNOT,
    'xnor': TokenType.KW_XNOR,
    'nbor': TokenType.KW_NBOR,
    'nband': TokenType.KW_NBAND,
    'nbnot': TokenType.KW_NBNOT,
    'nbxor': TokenType.KW_NBXOR,
}


class Lexer:
    def __init__(self, text, reporter):
        self.text = text
        self.reporter = reporter
        self.pos = 0
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
        self.line = 1
        self.col = 1

    def advance(self):
        if self.current_char == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def peek(self, offset=1):
        peek_pos = self.pos + offset
        if peek_pos >= len(self.text): return None
        return self.text[peek_pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace(): self.advance()

    def skip_comment(self):
        if self.current_char == '/' and self.peek() == '/':
            while self.current_char is not None and self.current_char != '\n': self.advance()
            return
        if self.current_char == '/' and self.peek() == '*':
            start_token = Token(None, '/*', self.line, self.col)
            self.advance(); self.advance()
            nesting_level = 1
            while nesting_level > 0:
                if self.current_char is None:
                    self.reporter.error("E015", "Unterminated multi-line comment", start_token)
                elif self.current_char == '/' and self.peek() == '*': self.advance(); self.advance(); nesting_level += 1
                elif self.current_char == '*' and self.peek() == '/': self.advance(); self.advance(); nesting_level -= 1
                else: self.advance()
            return

    def number(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char; self.advance()
        return int(result)

    def string_literal(self):
        self.advance()  # Consume opening "
        result = ""
        start_token = Token(None, '"', self.line, self.col - 1)
        while self.current_char is not None and self.current_char != '"':
            if self.current_char == '\\':
                self.advance()
                if self.current_char is None:
                    self.reporter.error("E022", "Unterminated string literal.", start_token)

                if self.current_char == 'n':
                    result += '\n'
                elif self.current_char == 't':
                    result += '\t'
                elif self.current_char == '\\':
                    result += '\\'
                elif self.current_char == '"':
                    result += '"'
                else:
                    # Keep the backslash and the character for unknown sequences
                    result += '\\' + self.current_char
            else:
                result += self.current_char
            self.advance()

        if self.current_char is None:
            self.reporter.error("E022", "Unterminated string literal.", start_token)

        self.advance()  # Consume closing "
        return result

    def char_literal(self):
        self.advance()  # Consume opening '
        char_val = 0

        if self.current_char == '\\':  # Check for an escape sequence
            self.advance()
            if self.current_char == 'n':
                char_val = 10  # ASCII for newline
            elif self.current_char == 't':
                char_val = 9  # ASCII for tab
            elif self.current_char == '\\':
                char_val = 92  # ASCII for backslash
            elif self.current_char == "'":
                char_val = 39  # ASCII for single quote
            else:
                # For now, any other escaped char is just the char itself
                char_val = ord(self.current_char)
        else:
            char_val = ord(self.current_char)

        self.advance()
        if self.current_char != "'":
            self.reporter.error("E021", "Unterminated or multi-character character literal",
                                Token(None, "'", self.line, self.col - 1))

        self.advance()  # Consume closing '
        return char_val

    def identifier(self):
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char; self.advance()
        return RESERVED_KEYWORDS.get(result, TokenType.IDENTIFIER), result

    def get_next_token(self):
        while self.current_char is not None:
            line, col = self.line, self.col

            # Space
            if self.current_char.isspace():
                self.skip_whitespace(); continue
            # Comment
            if self.current_char == '/' and (self.peek() == '/' or self.peek() == '*'):
                self.skip_comment(); continue
            # Types
            if self.current_char.isdigit():
                return Token(TokenType.INTEGER, self.number(), line, col)
            if self.current_char == "\"":
                return Token(TokenType.STRING, self.string_literal(), line, col)
            if self.current_char == "\'":
                return Token(TokenType.CHAR, self.char_literal(), line, col)
            # Identifier
            if self.current_char.isalpha() or self.current_char == '_':
                token_type, value = self.identifier()
                return Token(token_type, value, line, col)
            # Operators
            if self.current_char == '=' and self.peek() == '=' and self.peek(2) == '=':
                self.advance(); self.advance(); self.advance(); return Token(TokenType.TYPE_EQUAL, '===', line, col)
            if self.current_char == '=' and self.peek() == '=':
                self.advance(); self.advance(); return Token(TokenType.EQUAL, '==', line, col)
            if self.current_char == '!' and self.peek() == '=':
                self.advance(); self.advance(); return Token(TokenType.NOT_EQUAL, '!=', line, col)
            if self.current_char == '<' and self.peek() == '=':
                self.advance(); self.advance(); return Token(TokenType.LESS_EQUAL, '<=', line, col)
            if self.current_char == '>' and self.peek() == '=':
                self.advance(); self.advance(); return Token(TokenType.GREATER_EQUAL, '>=', line, col)
            try:
                token_type = TokenType(self.current_char)
                token = Token(token_type, token_type.value, line, col); self.advance()
                return token
            except ValueError:
                self.reporter.error("E016", f"Invalid character '{self.current_char}'", Token(None, self.current_char, line, col))
        return Token(TokenType.EOF, None, self.line, self.col)
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

    # Keywords
    KW_INT        = 'int'
    KW_MUT        = 'mut'
    KW_CONST      = 'const'
    KW_RETURN     = 'return'

    # Literals and identifiers
    IDENTIFIER    = 'IDENTIFIER'
    INTEGER       = 'INTEGER'

    # End of file
    EOF           = 'EOF'

class Token:
    """
    A simple class to represent a token.
    It holds the token type and its value.
    """
    def __init__(self, t, value):
        self.type = t
        self.value = value

    def __str__(self):
        # String representation of the class instance.
        # E.g., Token(INTEGER, 10), Token(PLUS, '+')
        return f'Token({self.type.name}, {repr(self.value)})'

    def __repr__(self):
        return self.__str__()

# A mapping of reserved keywords to their token types
RESERVED_KEYWORDS = {
    'int': Token(TokenType.KW_INT, 'int'),
    'mut': Token(TokenType.KW_MUT, 'mut'),
    'const': Token(TokenType.KW_CONST, 'const'),
    'return': Token(TokenType.KW_RETURN, 'return'),
    # 'print' is treated as a regular identifier for now
}

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def error(self, message):
        """Generic error handler."""
        raise Exception(f'Lexer error: {message}')

    def advance(self):
        """Advance the 'pos' pointer and set the 'current_char' variable."""
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # Indicates end of input
        else:
            self.current_char = self.text[self.pos]

    def peek(self):
        """Look at the next character without consuming the current one."""
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def skip_whitespace(self):
        """Skips over whitespace characters."""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        """Skips over comments (both single-line and multi-line)."""
        # Single-line comment
        if self.current_char == '/' and self.peek() == '/':
            while self.current_char is not None and self.current_char != '\n':
                self.advance()
            self.advance() # Skip the newline character
            return

        # Multi-line comment
        if self.current_char == '/' and self.peek() == '*':
            self.advance()  # Consume '/'
            self.advance()  # Consume '*'
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
        """Return a (multidigit) integer consumed from the input."""
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def identifier(self):
        """Handle identifiers and reserved keywords."""
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()

        # Check if the identifier is a reserved keyword
        token = RESERVED_KEYWORDS.get(result, Token(TokenType.IDENTIFIER, result))
        return token

    def get_next_token(self):
        """
        The main lexical analyzer method. It breaks the input string into tokens.
        """
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == '/' and (self.peek() == '/' or self.peek() == '*'):
                self.skip_comment()
                continue

            if self.current_char.isdigit():
                return Token(TokenType.INTEGER, self.number())

            if self.current_char.isalpha() or self.current_char == '_':
                return self.identifier()

            # Handle single-character tokens
            try:
                token_type = TokenType(self.current_char)
                token = Token(token_type, token_type.value)
                self.advance()
                return token
            except ValueError:
                self.error(f"Invalid character '{self.current_char}'")

        return Token(TokenType.EOF, None)
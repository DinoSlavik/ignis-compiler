class AST:
    """Base class for all AST nodes."""
    pass

class Program(AST):
    """Represents the root of the program."""
    def __init__(self, declarations):
        self.declarations = declarations

    def __repr__(self):
        decls = '\n'.join(map(repr, self.declarations))
        return f"Program(\n{decls}\n)"

class FunctionDecl(AST):
    """Represents a function declaration, e.g., int main() { ... }"""
    def __init__(self, type_node, func_name, body):
        self.type_node = type_node
        self.func_name = func_name
        self.body = body

    def __repr__(self):
        return f"  FunctionDecl(name='{self.func_name}', body={self.body})"

class VarDecl(AST):
    """Represents a variable declaration, e.g., int a = 10;"""
    def __init__(self, type_node, var_node, assign_node, is_mutable):
        self.type_node = type_node
        self.var_node = var_node
        self.assign_node = assign_node
        self.is_mutable = is_mutable

    def __repr__(self):
        mut_str = 'mut ' if self.is_mutable else ''
        return f"    VarDecl({mut_str}{self.type_node.value} {self.var_node.value} = {self.assign_node})"

class ConstDecl(AST):
    """Represents a constant declaration, e.g., const int VERSION = 1;"""
    def __init__(self, type_node, var_node, assign_node):
        self.type_node = type_node
        self.var_node = var_node
        self.assign_node = assign_node

    def __repr__(self):
        return f"  ConstDecl(const {self.type_node.value} {self.var_node.value} = {self.assign_node})"


class Type(AST):
    """Represents a type specifier like 'int'."""
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def __repr__(self):
        return f"Type(value='{self.value}')"

class Assign(AST):
    """Represents an assignment operation, e.g., result = ..."""
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f"    Assign({self.left.value} = {self.right})"


class Var(AST):
    """Represents a variable usage."""
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def __repr__(self):
        return f"Var(name='{self.value}')"

class Num(AST):
    """Represents an integer number."""
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def __repr__(self):
        return f"Num(value={self.value})"

class BinOp(AST):
    """Represents a binary operation like +, -, *, /."""
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f"BinOp(left={self.left}, op='{self.op.value}', right={self.right})"

class FunctionCall(AST):
    """Represents a function call, e.g., print(result)"""
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"    FunctionCall(name='{self.name}', args={self.args})"

class Compound(AST):
    """Represents a compound statement or a block { ... }"""
    def __init__(self):
        self.children = []

    def __repr__(self):
        children_repr = '\n'.join(map(repr, self.children))
        return f"Compound([\n{children_repr}\n    ])"

class Return(AST):
    """Represents a return statement."""
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"    Return(value={self.value})"
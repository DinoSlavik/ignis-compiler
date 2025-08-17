class AST:
    pass

class Program(AST):
    def __init__(self, declarations): self.declarations = declarations
    def __repr__(self): return f"Program(\n{', '.join(map(repr, self.declarations))}\n)"

class FunctionDecl(AST):
    def __init__(self, type_node, func_name, body): self.type_node = type_node; self.func_name = func_name; self.body = body
    def __repr__(self): return f"  FunctionDecl(name='{self.func_name}', body={self.body})"

class VarDecl(AST):
    def __init__(self, type_node, var_node, assign_node, is_mutable): self.type_node = type_node; self.var_node = var_node; self.assign_node = assign_node; self.is_mutable = is_mutable
    def __repr__(self): mut_str = 'mut ' if self.is_mutable else ''; return f"    VarDecl({mut_str}{self.type_node.value} {self.var_node.value} = {self.assign_node})"

class ConstDecl(AST):
    def __init__(self, type_node, var_node, assign_node): self.type_node = type_node; self.var_node = var_node; self.assign_node = assign_node
    def __repr__(self): return f"  ConstDecl(const {self.type_node.value} {self.var_node.value} = {self.assign_node})"

class IfExpr(AST):
    """Represents an if-else expression."""
    def __init__(self, condition, if_block, else_block):
        self.condition = condition
        self.if_block = if_block
        self.else_block = else_block # For now, else is mandatory for if-expressions
    def __repr__(self): return f"IfExpr(condition={self.condition}, then={self.if_block}, else={self.else_block})"

class WhileStmt(AST):
    """Represents a while statement."""
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    def __repr__(self): return f"    WhileStmt(condition={self.condition}, body={self.body})"

class Type(AST):
    def __init__(self, token): self.token = token; self.value = token.value
    def __repr__(self): return f"Type(value='{self.value}')"

class Assign(AST):
    def __init__(self, left, op, right): self.left = left; self.op = op; self.right = right
    def __repr__(self): return f"    Assign({self.left.value} = {self.right})"

class Var(AST):
    def __init__(self, token): self.token = token; self.value = token.value
    def __repr__(self): return f"Var(name='{self.value}')"

class Num(AST):
    def __init__(self, token): self.token = token; self.value = token.value
    def __repr__(self): return f"Num(value={self.value})"

class BinOp(AST):
    def __init__(self, left, op, right): self.left = left; self.op = op; self.right = right
    def __repr__(self): return f"BinOp(left={self.left}, op='{self.op.value}', right={self.right})"

class FunctionCall(AST):
    def __init__(self, name, args): self.name = name; self.args = args
    def __repr__(self): return f"    FunctionCall(name='{self.name}', args={self.args})"

class Block(AST):
    def __init__(self): self.children = []
    def __repr__(self): children_repr = '\n'.join(map(repr, self.children)); indented_children = "      " + children_repr.replace("\n", "\n      "); return f"Block([\n{indented_children}\n    ])"

class Return(AST):
    def __init__(self, value): self.value = value
    def __repr__(self): return f"    Return(value={self.value})"

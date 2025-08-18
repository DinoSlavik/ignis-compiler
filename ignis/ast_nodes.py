class AST: pass
class Program(AST):
    def __init__(self, declarations): self.declarations = declarations
    def __repr__(self): return f"Program(\n{', '.join(map(repr, self.declarations))}\n)"
class FunctionDecl(AST):
    def __init__(self, type_node, func_name, body): self.type_node, self.func_name, self.body = type_node, func_name, body
    def __repr__(self): return f"  FunctionDecl(name='{self.func_name}', body={self.body})"
class VarDecl(AST):
    def __init__(self, type_node, var_node, assign_node, is_mutable): self.type_node, self.var_node, self.assign_node, self.is_mutable = type_node, var_node, assign_node, is_mutable
    def __repr__(self): mut_str = 'mut ' if self.is_mutable else ''; return f"    VarDecl({self.type_node} {self.var_node.value} = {self.assign_node})"
class ConstDecl(AST):
    def __init__(self, type_node, var_node, assign_node): self.type_node, self.var_node, self.assign_node = type_node, var_node, assign_node
    def __repr__(self): return f"  ConstDecl(const {self.type_node} {self.var_node.value} = {self.assign_node})"
class IfExpr(AST):
    def __init__(self, condition, if_block, else_block): self.condition, self.if_block, self.else_block = condition, if_block, else_block
    def __repr__(self): return f"IfExpr(condition={self.condition}, then={self.if_block}, else={self.else_block})"
class WhileStmt(AST):
    def __init__(self, condition, body): self.condition, self.body = condition, body
    def __repr__(self): return f"    WhileStmt(condition={self.condition}, body={self.body})"
class LoopStmt(AST):
    def __init__(self, body): self.body = body
    def __repr__(self): return f"    LoopStmt(body={self.body})"
class ForStmt(AST):
    def __init__(self, init, condition, increment, body): self.init, self.condition, self.increment, self.body = init, condition, increment, body
    def __repr__(self): return f"    ForStmt(init={self.init}, cond={self.condition}, inc={self.increment}, body={self.body})"
class BreakStmt(AST):
    def __repr__(self): return "    BreakStmt"
class ContinueStmt(AST):
    def __repr__(self): return "    ContinueStmt"
class Type(AST):
    def __init__(self, token, pointer_level=0):
        self.token = token
        self.value = token.value
        self.pointer_level = pointer_level
    def __repr__(self):
        return f"{'ptr ' * self.pointer_level}{self.value}"
class Assign(AST):
    def __init__(self, left, op, right): self.left, self.op, self.right = left, op, right
    def __repr__(self):
        # Handle assignment to dereferenced pointer
        left_repr = f"deref {self.left.expr}" if isinstance(self.left, UnaryOp) and self.left.op.type == TokenType.KW_DEREF else self.left.value
        return f"    Assign({left_repr} = {self.right})"
class Var(AST):
    def __init__(self, token): self.token, self.value = token, token.value
    def __repr__(self): return f"Var(name='{self.value}')"
class Num(AST):
    def __init__(self, token): self.token, self.value = token, token.value
    def __repr__(self): return f"Num(value={self.value})"
class BinOp(AST):
    def __init__(self, left, op, right): self.left, self.op, self.right = left, op, right
    def __repr__(self): return f"BinOp(left={self.left}, op='{self.op.value}', right={self.right})"
class UnaryOp(AST):
    def __init__(self, op, expr): self.op, self.expr = op, expr
    def __repr__(self): return f"UnaryOp(op='{self.op.value}', expr={self.expr})"
class FunctionCall(AST):
    def __init__(self, name, args): self.name, self.args = name, args
    def __repr__(self): return f"    FunctionCall(name='{self.name}', args={self.args})"
class Block(AST):
    def __init__(self): self.children = []
    def __repr__(self): children_repr = '\n'.join(map(repr, self.children)); indented_children = "      " + children_repr.replace("\n", "\n      "); return f"Block([\n{indented_children}\n    ])"
class Return(AST):
    def __init__(self, value): self.value = value
    def __repr__(self): return f"    Return(value={self.value})"

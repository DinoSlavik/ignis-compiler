from lexer import TokenType

class AST: pass
class Program(AST):
    def __init__(self, declarations): self.declarations = declarations
    def __repr__(self): return f"Program(\n{', '.join(map(repr, self.declarations))}\n)"
class FunctionDecl(AST):
    def __init__(self, type_node, func_name, params, body): self.type_node, self.func_name, self.params, self.body = type_node, func_name, params, body
    def __repr__(self): return f"  FunctionDecl(name='{self.func_name}', params={self.params}, body={self.body})"
class StructDef(AST):
    def __init__(self, name, fields): self.name, self.fields = name, fields
    def __repr__(self): return f"  StructDef(name='{self.name}', fields={self.fields})"
class Param(AST):
    def __init__(self, type_node, var_node): self.type_node, self.var_node = type_node, var_node
    def __repr__(self): return f"Param({self.type_node}, {self.var_node.value})"
class Field(AST):
    def __init__(self, type_node, var_node): self.type_node, self.var_node = type_node, var_node
    def __repr__(self): return f"Field({self.type_node}, {self.var_node.value})"
class MemberAccess(AST):
    def __init__(self, left, right): self.left, self.right = left, right
    def __repr__(self): return f"MemberAccess({self.left}, '{self.right.value}')"
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
        self.token, self.value, self.pointer_level = token, token.value if token else "struct", pointer_level
    def __repr__(self): return f"{'ptr ' * self.pointer_level}{self.value}"
    def __eq__(self, other):
        if type(other) == type(self):
            return self.value == other.value and self.pointer_level == other.pointer_level
        else:
            raise NotImplementedError
class Assign(AST):
    def __init__(self, left, op, right): self.left, self.op, self.right = left, op, right
    def __repr__(self):
        left_repr = self.left
        if isinstance(self.left, UnaryOp) and self.left.op.type == TokenType.KW_DEREF: left_repr = f"deref {self.left.expr}"
        elif isinstance(self.left, Var): left_repr = self.left.value
        return f"    Assign({left_repr} = {self.right})"
class Var(AST):
    def __init__(self, token): self.token, self.value = token, token.value
    def __repr__(self): return f"Var(name='{self.value}')"
class Num(AST):
    def __init__(self, token): self.token, self.value = token, token.value
    def __repr__(self): return f"Num(value={self.value})"
class CharLiteral(AST):
    def __init__(self, token): self.token, self.value = token, token.value
    def __repr__(self): return f"Char(value={self.value})"
class StringLiteral(AST):
    def __init__(self, token): self.token, self.value = token, token.value
    def __repr__(self): return f"String(value='{self.value}')"
class BinOp(AST):
    def __init__(self, left, op, right): self.left, self.op, self.right = left, op, right
    def __repr__(self): return f"BinOp(left={self.left}, op='{self.op.value}', right={self.right})"
class UnaryOp(AST):
    def __init__(self, op, expr): self.op, self.expr = op, expr
    def __repr__(self): return f"UnaryOp(op='{self.op.value}', expr={self.expr})"
class FunctionCall(AST):
    def __init__(self, name_node, args): self.name_node, self.args = name_node, args
    def __repr__(self): return f"    FunctionCall(name='{self.name_node.value}', args={self.args})"
class Block(AST):
    def __init__(self): self.children = []
    def __repr__(self): children_repr = '\n'.join(map(repr, self.children)); indented_children = "      " + children_repr.replace("\n", "\n      "); return f"Block([\n{indented_children}\n    ])"
class Return(AST):
    def __init__(self, value): self.value = value
    def __repr__(self): return f"    Return(value={self.value})"
class Alloc(AST):
    def __init__(self, size_expr): self.size_expr = size_expr
    def __repr__(self): return f"Alloc(size={self.size_expr})"
class New(AST):
    def __init__(self, type_node): self.type_node = type_node
    def __repr__(self): return f"New(type_node={self.type_node})"
class Free(AST):
    def __init__(self, expr): self.expr = expr
    def __repr__(self): return f"Free(expr={self.expr})"
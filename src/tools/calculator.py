import ast, operator as op
_ops={ast.Add:op.add, ast.Sub:op.sub, ast.Mult:op.mul, ast.Div:op.truediv, ast.Pow:op.pow, ast.USub:op.neg}
def _eval(n):
    if isinstance(n, ast.Constant): return n.value
    if isinstance(n, ast.Num): return n.n
    if isinstance(n, ast.BinOp): return _ops[type(n.op)](_eval(n.left), _eval(n.right))
    if isinstance(n, ast.UnaryOp): return _ops[type(n.op)](_eval(n.operand))
    raise ValueError("unsupported")
def calculate(expression: str) -> str:
    try: return str(_eval(ast.parse(expression, mode="eval").body))
    except Exception as e: return f"error: {e}"

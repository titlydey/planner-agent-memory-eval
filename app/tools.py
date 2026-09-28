import ast, operator as op

_OPS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv, ast.USub: op.neg}

def calculate(expression):
    """Safe arithmetic: parses the AST and allows only numbers and + - * /."""
    if len(expression) > 100:
        raise ValueError("expression too long")
    def ev(n):
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in _OPS:
            return _OPS[type(n.op)](ev(n.left), ev(n.right))
        if isinstance(n, ast.UnaryOp) and type(n.op) in _OPS:
            return _OPS[type(n.op)](ev(n.operand))
        raise ValueError("unsupported expression")
    return ev(ast.parse(expression, mode="eval").body)

_F = {("km", "miles"): 0.621371, ("miles", "km"): 1.609344, ("kg", "lb"): 2.204623, ("lb", "kg"): 0.453592}

def convert(value, **kw):
    a, b = kw["from"].lower(), kw["to"].lower()
    if (a, b) == ("c", "f"):
        return value * 9 / 5 + 32
    if (a, b) == ("f", "c"):
        return (value - 32) * 5 / 9
    if (a, b) in _F:
        return round(value * _F[(a, b)], 4)
    raise ValueError(f"unsupported conversion {a}->{b}")

_GLOSSARY = {"agent": "An LLM-driven program that plans and calls tools to reach a goal.",
             "rag": "Retrieval-augmented generation: fetch relevant documents, then answer from them.",
             "embedding": "A numeric vector that represents the meaning of text.",
             "guardrail": "A check that blocks or filters unsafe inputs and outputs."}

def define(term):
    return _GLOSSARY.get(term.lower(), "unknown term")

TOOLS = {"calculate": calculate, "convert": convert, "define": define}

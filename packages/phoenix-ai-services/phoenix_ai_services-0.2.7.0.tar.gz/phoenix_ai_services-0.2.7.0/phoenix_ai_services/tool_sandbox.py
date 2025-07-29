import math


def safe_eval(expr: str):
    allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
    allowed_names["abs"] = abs
    allowed_names["round"] = round

    code = compile(expr, "<string>", "eval")
    return eval(code, {"__builtins__": {}}, allowed_names)

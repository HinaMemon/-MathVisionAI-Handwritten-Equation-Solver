# parser_solver.py
from sympy import Eq, solve, sympify, diff, Symbol
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
import re

transformations = (standard_transformations + (implicit_multiplication_application,))

STOPWORDS = ["solve", "solue", "find", "calculate", "equation", "result"]


def clean_expression(text: str) -> str:
    lower = text.lower()

    # Remove stopwords
    for word in STOPWORDS:
        lower = lower.replace(word, "")

    # Replace common OCR mistakes
    lower = lower.replace("×", "*")
    lower = lower.replace("^", "**")  # convert ^ to python power
    lower = lower.replace(":", "/")

    # Remove extra spaces
    lower = re.sub(r"\s+", "", lower)
    return lower.strip()


def solve_math_expression(text: str):
    expr = clean_expression(text)
    try:
        # Handle derivatives: look for "d/dx" pattern
        if "d/dx" in expr:
            match = re.search(r"d/dx\(?([^)]+)\)?", expr)
            if match:
                inner_expr = match.group(1)
                x = Symbol("x")
                inner = parse_expr(inner_expr, transformations=transformations)
                result = diff(inner, x)
                return f"Derivative wrt x: {result}"

        # Handle equations
        if "=" in expr:
            left, right = expr.split("=", 1)
            left_expr = parse_expr(left, transformations=transformations)
            right_expr = parse_expr(right, transformations=transformations)
            var = list(left_expr.free_symbols | right_expr.free_symbols)
            if var:
                sol = solve(Eq(left_expr, right_expr), var[0])
                return f"{var[0]} = {sol}"
            else:
                return f"Equation result: {left_expr.equals(right_expr)}"
        else:
            # Just evaluate expression
            result = sympify(expr).evalf()
            return f"Result: {result}"
    except Exception as e:
        return f"Error solving expression: {e}\n(OCR gave: {expr})"



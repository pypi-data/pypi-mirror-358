import re
import math
import string

# === Helper ===

def evaluate_expr(expr, values=None):
    expr = expr.replace('^', '**')
    if values:
        for k, v in values.items():
            expr = expr.replace(k, str(v))
    return eval(expr)

# === Simplifier ===

def simplify_expression(expr):
    expr = expr.replace('-', '+-')
    terms = expr.split('+')
    x_coeff, constant = 0.0, 0.0
    for term in terms:
        term = term.strip()
        if not term:
            continue
        if 'x' in term:
            coeff = term.replace('x', '')
            if coeff in ['', '+']:
                coeff = 1
            elif coeff == '-':
                coeff = -1
            x_coeff += float(coeff)
        else:
            constant += float(term)
    result = ""
    if abs(x_coeff) > 1e-12:
        result += f"{x_coeff}x"
    if abs(constant) > 1e-12:
        if constant > 0 and result:
            result += f" + {constant}"
        else:
            result += f"{constant}"
    return result or "0"

# === Single Equation ===

def parse_equation(equation):
    if "=" not in equation:
        raise ValueError("Equation must contain '='")
    return equation.split("=")

def is_quadratic(expr):
    return 'x^2' in expr or 'x²' in expr

def extract_terms(expr, var="x"):
    expr = expr.replace('-', '+-')
    terms = expr.split('+')
    coeff, const = 0.0, 0.0
    for t in terms:
        t = t.strip()
        if not t:
            continue
        if var in t:
            t = t.replace(var, '')
            if t in ['', '+']:
                coeff += 1
            elif t == '-':
                coeff -= 1
            else:
                coeff += float(t)
        else:
            const += float(t)
    return coeff, const

def solve_linear(equation):
    lhs, rhs = parse_equation(equation)
    a1, b1 = extract_terms(lhs)
    a2, b2 = extract_terms(rhs)
    a = a1 - a2
    b = b2 - b1
    if abs(a) < 1e-12:
        if abs(b) < 1e-12:
            return "Infinite solutions"
        else:
            return "No solution"
    return b / a

def solve_quadratic(equation):
    lhs, rhs = parse_equation(equation)
    if rhs.strip() != "0":
        raise ValueError("Quadratic equations must be in the form ax^2 + bx + c = 0")
    lhs = lhs.replace('-', '+-')
    terms = lhs.split('+')
    a = b = c = 0.0
    for t in terms:
        t = t.strip()
        if 'x^2' in t or 'x²' in t:
            coeff = t.replace('x^2', '').replace('x²', '')
            a += float(coeff or '1')
        elif 'x' in t:
            coeff = t.replace('x', '')
            b += float(coeff or '1')
        elif t:
            c += float(t)
    D = b**2 - 4*a*c
    if D < 0:
        return "No real solution"
    elif D == 0:
        return -b / (2*a)
    else:
        sqrt_D = math.sqrt(D)
        x1 = (-b + sqrt_D) / (2*a)
        x2 = (-b - sqrt_D) / (2*a)
        return (x1, x2)

def solve(input_str):
    input_str = input_str.replace(" ", "")
    if "=" in input_str:
        if is_quadratic(input_str):
            return solve_quadratic(input_str)
        else:
            return solve_linear(input_str)
    else:
        return simplify_expression(input_str)

# === Two Equations System ===

def parse_expression_side(expr):
    expr = expr.replace('-', '+-')
    expr = expr.replace(' ', '')
    terms = expr.split('+')
    coeffs = {v: 0.0 for v in string.ascii_lowercase}
    constant = 0.0

    for t in terms:
        if not t:
            continue

        matched = False
        for var in string.ascii_lowercase:
            if var in t:
                matched = True
                if t == var:
                    coeffs[var] += 1.0
                elif t == '-' + var:
                    coeffs[var] -= 1.0
                else:
                    expr_with_1 = t.replace(var, '(1)')
                    coeffs[var] += evaluate_expr(expr_with_1)
                break
        if not matched:
            constant += evaluate_expr(t)

    return coeffs, constant

def parse_system_equation(eq):
    lhs, rhs = eq.split('=')
    coeffs_lhs, const_lhs = parse_expression_side(lhs)
    coeffs_rhs, const_rhs = parse_expression_side(rhs)

    all_vars = set(coeffs_lhs) | set(coeffs_rhs)
    a_var, b_var = sorted([v for v in all_vars if (coeffs_lhs[v] - coeffs_rhs[v]) != 0])[:2]

    a = coeffs_lhs[a_var] - coeffs_rhs[a_var]
    b = coeffs_lhs[b_var] - coeffs_rhs[b_var]
    c = const_rhs - const_lhs
    return a, b, c, a_var, b_var

def solve_system(eq1, eq2):
    a1, b1, c1, var1, var2 = parse_system_equation(eq1)
    a2, b2, c2, _, _ = parse_system_equation(eq2)

    det = a1 * b2 - a2 * b1
    if abs(det) < 1e-12:
        return "No unique solution"

    dx = c1 * b2 - c2 * b1
    dy = a1 * c2 - a2 * c1

    val1 = dx / det
    val2 = dy / det

    return {var1: val1, var2: val2}


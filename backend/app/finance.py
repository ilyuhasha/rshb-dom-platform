"""Финансовый движок симулятора «Что, если...?» (Задача 1).

Центральные формулы аннуитетной ипотеки:
  payment = S * i * (1+i)^n / ((1+i)^n - 1),  где i = rate/12/100
  n = log(pmt/(pmt - S*i)) / log(1+i)          (срок при известном платеже)
"""
import ast
import math
import re
import operator as op

_ALLOWED_BIN = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
                ast.Div: op.truediv, ast.Pow: op.pow, ast.Mod: op.mod,
                ast.FloorDiv: op.floordiv}
_ALLOWED_CMP = {ast.Lt: op.lt, ast.LtE: op.le, ast.Gt: op.gt,
                ast.GtE: op.ge, ast.Eq: op.eq, ast.NotEq: op.ne}
_ALLOWED_UNARY = {ast.USub: op.neg, ast.UAdd: op.pos, ast.Not: op.not_}

_SAFE_FUNCS = {
    "min": min, "max": max, "abs": abs, "round": round,
    "log": math.log, "log10": math.log10, "sqrt": math.sqrt,
    "pow": pow, "ceil": math.ceil, "floor": math.floor,
    "if": lambda cond, a, b: a if cond else b,
    "annual_share": lambda months: months / 12.0,
}


def safe_eval(expr: str, variables: dict) -> float:
    """Безопасное вычисление арифметического выражения.

    Поддерживаются: числа, +,-,*,/,**,%, сравнения, скобки,
    тернарный оператор (x if cond else y), вызов min/max/abs/round/
    log/sqrt/annuity/months_to_repay и переменные из словаря.
    Никакого доступа к Python-окружению — только AST-интерпретация.
    """
    expr = expr.strip()
    # Удобная короткая форма if(cond, a, b) -> (a if cond else b)
    m = re.match(r'^if\((.+)\)$', expr)
    if m:
        parts = _split_args(m.group(1))
        if len(parts) == 3:
            expr = f"({parts[1]} if ({parts[0]}) else ({parts[2]}))"
    try:
        tree = ast.parse(expr, mode="eval")
        return float(_eval_node(tree.body, variables))
    except ZeroDivisionError:
        return 0.0
    except Exception:
        raise ValueError(f"Не удалось вычислить выражение: {expr}")


def _split_args(s: str) -> list:
    """Разбивает аргументы функции по запятым верхнего уровня."""
    out, depth, cur = [], 0, []
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    out.append("".join(cur).strip())
    return out


def _eval_node(node, variables):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name):
        if node.id in variables:
            return variables[node.id]
        if node.id in ("True", "False"):
            return node.id == "True"
        raise ValueError(f"Неизвестная переменная: {node.id}")
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BIN:
        return _ALLOWED_BIN[type(node.op)](
            _eval_node(node.left, variables), _eval_node(node.right, variables))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY:
        return _ALLOWED_UNARY[type(node.op)](_eval_node(node.operand, variables))
    if isinstance(node, ast.Compare) and type(node.ops[0]) in _ALLOWED_CMP:
        left = _eval_node(node.left, variables)
        for cmp_op, comparator in zip(node.ops, node.comparators):
            fn = _ALLOWED_CMP[type(cmp_op)]
            right = _eval_node(comparator, variables)
            if not fn(left, right):
                return False
            left = right
        return True
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        fname = node.func.id
        # Функция может быть передана в словаре переменных (annuity и др.)
        if fname in variables and callable(variables[fname]):
            args = [_eval_node(a, variables) for a in node.args]
            return variables[fname](*args)
        if fname in _SAFE_FUNCS:
            args = [_eval_node(a, variables) for a in node.args]
            return _SAFE_FUNCS[fname](*args)
        raise ValueError(f"Функция недоступна: {fname}")
    if isinstance(node, ast.IfExp):
        cond = _eval_node(node.test, variables)
        return _eval_node(node.body if cond else node.orelse, variables)
    raise ValueError(f"Недопустимая конструкция в формуле: {type(node).__name__}")


# ---------- Стандартные финансовые функции для формул ----------

def annuity_payment(principal: float, annual_rate_pct: float, months: int) -> float:
    """Аннуитетный платёж."""
    i = annual_rate_pct / 100 / 12
    if months <= 0:
        return 0.0
    if i == 0:
        return principal / months
    k = (1 + i) ** months
    return principal * i * k / (k - 1)


def months_to_repay(principal: float, annual_rate_pct: float,
                    payment: float) -> float:
    """Число месяцев для погашения суммы при данном платеже (аннуитет).

    Если платежа не хватает даже на проценты — долг не гасится никогда:
    возвращаем большой конечный срок (600 лет) вместо inf, чтобы
    результат оставался JSON-сериализуемым, а пользователь видел
    нереалистичность ввода по огромному сроку.
    """
    i = annual_rate_pct / 100 / 12
    if payment <= 0 or principal <= 0:
        return 0.0
    if payment <= principal * i:
        return 7200.0  # 600 лет — маркер «платёж не покрывает проценты»
    if i == 0:
        return principal / payment
    return math.log(payment / (payment - principal * i)) / math.log(1 + i)


def total_paid(payment: float, months: float) -> float:
    return payment * months


def overpay(principal: float, payment: float, months: float) -> float:
    return payment * months - principal


def reduce_term_effect(principal: float, rate: float, payment: float,
                       prepay: float) -> dict:
    """Досрочный платёж: сокращение срока при том же платеже."""
    new_principal = max(0.0, principal - prepay)
    return {
        "new_debt": new_principal,
        "new_months": months_to_repay(new_principal, rate, payment),
    }


def reduce_payment_effect(principal: float, rate: float, months_left: int,
                          prepay: float) -> dict:
    """Досрочный платёж: снижение платежа при том же сроке."""
    new_principal = max(0.0, principal - prepay)
    return {
        "new_debt": new_principal,
        "new_payment": annuity_payment(new_principal, rate, months_left),
    }


def rental_income(rent: float, months: float,
                  vacancy_pct: float = 0, management_pct: float = 0,
                  tax_pct: float = 4) -> float:
    """Доход от аренды за период с учётом простоя, управления и налога (НПД 4%)."""
    eff = rent * (1 - vacancy_pct / 100)
    eff = eff - rent * management_pct / 100
    return eff * (1 - tax_pct / 100) * months


def tax_deduction(property_cost: float, interest_paid: float = 0,
                  cap_prop: float = 2_000_000, cap_int: float = 3_000_000) -> dict:
    """Имущественный налоговый вычет (13%): с покупки (до 2 млн) и с процентов (до 3 млн)."""
    prop_base = min(property_cost, cap_prop)
    int_base = min(interest_paid, cap_int)
    return {
        "deduction_property": prop_base * 0.13,
        "deduction_interest": int_base * 0.13,
        "deduction_total": (prop_base + int_base) * 0.13,
    }


def budget_available(income: float, other_expenses: float,
                     payment: float) -> float:
    return income - other_expenses - payment

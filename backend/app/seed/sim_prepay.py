"""Сценарий 2: Досрочное погашение."""

SCENARIO = {
    "key": "prepay",
    "title": "Досрочное погашение",
    "description": "Как досрочный платёж меняет срок и сколько процентов вы сэкономите.",
    "category": "Ипотека",
    "icon": "⚡",
    "sort": 20,
    "params_schema": [
        {"key": "balance", "label": "Остаток долга", "unit": "₽", "type": "number", "default": 4800000, "min": 30000, "max": 100000000, "step": 50000},
        {"key": "rate", "label": "Ставка", "unit": "% в год", "type": "number", "default": 14, "min": 0.1, "max": 40, "step": 0.1},
        {"key": "payment", "label": "Текущий платёж", "unit": "₽/мес.", "type": "number", "default": 61000, "min": 1000, "max": 2000000, "step": 1000},
        {"key": "prepay", "label": "Досрочный платёж", "unit": "₽", "type": "number", "default": 500000, "min": 0, "max": 100000000, "step": 50000},
    ],
    "formulas": [
        {"key": "months_before", "label": "Срок был", "expr": "months_to_repay(balance, rate, payment)", "unit": "мес."},
        {"key": "overpay_before", "label": "Проценты были бы", "expr": "payment * months_before - balance", "unit": "₽", "hidden": True},
        {"key": "new_balance", "label": "Долг после взноса", "expr": "balance - prepay", "unit": "₽"},
        {"key": "months_after", "label": "Срок стал (платёж тот же)", "expr": "months_to_repay(new_balance, rate, payment)", "unit": "мес."},
        {"key": "overpay_after", "label": "Проценты станут", "expr": "payment * months_after - new_balance", "unit": "₽", "hidden": True},
        {"key": "saved_interest", "label": "Экономия на процентах", "expr": "overpay_before - overpay_after", "unit": "₽"},
        {"key": "months_saved", "label": "Срок короче на", "expr": "months_before - months_after", "unit": "мес."},
    ],
    "hints": [
        {"title": "Сокращайте срок, а не платёж", "text": "При одинаковой сумме взноса сокращение срока даёт большую экономию процентов, чем снижение платежа.", "condition": ""},
        {"title": "Вносите в дату платежа", "text": "Досрочный взнос в дату очередного платежа минимизирует проценты, начисленные за месяц.", "condition": ""},
    ],
}

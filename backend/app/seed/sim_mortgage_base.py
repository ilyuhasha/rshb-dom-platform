"""Сценарий 1: Базовый ипотечный расчёт."""

SCENARIO = {
    "key": "mortgage_base",
    "title": "Базовый ипотечный расчёт",
    "description": "Аннуитетный платёж, переплата и долговая нагрузка по классической ипотеке РСХБ.",
    "category": "Ипотека",
    "icon": "🏦",
    "sort": 10,
    "params_schema": [
        {"key": "price", "label": "Стоимость объекта", "unit": "₽", "type": "number", "default": 6500000, "min": 300000, "max": 100000000, "step": 50000},
        {"key": "down", "label": "Первоначальный взнос", "unit": "₽", "type": "number", "default": 1300000, "min": 0, "max": 100000000, "step": 50000},
        {"key": "rate", "label": "Ставка", "unit": "% в год", "type": "number", "default": 16, "min": 0.1, "max": 40, "step": 0.1},
        {"key": "years", "label": "Срок кредита", "unit": "лет", "type": "number", "default": 25, "min": 1, "max": 35, "step": 1},
        {"key": "income", "label": "Доход семьи", "unit": "₽/мес.", "type": "number", "default": 180000, "min": 0, "max": 10000000, "step": 10000, "optional": True},
    ],
    "formulas": [
        {"key": "loan", "label": "Сумма кредита", "expr": "price - down", "unit": "₽"},
        {"key": "months", "label": "Срок в месяцах", "expr": "years * 12", "unit": "мес."},
        {"key": "payment", "label": "Ежемесячный платёж", "expr": "annuity(loan, rate, months)", "unit": "₽/мес."},
        {"key": "total", "label": "Всего выплат банку", "expr": "payment * months", "unit": "₽"},
        {"key": "overpay", "label": "Переплата (проценты)", "expr": "total - loan", "unit": "₽"},
        {"key": "overpay_pct", "label": "Переплата в % от кредита", "expr": "overpay / loan * 100", "unit": "%"},
        {"key": "dti", "label": "Долговая нагрузка", "expr": "if(income > 0, payment / income * 100, 0)", "unit": "%"},
    ],
    "hints": [
        {"title": "Взнос 20%+ снижает ставку", "text": "При первоначальном взносе от 20% стоимости банки, включая РСХБ, предлагают сниженную ставку и выше шанс одобрения.", "condition": "down / price < 0.2"},
        {"title": "Платёж не выше 40% дохода", "text": "Safe-уровень долговой нагрузки — до 40% дохода семьи. Проверьте показатель ДТИ после расчёта.", "condition": "payment / income > 0.4"},
    ],
}

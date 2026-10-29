"""Сценарий 4: Сдача квартиры в аренду."""

SCENARIO = {
    "key": "rent_out",
    "title": "Сдача квартиры в аренду",
    "description": "Платёж по ипотеке против дохода от аренды: cashflow, окупаемость и налог НПД 4%.",
    "category": "Инвестиции",
    "icon": "🔑",
    "sort": 40,
    "params_schema": [
        {"key": "price", "label": "Стоимость квартиры", "unit": "₽", "type": "number", "default": 7000000, "min": 300000, "max": 100000000, "step": 100000},
        {"key": "down", "label": "Первоначальный взнос", "unit": "₽", "type": "number", "default": 1400000, "min": 0, "max": 100000000, "step": 50000},
        {"key": "rent", "label": "Аренда в месяц", "unit": "₽/мес.", "type": "number", "default": 35000, "min": 5000, "max": 500000, "step": 1000},
        {"key": "rate", "label": "Ставка", "unit": "% в год", "type": "number", "default": 16, "min": 0.1, "max": 40, "step": 0.1},
        {"key": "years", "label": "Срок ипотеки", "unit": "лет",  "type": "number", "default": 25, "min": 1, "max": 35, "step": 1},
        {"key": "vacancy", "label": "Простой (мес. в год)", "unit": "мес.", "type": "number", "default": 1, "min": 0, "max": 6, "step": 1},
    ],
    "formulas": [
        {"key": "loan", "label": "Сумма кредита", "expr": "price - down", "unit": "₽", "hidden": True},
        {"key": "payment", "label": "Платёж по ипотеке", "expr": "annuity(loan, rate, years * 12)", "unit": "₽/мес."},
        {"key": "effective_rent", "label": "Доход с учётом простоя и НПД 4%", "expr": "rent * (12 - vacancy) / 12 * 0.96", "unit": "₽/мес."},
        {"key": "cashflow", "label": "Cashflow в месяц", "expr": "effective_rent - payment", "unit": "₽/мес."},
        {"key": "payback_years", "label": "Окупаемость объекта", "expr": "if(effective_rent > 0, price / (effective_rent * 12), 0)", "unit": "лет"},
        {"key": "yield_pct", "label": "Доходность (кап. ставка)", "expr": "if(price > 0, effective_rent * 12 / price * 100, 0)", "unit": "%"},
    ],
    "hints": [
        {"title": "Проверьте законность", "text": "Если квартира в ипотеке, сдача в аренду требует согласия банка. В РСХБ согласие оформляется заявлением — бесплатно.", "condition": ""},
        {"title": "НПД 4% — ваш налог", "text": "Самозанятость (налог на проф. доход 4%) легализует доход от аренды и даёт чеки квартирантам.", "condition": ""},
    ],
}

"""Сценарий 6: Сельская ипотека 3%."""

SCENARIO = {
    "key": "rural_mortgage",
    "title": "Сельская ипотека 3%",
    "description": "Льготная ставка 3% на дом в сельской местности: платёж и экономия против рыночной ставки.",
    "category": "Ипотека",
    "icon": "🌾",
    "sort": 60,
    "params_schema": [
        {"key": "price", "label": "Стоимость дома", "unit": "₽", "type": "number", "default": 4500000, "min": 300000, "max": 12000000, "step": 50000},
        {"key": "down", "label": "Первоначальный взнос (от 10%)", "unit": "₽", "type": "number", "default": 450000, "min": 0, "max": 12000000, "step": 50000},
        {"key": "rural_rate", "label": "Ставка сельской ипотеки", "unit": "% в год", "type": "number", "default": 3, "min": 0.1, "max": 10, "step": 0.1},
        {"key": "market_rate", "label": "Рыночная ставка для сравнения", "unit": "% в год", "type": "number", "default": 16, "min": 0.1, "max": 40, "step": 0.1},
        {"key": "years", "label": "Срок", "unit": "лет", "type": "number", "default": 25, "min": 1, "max": 30, "step": 1},
    ],
    "formulas": [
        {"key": "loan", "label": "Сумма кредита", "expr": "price - down", "unit": "₽"},
        {"key": "months", "label": "Срок в месяцах", "expr": "years * 12", "unit": "мес.", "hidden": True},
        {"key": "payment_rural", "label": "Платёж по сельской ставке", "expr": "annuity(loan, rural_rate, months)", "unit": "₽/мес."},
        {"key": "payment_market", "label": "Платёж по рыночной ставке", "expr": "annuity(loan, market_rate, months)", "unit": "₽/мес."},
        {"key": "month_saved", "label": "Экономия в месяц", "expr": "payment_market - payment_rural", "unit": "₽/мес."},
        {"key": "total_saved", "label": "Экономия за весь срок", "expr": "payment_market * months - payment_rural * months", "unit": "₽"},
        {"key": "overpay_rural", "label": "Переплата по сельской ставке", "expr": "payment_rural * months - loan", "unit": "₽"},
    ],
    "hints": [
        {"title": "Лимит программы", "text": "Сельская ипотека: до 5 млн ₽ (ДФО — до 6 млн) на дом или участок под ИЖС в сельской территории, участвующей в программе.", "condition": "loan > 5000000"},
        {"title": "Проверьте населённый пункт", "text": "Объект должен находиться на территории, включённой в программу «Комплексное развитие сельских территорий». Список — в навигаторе, шаг «Финансы».", "condition": ""},
    ],
}

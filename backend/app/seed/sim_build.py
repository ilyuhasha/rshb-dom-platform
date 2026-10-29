"""Сценарий 5: Строительство дома."""

SCENARIO = {
    "key": "build_house",
    "title": "Строительство дома",
    "description": "Кредит на строительство: транши, платёж на период стройки и после ввода дома.",
    "category": "Строительство",
    "icon": "🏗",
    "sort": 50,
    "params_schema": [
        {"key": "land_cost", "label": "Стоимость участка", "unit": "₽", "type": "number", "default": 1200000, "min": 0, "max": 50000000, "step": 50000},
        {"key": "build_cost", "label": "Смета строительства", "unit": "₽", "type": "number", "default": 5000000, "min": 300000, "max": 100000000, "step": 100000},
        {"key": "own_funds", "label": "Свои средства", "unit": "₽", "type": "number", "default": 1500000, "min": 0, "max": 100000000, "step": 50000},
        {"key": "rate", "label": "Ставка на период стройки", "unit": "% в год", "type": "number", "default": 17, "min": 0.1, "max": 40, "step": 0.1},
        {"key": "build_years", "label": "Длительность стройки", "unit": "лет", "type": "number", "default": 2, "min": 1, "max": 5, "step": 1},
        {"key": "term_years", "label": "Срок кредита после ввода", "unit": "лет", "type": "number", "default": 20, "min": 1, "max": 35, "step": 1},
        {"key": "income", "label": "Доход семьи", "unit": "₽/мес.", "type": "number", "default": 200000, "min": 0, "max": 10000000, "step": 10000},
    ],
    "formulas": [
        {"key": "total_project", "label": "Весь проект (участок + дом)", "expr": "land_cost + build_cost", "unit": "₽"},
        {"key": "loan", "label": "Сумма кредита", "expr": "max(0, total_project - own_funds)", "unit": "₽"},
        {"key": "build_months", "label": "Стройка в месяцах", "expr": "build_years * 12", "unit": "мес.", "hidden": True},
        {"key": "tranche", "label": "Транш в месяц стройки", "expr": "if(build_months > 0, min(build_cost, loan) / build_months, 0)", "unit": "₽/мес."},
        {"key": "build_interest", "label": "Проценты за период стройки (примерно)", "expr": "loan * (rate / 100) * (build_years / 2)", "unit": "₽"},
        {"key": "debt_after_build", "label": "Долг после ввода дома", "expr": "loan + build_interest", "unit": "₽"},
        {"key": "payment_after", "label": "Платёж после ввода дома", "expr": "annuity(debt_after_build, rate, term_years * 12)", "unit": "₽/мес."},
        {"key": "dti", "label": "Долговая нагрузка после ввода", "expr": "if(income > 0, payment_after / income * 100, 0)", "unit": "%"},
    ],
    "hints": [
        {"title": "Транши вместо всей суммы", "text": "Кредит на строительство выдаётся траншами по мере стройки — проценты начисляются только на выданное. Это и показывает строка «Транш в месяц».", "condition": ""},
        {"title": "Сельская и семейная ипотека", "text": "Если дом строится в сельской местности, применяйте ставку сельской ипотеки от 3% — пересчитайте с меньшей ставкой.", "condition": "rate > 10"},
    ],
}

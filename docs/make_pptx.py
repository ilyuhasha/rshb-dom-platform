# -*- coding: utf-8 -*-
"""Генератор презентации «РСХБ · Путь к своему дому» (PPTX, 16:9)."""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

# ---- палитра РСХБ ----
GREEN = RGBColor(0x1E, 0x9E, 0x4A)       # основной зелёный
GREEN_DARK = RGBColor(0x0E, 0x3B, 0x2E)  # тёмно-зелёный фон
GREEN_MID = RGBColor(0x14, 0x5A, 0x3A)
LIGHT = RGBColor(0xF2, 0xF7, 0xF3)       # почти белый с зелёным оттенком
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GREY = RGBColor(0x5A, 0x6B, 0x5E)
YELLOW = RGBColor(0xFF, 0xC8, 0x3D)      # акцент (жёлтый РСХБ)
RED = RGBColor(0xE0, 0x4A, 0x3F)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]

def add_slide(bg=GREEN_DARK):
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = bg
    return s

def box(slide, x, y, w, h):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    return tb, tf

def para(tf, text, size=18, color=WHITE, bold=False, align=PP_ALIGN.LEFT,
         first=False, space_after=6, font="Calibri"):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_after = Pt(space_after)
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.color.rgb = color
    r.font.bold = bold
    r.font.name = font
    return p

def rect(slide, x, y, w, h, fill, line=None, radius=True):
    shp = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
        Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    if line:
        shp.line.color.rgb = line
        shp.line.width = Pt(1)
    else:
        shp.line.fill.background()
    shp.shadow.inherit = False
    return shp

def header(slide, title, subtitle=None, num=None):
    rect(slide, 0, 0, 13.333, 1.25, GREEN, radius=False)
    _, tf = box(slide, 0.5, 0.18, 10.5, 0.9)
    para(tf, title, 30, WHITE, bold=True, first=True, space_after=0)
    if subtitle:
        para(tf, subtitle, 14, RGBColor(0xD8, 0xF0, 0xDE), space_after=0)
    if num:
        _, tf2 = box(slide, 12.1, 0.3, 1.0, 0.6)
        para(tf2, num, 16, YELLOW, bold=True, align=PP_ALIGN.RIGHT, first=True, space_after=0)

def chip(slide, x, y, w, h, title, body, tcolor=GREEN, fill=LIGHT):
    rect(slide, x, y, w, h, fill)
    _, tf = box(slide, x + 0.15, y + 0.1, w - 0.3, h - 0.2)
    para(tf, title, 15, tcolor, bold=True, first=True, space_after=3)
    for line in body:
        para(tf, "• " + line, 12.5, GREY, space_after=2)

# ============ СЛАЙД 1: ТИТУЛ ============
s = add_slide()
rect(s, 0, 0, 13.333, 7.5, GREEN_DARK, radius=False)
# декоративные круги
for cx, cy, d, c in [(10.8, -1.2, 4.5, GREEN_MID), (11.9, 4.9, 3.8, GREEN), (-1.5, 5.2, 3.5, GREEN_MID)]:
    shp = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx), Inches(cy), Inches(d), Inches(d))
    shp.fill.solid(); shp.fill.fore_color.rgb = c; shp.line.fill.background()
    shp.shadow.inherit = False
rect(s, 0.9, 2.0, 0.12, 2.6, YELLOW, radius=False)
_, tf = box(s, 1.35, 1.75, 10.5, 3.2)
para(tf, "РСХБ · СВОЁ ЖИЛЬЁ", 20, YELLOW, bold=True, first=True, space_after=8)
para(tf, "Путь к своему дому", 54, WHITE, bold=True, space_after=8)
para(tf, "Цифровая платформа: три сервиса в одном приложении", 22, RGBColor(0xCF, 0xE8, 0xD6))
_, tf = box(s, 1.35, 5.3, 11, 1.6)
para(tf, "Стипендиальная программа РСХБ 2026–2027 · Направление «Информационные технологии»", 14, RGBColor(0xA8, 0xCC, 0xB2), first=True, space_after=4)
para(tf, "Задачи 1–3: симулятор «Что, если…?» · интерактивный навигатор · «Жизнь после ипотеки»", 14, RGBColor(0xA8, 0xCC, 0xB2))

# ============ СЛАЙД 2: О РЕШЕНИИ ============
s = add_slide(LIGHT)
header(s, "Одна платформа — три задачи конкурса", "Full-stack веб-приложение: фронтенд + бэкенд + PostgreSQL + Docker", "01")
cards = [
    (0.5, 1.7, "Задача 1 · Симулятор «Что, если…?»",
     ["6 финансовых сценариев", "Досрочка, ремонт, аренда, стройка, сельская ипотека", "Платёж, срок, переплата, бюджет — онлайн", "Формулы настраиваются администратором"]),
    (4.72, 1.7, "Задача 2 · Навигатор пути",
     ["7 адаптивных маршрутов клиента", "Квартира, дом, участок, стройка, ремонт, с/и, новостройка", "42 шага · 238 пунктов чек-листов", "Прогресс сохраняется на сервере"]),
    (8.94, 1.7, "Задача 3 · Жизнь после ипотеки",
     ["10 сервисов после оформления", "Досрочка, вычеты, справки, страхование", "Гость — демо-данные", "Клиент ЛК — банковский контур"]),
]
for x, y, t, body in cards:
    chip(s, x, y, 3.9, 3.3, t, body)
_, tf = box(s, 0.5, 5.35, 12.3, 1.4)
para(tf, "Технологии", 16, GREEN, bold=True, first=True)
para(tf, "Python · FastAPI · SQLAlchemy · PostgreSQL · Docker · REST API · SPA без сборки", 15, GREY)

# ============ СЛАЙД 3: АРХИТЕКТУРА ============
s = add_slide(LIGHT)
header(s, "Архитектура системы", "Классическая трёхслойная: клиент → API → данные", "02")
# слои
layers = [
    (1.6, "КЛИЕНТ", "frontend/index.html — SPA: 3 модуля-вкладки, fetch к REST API, без npm-сборки", GREEN),
    (3.05, "API · FastAPI", "3 роутера (sim / nav / life) · Pydantic-валидация · Swagger /docs · CORS", GREEN_MID),
    (4.5, "ДОМЕН", "finance.py: safe_eval на AST — формулы администратора без eval() · фин. функции аннуитета", GREEN_MID),
    (5.95, "ДАННЫЕ", "SQLAlchemy ORM · 8 таблиц · SQLite (dev) / PostgreSQL 16 (Docker) · идемпотентные сиды", GREEN),
]
for y, t, body, c in layers:
    rect(s, 0.7, y, 11.9, 1.25, c)
    _, tf = box(s, 1.0, y + 0.12, 2.2, 1.0)
    para(tf, t, 16, YELLOW, bold=True, first=True, space_after=0)
    _, tf2 = box(s, 3.3, y + 0.12, 9.1, 1.0)
    para(tf2, body, 13.5, WHITE, first=True, space_after=0)
# стрелки
for y in (2.85, 4.3, 5.75):
    arr = s.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(6.5), Inches(y), Inches(0.35), Inches(0.2))
    arr.fill.solid(); arr.fill.fore_color.rgb = GREY; arr.line.fill.background(); arr.shadow.inherit = False

# ============ СЛАЙД 4: ЗАДАЧА 1 ТИТУЛ ============
s = add_slide()
rect(s, 0, 0, 13.333, 7.5, GREEN, radius=False)
_, tf = box(s, 0.9, 2.4, 11.5, 2.8)
para(tf, "ЗАДАЧА 1", 22, YELLOW, bold=True, first=True, space_after=6)
para(tf, "Симулятор финансовых сценариев «Что, если…?»", 40, WHITE, bold=True, space_after=10)
para(tf, "Моделирование ипотечных и строительных сценариев: досрочный платёж, кредит на ремонт, сдача в аренду", 18, RGBColor(0xE6, 0xF6, 0xEA))

# ============ СЛАЙД 5: СЦЕНАРИИ СИМУЛЯТОРА ============
s = add_slide(LIGHT)
header(s, "Задача 1 · Шесть сценариев моделирования", "Каждый пересчитывает платёж, срок, переплоту и бюджет мгновенно", "03")
sc = [
    ("Базовая ипотека", ["Цена, взнос, ставка, срок", "Аннуитетный платёж", "Переплата и ДТІ"]),
    ("Досрочное погашение", ["Взнос → срок короче", "Экономия на процентах", "Сокращение срока vs платежа"]),
    ("Кредит на ремонт", ["Отдельный кредит на ремонт", "Суммарная нагрузка", "Остаток бюджета семьи"]),
    ("Сдача в аренду", ["Доход с простоем и НПД", "Кэшфлоу в месяц", "Окупаемость и доходность"]),
    ("Строительство дома", ["Транши по этапам", "Проценты на стройке", "Платёж после ввода"]),
    ("Сельская ипотека 3%", ["Ставка 3% против рынка", "Экономия в месяц", "Экономия за весь срок"]),
]
for i, (t, body) in enumerate(sc):
    x = 0.5 + (i % 3) * 4.22
    y = 1.7 + (i // 3) * 2.5
    chip(s, x, y, 3.9, 2.2, t, body)

# ============ СЛАЙД 6: ФОРМУЛЫ ============
s = add_slide(LIGHT)
header(s, "Задача 1 · Формулы и параметры", "Ядро — аннуитетная модель; всё задаётся данными, а не кодом", "04")
_, tf = box(s, 0.6, 1.65, 6.2, 4.8)
para(tf, "Финансовое ядро", 17, GREEN, bold=True, first=True, space_after=8)
para(tf, "платёж:  P = S · i·(1+i)ⁿ / ((1+i)ⁿ − 1)", 15, GREY, space_after=4, font="Consolas")
para(tf, "срок:     n = ln(P/(P − S·i)) / ln(1+i)", 15, GREY, space_after=4, font="Consolas")
para(tf, "переплата: Ov = P·n − S", 15, GREY, space_after=10, font="Consolas")
para(tf, "Дополнительные модели", 17, GREEN, bold=True, space_after=6)
for t in ["Аренда: простой (вакантность), управление, налог НПД 4%", "Стройка: транши → проценты периода → платёж после ввода", "Вычеты: 13% с лимитами 2 млн (покупка) и 3 млн (проценты)", "ДТІ = платёж / доход — индикатор долговой нагрузки"]:
    para(tf, "• " + t, 13.5, GREY, space_after=4)
rect(s, 7.1, 1.65, 5.7, 4.8, GREEN_DARK)
_, tf = box(s, 7.4, 1.85, 5.1, 4.4)
para(tf, "Пример: досрочный платёж", 16, YELLOW, bold=True, first=True, space_after=8)
para(tf, "Ввод: долг 4,8 млн · 14% · платёж 61 000 ₽", 13.5, WHITE, space_after=6)
para(tf, "Досрочно: 500 000 ₽", 13.5, WHITE, space_after=10)
para(tf, "−67 месяцев", 30, YELLOW, bold=True, space_after=4)
para(tf, "срок короче на 5,5 лет", 13, RGBColor(0xCF, 0xE8, 0xD6), space_after=8)
para(tf, "−3 566 215 ₽", 30, YELLOW, bold=True, space_after=4)
para(tf, "экономия на процентах", 13, RGBColor(0xCF, 0xE8, 0xD6))

# ============ СЛАЙД 7: SAFE_EVAL ============
s = add_slide(LIGHT)
header(s, "Задача 1 · Настройка администратором", "Новые сценарии, формулы, параметры и подсказки — без программиста и деплоя", "05")
steps = [
    ("1 · Сценарий как данные", "Сценарий хранится в PostgreSQL: параметры, формулы, подсказки — JSON. CRUD через REST."),
    ("2 · safe_eval вместо eval", "Формула — строка. Исполнение: AST-разбор Python и обход с белым списком. Без eval, импортов, доступа к ОС."),
    ("3 · Изоляция расчётов", "Ошибка одной формулы не рушит сценарий: строка помечается ошибкой, остальные считаются."),
    ("4 · Умные подсказки", "У подсказки есть condition — выражение от переменных: предупреждение при ДТІ > 50% и т.п."),
]
for i, (t, body) in enumerate(steps):
    y = 1.65 + i * 1.32
    rect(s, 0.6, y, 12.1, 1.15, LIGHT if i % 2 else WHITE, line=GREEN)
    _, tf = box(s, 0.85, y + 0.1, 3.4, 0.95)
    para(tf, t, 15, GREEN, bold=True, first=True, space_after=0)
    _, tf2 = box(s, 4.4, y + 0.1, 8.1, 0.95)
    para(tf2, body, 13, GREY, first=True, space_after=0)

# ============ СЛАЙД 8: ЗАДАЧА 2 ТИТУЛ ============
s = add_slide()
rect(s, 0, 0, 13.333, 7.5, GREEN, radius=False)
_, tf = box(s, 0.9, 2.4, 11.5, 2.8)
para(tf, "ЗАДАЧА 2", 22, YELLOW, bold=True, first=True, space_after=6)
para(tf, "Интерактивный навигатор «Путь к своему дому»", 40, WHITE, bold=True, space_after=10)
para(tf, "От выбора недвижимости до сделки и обустройства — 7 адаптивных сценариев", 18, RGBColor(0xE6, 0xF6, 0xEA))

# ============ СЛАЙД 9: ЭТАПЫ ============
s = add_slide(LIGHT)
header(s, "Задача 2 · Шесть этапов пути клиента", "Единый каркас, который адаптируется под сценарий", "06")
stages = [
    ("1. Выбор", "Бюджет, район, параметры объекта, просмотры"),
    ("2. Финансы", "Взнос, программа, одобрение, структура платежей"),
    ("3. Проверка", "Документы, обременения, юр. чистота, оценка"),
    ("4. Сделка", "Договор, аккредитив/эскроу, расчёты, подписание"),
    ("5. Регистрация", "Росреестр, право собственности, выписка ЕГРН"),
    ("6. Обустройство", "Ремонт, страхование, переезд, налоги и вычеты"),
]
for i, (t, body) in enumerate(stages):
    x = 0.45 + (i % 3) * 4.25
    y = 1.75 + (i // 3) * 2.35
    rect(s, x, y, 3.95, 2.0, WHITE, line=GREEN)
    _, tf = box(s, x + 0.2, y + 0.12, 3.55, 1.75)
    para(tf, t, 17, GREEN, bold=True, first=True, space_after=6)
    para(tf, body, 13.5, GREY)
_, tf = box(s, 0.45, 6.35, 12.4, 0.7)
para(tf, "Каждый этап раскрыт в шаги с чек-листами, советами и предупреждениями «на чужих ошибках»", 14, GREEN, bold=True, first=True)

# ============ СЛАЙД 10: 7 СЦЕНАРИЕВ ============
s = add_slide(LIGHT)
header(s, "Задача 2 · Семь сценариев — семь разных маршрутов", "Маршрут перестраивается: этапы те же, наполнение уникально", "07")
rows = [
    ("Квартира (вторичка)", "34 пункта", "Проверка дома, подвала, истории продаж, торг"),
    ("Частный дом", "38 пунктов", "Техпаспорт, границы, коммуникации, договор ЭСО"),
    ("Участок", "32 пункта", "Межевание, ВРИ, категории земель, подъезд, ЛЭП"),
    ("Строительство", "36 пунктов", "Проект, смета, транши, надзор, ввод в эксплуатацию"),
    ("Ремонт", "31 пункт", "Сметы, чеки, узаконивание перепланировки"),
    ("Сельская ипотека", "31 пункт", "Проверка села в программе, ставка 3%, лимиты"),
    ("Готовый объект (новостройка)", "34 пункта", "214-ФЗ, эскроу, приёмка, дефекты, ключи"),
]
y0 = 1.6
for i, (t, cnt, uniq) in enumerate(rows):
    y = y0 + i * 0.75
    rect(s, 0.5, y, 12.3, 0.65, WHITE if i % 2 == 0 else LIGHT, line=RGBColor(0xCC, 0xE3, 0xD2))
    _, tf = box(s, 0.75, y + 0.09, 4.6, 0.5)
    para(tf, t, 14.5, GREEN, bold=True, first=True, space_after=0)
    _, tf = box(s, 5.5, y + 0.09, 1.6, 0.5)
    para(tf, cnt, 13, GREY, first=True, space_after=0)
    _, tf = box(s, 7.2, y + 0.09, 5.4, 0.5)
    para(tf, uniq, 13, GREY, first=True, space_after=0)

# ============ СЛАЙД 11: КАК МЕНЯЮТСЯ ШАГИ ============
s = add_slide(LIGHT)
header(s, "Задача 2 · Как навигатор меняет шаги", "Пример: этап «Проверка» в трёх сценариях", "08")
cols = [
    ("Квартира", ["Выписка ЕГРН: собственники", "История переходов права", "Долги по ЖКХ, справка об отсутствии", "Неузаконенные перепланировки", "Проверка дома: подвал, крыша"]),
    ("Участок", ["Межевое дело, границы", "ВРИ по ПЗЗ — можно строить?", "Категория земель: СНТ/ИЖС/ЛПХ", "Обременения: ЛЭП, газ, охранные зоны", "Проезд — круглогодичный?"],),
    ("Стройка", ["Права на участок и ВРИ", "ГПЗУ: пятно застройки", "Проект и смета — экспертиза", "Договор подряда: этапы, штрафы", "Учёт траншей по документам"]),
]
for i, (t, body) in enumerate(cols):
    x = 0.5 + i * 4.22
    rect(s, x, 1.65, 3.9, 4.9, WHITE, line=GREEN)
    _, tf = box(s, x + 0.2, 1.8, 3.5, 0.5)
    para(tf, t, 17, GREEN, bold=True, first=True, space_after=0)
    _, tf = box(s, x + 0.2, 2.4, 3.5, 4.0)
    for b in body:
        para(tf, "• " + b, 13, GREY, space_after=8)
_, tf = box(s, 0.5, 6.7, 12.3, 0.6)
para(tf, "Все 21 пара сценариев различаются — проверено автотестом", 14, GREEN, bold=True, first=True)

# ============ СЛАЙД 12: СРАВНЕНИЕ ============
s = add_slide(LIGHT)
header(s, "Задача 2 · Режим сравнения сценариев", "Матрица: этап × сценарий, уникальные шаги подсвечены", "09")
# мини-таблица
import copy
tbl_data = [
    ["Этап", "Кв.", "Дом", "Уч.", "Стр.", "Рем.", "С/И", "Нов."],
    ["Выбор", "Кв.", "Дом", "Уч.", "Стр.", "Рем.", "С/И", "Нов."],
    ["Финансы", "Ип", "Ип", "Уч-Ип", "Стр-кр", "Рем-кр", "С/И 3%", "Эскр"],
    ["Проверка", "ЕГРН", "ТП+Г", "Меж", "ГПЗУ", "Сметы", "Село", "214-ФЗ"],
    ["Сделка", "Аккр", "Аккр", "Аккр", "Подр", "Дог", "Аккр", "Эскроу"],
]
gfx = s.shapes.add_table(5, 8, Inches(0.7), Inches(1.8), Inches(11.9), Inches(3.6)).table
for r, row in enumerate(tbl_data):
    for c, val in enumerate(row):
        cell = gfx.cell(r, c)
        cell.text = val
        p = cell.text_frame.paragraphs[0]
        p.runs[0].font.size = Pt(13 if r else 14)
        p.runs[0].font.bold = r == 0 or c == 0
        p.runs[0].font.color.rgb = WHITE if r == 0 else GREY
        cell.fill.solid()
        cell.fill.fore_color.rgb = GREEN if r == 0 else (LIGHT if r % 2 else WHITE)
_, tf = box(s, 0.7, 5.7, 11.9, 1.2)
para(tf, "Красным в интерфейсе подсвечены шаги, уникальные для сценария — сразу видно различие маршрутов.", 14, GREY, first=True)
para(tf, "Прогресс отмечается в чек-листах и хранится на сервере (PostgreSQL), доступен с любого устройства.", 14, GREY)

# ============ СЛАЙД 13: ЗАДАЧА 3 ТИТУЛ ============
s = add_slide()
rect(s, 0, 0, 13.333, 7.5, GREEN, radius=False)
_, tf = box(s, 0.9, 2.4, 11.5, 2.8)
para(tf, "ЗАДАЧА 3", 22, YELLOW, bold=True, first=True, space_after=6)
para(tf, "Модуль «Жизнь после ипотеки»", 40, WHITE, bold=True, space_after=10)
para(tf, "Что делать после оформления: платежи, вычеты, справки, страхование и сервисы банка", 18, RGBColor(0xE6, 0xF6, 0xEA))

# ============ СЛАЙД 14: 10 СЕРВИСОВ ============
s = add_slide(LIGHT)
header(s, "Задача 3 · Десять сервисов после ипотеки", "Каждый — с инструкцией, документами и калькулятором где уместно", "10")
svc = [
    ("⚡ Досрочное погашение", "Сократить срок или платёж"),
    ("📅 Изменение условия", "Срок ↔ платёж, льготные каникулы"),
    ("🧾 Налоговый вычет", "13%: покупка + проценты, до 650 т.р."),
    ("📄 Справки", "Остаток долга, проценты для ФНС"),
    ("🛡 Страхование", "Продление вовремя: иначе +1 п.п."),
    ("💳 Рефинансирование", "Когда выгодно, когда нет"),
    ("🔔 Платежи", "Автоплатёж, даты, просрочки"),
    ("👨‍👩‍👧 Материнский капитал", "Погашение, обязательство"),
    ("🌍 Господдержка", "Семейная, сельская, IT-ипотека"),
    ("📞 Сервисы банка", "Поддержка, отделения, atendimento"),
]
svc[9] = ("📞 Сервисы банка", "Поддержка, отделения, партнёры")
for i, (t, body) in enumerate(svc):
    x = 0.5 + (i % 5) * 2.52
    y = 1.75 + (i // 5) * 2.45
    rect(s, x, y, 2.32, 2.2, WHITE, line=GREEN)
    _, tf = box(s, x + 0.12, y + 0.12, 2.08, 1.95)
    para(tf, t, 13, GREEN, bold=True, first=True, space_after=6)
    para(tf, body, 11.5, GREY)

# ============ СЛАЙД 15: ДВА КОНТУРА ============
s = add_slide(LIGHT)
header(s, "Задача 3 · Гость и авторизованный клиент", "Два контура данных в одном модуле", "11")
# гость
rect(s, 0.6, 1.7, 5.9, 4.6, WHITE, line=GREY)
_, tf = box(s, 0.9, 1.9, 5.3, 4.2)
para(tf, "ГОСТЬ · публичный сайт", 18, GREY, bold=True, first=True, space_after=8)
for t in ["Демо-ипотека: сумма, ставка, платёж", "Остаток долга и график", "Калькуляторы сервисов на демо-данных", "Регистрация не нужна", "источник: DEMO_MORTGAGE"]:
    para(tf, "• " + t, 13.5, GREY, space_after=6)
# клиент
rect(s, 6.85, 1.7, 5.9, 4.6, GREEN_DARK)
_, tf = box(s, 7.15, 1.9, 5.3, 4.2)
para(tf, "КЛИЕНТ · личный кабинет", 18, YELLOW, bold=True, first=True, space_after=8)
for t in ["Вход по логину/паролю → токен", "Реальная ипотека из БД (контур банка)", "Остаток, ставка, страхование, даты", "Действия: «запланировать досрочку»", "источник: source = bank"]:
    para(tf, "• " + t, 13.5, WHITE, space_after=6)
_, tf = box(s, 0.6, 6.5, 12.2, 0.6)
para(tf, "API один: GET /api/life/context — контент определяется наличием токена", 14, GREEN, bold=True, first=True)

# ============ СЛАЙД 16: БД ============
s = add_slide(LIGHT)
header(s, "Модель данных", "8 таблиц PostgreSQL, SQLAlchemy ORM", "12")
tbls = [
    ("users", "логины, хэши PBKDF2, админ-флаг"),
    ("mortgages", "ипотеки клиентов: долг, ставка, платежи, страхование"),
    ("sim_scenarios", "сценарии: params_schema, formulas, hints (JSON)"),
    ("sim_calculations", "история расчётов с вводом и результатом"),
    ("nav_scenarios", "маршруты: шаги, чек-листы, советы (JSON)"),
    ("nav_progress", "отметки чек-листов по пользователям"),
    ("life_services", "сервисы: инструкции, документы, калькуляторы"),
    ("life_actions", "запланированные действия клиентов"),
]
for i, (t, d) in enumerate(tbls):
    x = 0.6 + (i % 2) * 6.3
    y = 1.7 + (i // 2) * 1.25
    rect(s, x, y, 5.9, 1.05, WHITE, line=GREEN)
    _, tf = box(s, x + 0.2, y + 0.08, 5.5, 0.9)
    para(tf, t, 15, GREEN, bold=True, first=True, space_after=2, font="Consolas")
    para(tf, d, 12.5, GREY)

# ============ СЛАЙД 17: DOCKER + ЗАПУСК ============
s = add_slide(LIGHT)
header(s, "Развёртывание: Docker Compose", "git clone → docker compose up → готово", "13")
rect(s, 0.6, 1.7, 6.4, 2.6, GREEN_DARK)
_, tf = box(s, 0.9, 1.9, 5.8, 2.3)
para(tf, "$ git clone <repo>", 15, WHITE, first=True, space_after=4, font="Consolas")
para(tf, "$ cd rshb-dom-platform", 15, WHITE, space_after=4, font="Consolas")
para(tf, "$ docker compose up --build", 15, YELLOW, bold=True, space_after=8, font="Consolas")
para(tf, "→ http://localhost:8078", 15, YELLOW, bold=True, font="Consolas")
items = [
    ("api", "FastAPI + uvicorn, порт 8078, сборка из Dockerfile (python:3.11-slim)"),
    ("db", "PostgreSQL 16 Alpine + том pgdata + healthcheck pg_isready"),
    ("автосхема", "таблицы и сиды применяются при старте — миграций вручную нет"),
]
for i, (t, d) in enumerate(items):
    y = 4.6 + i * 0.85
    _, tf = box(s, 0.6, y, 6.4, 0.8)
    para(tf, t, 14, GREEN, bold=True, first=True, space_after=1)
    para(tf, d, 12.5, GREY)
rect(s, 7.3, 1.7, 5.5, 4.9, WHITE, line=GREEN)
_, tf = box(s, 7.55, 1.9, 5.0, 4.5)
para(tf, "Почему это надёжно", 16, GREEN, bold=True, first=True, space_after=8)
for t in ["Один compose-файл: среда воспроизводима у любого ревьюера", "БД в томе: данные переживают перезапуск", "Сборка кэшируется слоями — быстрые пересборки", "Swagger /docs — документация API из кода", "Тот же код работает на SQLite без Docker (dev-режим)"]:
    para(tf, "• " + t, 13, GREY, space_after=7)

# ============ СЛАЙД 18: ИТОГИ ============
s = add_slide()
rect(s, 0, 0, 13.333, 7.5, GREEN_DARK, radius=False)
for cx, cy, d, c in [(-1.6, -1.6, 4.2, GREEN_MID), (11.4, 5.1, 4.0, GREEN_MID)]:
    shp = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx), Inches(cy), Inches(d), Inches(d))
    shp.fill.solid(); shp.fill.fore_color.rgb = c; shp.line.fill.background()
    shp.shadow.inherit = False
_, tf = box(s, 0.9, 0.7, 11.5, 1.2)
para(tf, "Итоги", 40, WHITE, bold=True, first=True)
stats = [
    ("3 задачи", "в одном приложении — полностью"),
    ("6 сценариев", "финансового моделирования"),
    ("7 маршрутов", "навигатора, 238 пунктов"),
    ("10 сервисов", "«после ипотеки», 2 контура"),
    ("40 тестов", "API + фронтенд, все зелёные"),
    ("1 команда", "docker compose up"),
]
for i, (big, small) in enumerate(stats):
    x = 0.9 + (i % 3) * 4.0
    y = 2.1 + (i // 3) * 2.2
    _, tf = box(s, x, y, 3.7, 1.9)
    para(tf, big, 34, YELLOW, bold=True, first=True, space_after=4)
    para(tf, small, 15, RGBColor(0xCF, 0xE8, 0xD6))
_, tf = box(s, 0.9, 6.6, 11.5, 0.6)
para(tf, "Полный код, README и техническая документация — в репозитории GitHub", 15, RGBColor(0xA8, 0xCC, 0xB2), first=True)

prs.save("/workspace/rshb-presentation.pptx")
print("Сохранено: /workspace/rshb-presentation.pptx, слайдов:", len(prs.slides.__iter__.__self__._sldIdLst))

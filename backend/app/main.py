"""Точка входа: FastAPI-приложение «РСХБ · Путь к своему дому»."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .init_db import init_db
from .routers import sim, nav, life

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Три сервиса РСХБ: симулятор «Что, если...?», "
                "навигатор «Путь к своему дому», модуль «Жизнь после ипотеки»",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # демо; в продакшене — домен фронтенда
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sim.router)
app.include_router(nav.router)
app.include_router(life.router)

# Статика фронтенда: ищем frontend/ в нескольких возможных местах —
# раскладка локальная (корень/backend/app) и в Docker (/app/app) различается
_CANDIDATES = [
    BASE_DIR.parent / "frontend",   # локально: <корень>/frontend
    BASE_DIR / "frontend",          # docker: /app/frontend
]
STATIC_DIR = next((p for p in _CANDIDATES if p.exists()), _CANDIDATES[0])
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"app": settings.APP_NAME, "version": settings.APP_VERSION,
            "docs": "/docs"}


@app.on_event("startup")
def startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME,
            "version": settings.APP_VERSION}

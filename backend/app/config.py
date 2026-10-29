"""Конфигурация приложения. Все настройки берутся из переменных окружения."""
import os


class Settings:
    # Строка подключения к БД. В Docker — PostgreSQL, локально можно SQLite.
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite:///./rshb.db"
    )
    # Секрет для подписи токенов авторизации.
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    APP_NAME: str = "РСХБ · Путь к своему дому"
    APP_VERSION: str = "1.0.0"
    ADMIN_TOKEN: str = os.getenv("ADMIN_TOKEN", "admin-demo-token")


settings = Settings()

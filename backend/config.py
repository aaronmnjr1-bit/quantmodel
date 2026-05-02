from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Application
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "change_me_in_production"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://quantmodel:quantmodel_secret@localhost:5432/quantmodel"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # MetaTrader 5
    MT5_LOGIN: int = 0
    MT5_PASSWORD: str = ""
    MT5_SERVER: str = ""

    # Scraping
    FOREXFACTORY_BASE_URL: str = "https://www.forexfactory.com"
    SCRAPE_INTERVAL_SECONDS: int = 300

    # Trading defaults
    DEFAULT_RISK_PCT: float = 1.0
    DEFAULT_MAX_POSITIONS: int = 5
    DEFAULT_DAILY_LOSS_LIMIT: float = 3.0
    DEFAULT_TRADING_MODE: str = "scalp"

    # JWT
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24


settings = Settings()

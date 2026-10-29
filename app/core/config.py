from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://pizza:pizza@localhost:5432/pizzeria"
    JWT_SECRET: str = "cambiar-en-prod"
    JWT_ALG: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 8
    CORS_ORIGINS: list[str] = ["*"]


settings = Settings()
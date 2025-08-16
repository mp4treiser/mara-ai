import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(".env")


class DBSettings(BaseSettings):
    host: str = os.environ.get("DB_HOST", "localhost")
    port: int = int(os.environ.get("DB_PORT", "5432"))
    user: str = os.environ.get("DB_USER", "postgres")
    password: str = os.environ.get("DB_PASS", "postgres")
    name: str = os.environ.get("DB_NAME", "mara")


class RedisSettings(BaseSettings):
    host: str = os.environ.get("REDIS_HOST", "localhost")
    port: int = int(os.environ.get("REDIS_PORT", "6379"))
    password: str = os.environ.get("REDIS_PASSWORD", "")
    db: int = int(os.environ.get("REDIS_DB", "0"))
    
    @property
    def url(self) -> str:
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


class Settings():
    db: DBSettings = DBSettings()
    redis: RedisSettings = RedisSettings()
    
    # JWT Settings
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Celery Settings
    @property
    def CELERY_BROKER_URL(self) -> str:
        return self.redis.url
    
    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        return self.redis.url


settings = Settings()

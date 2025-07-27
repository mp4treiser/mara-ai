import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(".env")


class DBSettings(BaseSettings):
    host: str = os.environ.get("DB_HOST")
    port: int = os.environ.get("DB_PORT")
    user: str = os.environ.get("DB_USER")
    password: str = os.environ.get("DB_PASS")
    name: str = os.environ.get("DB_NAME")


class Settings():
    db: DBSettings = DBSettings()


settings = Settings()

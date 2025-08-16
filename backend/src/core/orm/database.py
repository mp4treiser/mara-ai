from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from src.core.config import settings

# Асинхронное подключение
DATABASE_URL = f"postgresql+asyncpg://{settings.db.user}:{settings.db.password}@{settings.db.host}:{settings.db.port}/{settings.db.name}"
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# Синхронное подключение для роутеров
SYNC_DATABASE_URL = f"postgresql://{settings.db.user}:{settings.db.password}@{settings.db.host}:{settings.db.port}/{settings.db.name}"
sync_engine = create_engine(SYNC_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

Base = declarative_base()

async def get_async_session():
    async with AsyncSessionLocal() as session:
        yield session

def get_db():
    """Синхронная функция для получения сессии БД в роутерах"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

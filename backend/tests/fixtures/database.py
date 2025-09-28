import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from sqlalchemy.orm import sessionmaker

from src.core.config import settings
from src.core.orm import Base


class TestDatabase:
    def __init__(self):
        self.database_url = f'postgresql+asyncpg://{settings.db.user}:{settings.db.password}@{settings.db.host}:{settings.db.port}/{settings.db.test_name}'
        self.engine = create_async_engine(self.database_url)
        self.session_maker = sessionmaker(
            self.engine,class_=AsyncSession, expire_on_commit=False
        )

    async def create_database(self):  # noqa

        try:
            conn = await asyncpg.connect(
                host=settings.db.host,
                port=settings.db.port,
                user=settings.db.user,
                password=settings.db.password,
                database=settings.db.test_name,
            )
            await conn.close()
        except asyncpg.InvalidCatalogNameError:
            sys_conn = await asyncpg.connect(
                host=settings.db.host,
                port=settings.db.port,
                user=settings.db.user,
                password=settings.db.password,
            )
            try:
                await sys_conn.execute(
                    f'CREATE DATABASE "{settings.db.test_name}" OWNER "{settings.db.user}"'
                )
            finally:
                await sys_conn.close()

    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    async def close(self):
        await self.engine.dispose()
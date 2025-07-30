from contextlib import asynccontextmanager
from typing import AsyncGenerator
from typing import Type

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase


class DatabaseConnect:
    """Database Connect"""

    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(url=url, echo=echo)
        self.session_maker = async_sessionmaker(self.engine, expire_on_commit=False)

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()

    @asynccontextmanager
    async def session_wrap(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()

    async def create_all_tables(self, base: Type[DeclarativeBase]) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(base.metadata.create_all)

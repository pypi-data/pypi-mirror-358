from typing import Type

from sqlalchemy import func
from sqlalchemy import text
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select


class BaseAdapter[T]:
    """
    Base adapter for creating, retrieving,
    updating and deleting entities from a database.
    """

    session: AsyncSession
    entity_table: Type[T]

    def __init__(self, session: AsyncSession, entity_table: Type[T]) -> None:
        self.session = session
        self.entity_table = entity_table

    async def _get(self, statement: Select) -> T | None:
        """Private get method."""
        res = await self.session.execute(statement)
        return res.unique().scalar_one_or_none()

    async def get(self, **filter_by) -> T | None:
        """Get a single entity by filter."""
        stmt = select(self.entity_table).filter_by(**filter_by)
        return await self._get(stmt)

    async def get_all(
            self,
            limit: int | None = None,
            offset: int | None = None,
            order_by: str | None = None,
            **filter_by
    ) -> list[T]:
        """Get all entities by filter."""
        stmt = select(self.entity_table).filter_by(**filter_by)
        if limit is not None and offset is not None:
            stmt = stmt.limit(limit).offset(offset)
        if order_by is not None:
            stmt = stmt.order_by(text(order_by))
        res = await self.session.scalars(stmt)
        return [row for row in res.unique().all()]

    async def create(self, create_data: dict[str, any]) -> T:
        """Create an entity."""
        stmt = insert(self.entity_table).values(**create_data)
        stmt = stmt.returning(self.entity_table)
        return await self.session.scalar(stmt)

    async def update(
            self,
            entity_table: T,
            update_data: dict[str, any]
    ) -> T:
        """Update an entity."""
        for key, value in update_data.items():
            setattr(entity_table, key, value)
        self.session.add(entity_table)
        await self.session.flush()
        return entity_table

    async def delete(self, entity_table: T) -> None:
        """Delete an entity."""
        await self.session.delete(entity_table)

    async def count(self) -> int:
        """Count as entities."""
        stmt = select(func.count()).select_from(self.entity_table)
        return await self.session.scalar(stmt)

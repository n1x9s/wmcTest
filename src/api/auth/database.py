import uuid
from typing import Sequence

from sqlalchemy import select

from src.config.loader import engine, async_session_maker


async def create_db_and_tables():
    from wms_services.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_user_by_id(user_id: uuid.UUID):
    from wms_services.models import User

    async with async_session_maker() as session:
        stmt = select(User).filter(User.id == user_id)
        result = await session.execute(stmt)

        user = result.scalar_one_or_none()

        if not user:
            raise Exception("User not found")
        return user


async def get_users() -> Sequence:
    from wms_services.models import User

    """Список пользователей"""
    async with async_session_maker() as session:
        try:
            stmt = select(User)
            result = await session.execute(stmt)
            users = result.scalars().all()
            return users
        except Exception as e:
            raise Exception(f"Error fetching users: {str(e)}")

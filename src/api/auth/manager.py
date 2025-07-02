import uuid
from collections.abc import AsyncGenerator
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import config
from wms_services.models import User, ProfileModel


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    from src.config.loader import async_session_maker
    async with async_session_maker() as session:
        yield session


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    from src.config.loader import async_session_maker
    with async_session_maker() as session:
        yield session

SECRET = config.JWT_SECRET


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        from src.config.loader import async_session_maker

        async with async_session_maker() as session:
            profile = ProfileModel(user_id=user.id)

            session.add(profile)

            await session.commit()

        logger.info(f"User {user.id} has registered.")
        logger.info(f"Profile for user {user.id} has added with ID {profile.id}.")

    async def on_after_request_verify(
            self, user: User, token: str, request: Optional[Request] = None
    ):
        logger.info(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    from wms_services.models import User

    return SQLAlchemyUserDatabase(session, User)


async def get_user_manager(user_db=Depends(get_user_db)):
    return UserManager(user_db)

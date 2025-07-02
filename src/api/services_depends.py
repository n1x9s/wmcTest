from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.api.auth.manager import get_async_session
from src.config.loader import fastapi_users
from wms_services.models import User
from wms_services.repositories import (
    ProfileDBRepository,
    WBAccountsDBRepo
)
from wms_services.services import (
    ProfileService,
    WBAccountsService
)

def get_user(user: User = Depends(fastapi_users.current_user())) -> User:
    if user is None or user.profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Profile does not exist")
    return user


def get_profile_service(session: AsyncSession = Depends(get_async_session)) -> ProfileService:
    return ProfileService(ProfileDBRepository(session=session))


def get_wb_accounts_service(
        session: AsyncSession = Depends(get_async_session),
) -> WBAccountsService:
    return WBAccountsService(
        WBAccountsDBRepo(session=session),
        ProfileDBRepository(session=session),
    )
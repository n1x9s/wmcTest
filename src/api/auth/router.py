from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_jwt import JwtAccessBearer, JwtRefreshBearer
from fastapi_users.manager import BaseUserManager


from src.api.auth.auth import decode_token
from src.api.auth.database import get_user_by_id, get_users
from src.api.auth.schemas import UserRead
from src.config import config
from src.config.loader import fastapi_users
from wms_services.models import User

router = APIRouter(
    prefix="/auth/jwt",
    tags=["auth"],
)

users_router = APIRouter(
    prefix="/users",
    tags=["users"],
)

access_security = JwtAccessBearer(secret_key=config.JWT_SECRET)
refresh_security = JwtRefreshBearer(secret_key=config.JWT_SECRET)


@router.post("/login")
async def login(
        credentials: OAuth2PasswordRequestForm = Depends(),
        user_manager: BaseUserManager = Depends(fastapi_users.get_user_manager)
):
    user = await user_manager.authenticate(credentials=credentials)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = access_security.create_access_token({"sub": str(user.id)},
                                                       timedelta(seconds=config.JWT_ACCESS_LIFETIME_SECONDS))
    refresh_token = refresh_security.create_refresh_token({"sub": str(user.id)},
                                                          timedelta(seconds=config.JWT_REFRESH_LIFETIME_SECONDS))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    try:
        payload = await decode_token(refresh_token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=e)

    user_id = payload['subject']['sub']

    try:
        user = await get_user_by_id(user_id)
    except Exception as e:
        raise HTTPException(status_code=401, detail=e)

    new_access_token = access_security.create_access_token({"sub": str(user.id)},
                                                           timedelta(seconds=config.JWT_ACCESS_LIFETIME_SECONDS))

    return {"access_token": new_access_token, "token_type": "bearer"}

@users_router.get('/all', response_model=List[UserRead])
async def get_users_router(user: User = Depends(fastapi_users.current_user())):
    users = await get_users()
    return [UserRead(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        second_name=user.second_name,
        last_name=user.last_name,
        role=user.role,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        is_verified=user.is_verified,
    ) for user in users]

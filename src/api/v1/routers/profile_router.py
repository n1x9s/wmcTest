import uuid

from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status

from src.api.services_depends import get_profile_service
from src.api.v1.responses import COMMON_RESPONSES
from src.config.loader import fastapi_users
from wms_services.models import User
from wms_services.schemas import ProfileResponseSchema, ProfileRequestSchema
from wms_services.services import ProfileService

router = APIRouter(
    prefix="/profile",
    tags=["profile"],
)


async def extract_profile_path_id(kwargs) -> uuid.UUID:
    return kwargs.get("profile_id")


async def extract_profile_from_user(kwargs) -> uuid.UUID:
    user = kwargs.get("user")
    profile_service: ProfileService = kwargs.get("profile_service")
    profile = await profile_service.get_by_id(user_id=user.id)

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль не найден",
        )

    return profile.id


@router.get("/profile/{profile_id}", response_model=ProfileResponseSchema, responses=COMMON_RESPONSES)
async def get_profile_by_profile_id(
        profile_id: uuid.UUID = Path(..., description="ID профиля"),
        profile_service: ProfileService = Depends(get_profile_service),
        user: User = Depends(fastapi_users.current_user())
):
    """Профиль пользователя по ID профиля (владелец профиля или суперпользователь)"""
    profile = await profile_service.get_by_id(profile_id=profile_id)

    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Профиль не найден")

    return ProfileResponseSchema.model_validate(profile)


@router.get("/user/{user_id}", response_model=ProfileResponseSchema, responses=COMMON_RESPONSES)
async def get_profile_by_user_id(
        user_id: uuid.UUID = Path(..., description="ID профиля"),
        profile_service: ProfileService = Depends(get_profile_service),
        user: User = Depends(fastapi_users.current_user())
):
    """Профиль пользователя по ID пользователя (суперпользователь)"""
    profile = await profile_service.get_by_id(user_id=user_id)

    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Профиль не найден")

    return ProfileResponseSchema.model_validate(profile)


@router.get("/current-user", response_model=ProfileResponseSchema, responses=COMMON_RESPONSES)
async def get_profile_by_user_id(
        profile_service: ProfileService = Depends(get_profile_service),
        user: User = Depends(fastapi_users.current_user())
):
    """Профиль текущего пользователя"""
    profile = await profile_service.get_by_id(user_id=user.id)

    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Профиль не найден")

    return ProfileResponseSchema.model_validate(profile)


@router.get("/profiles", response_model=list[ProfileResponseSchema], responses=COMMON_RESPONSES)
async def get_all_profiles(
        profile_service: ProfileService = Depends(get_profile_service),
        user: User = Depends(fastapi_users.current_user())
):
    """Список профилей (суперпользователь)"""
    profiles = await profile_service.get_all_profiles()
    return [ProfileResponseSchema.model_validate(profile) for profile in profiles]


@router.put("/{profile_id}", response_model=ProfileResponseSchema, responses=COMMON_RESPONSES)
async def update_profile(
        updated_data: ProfileRequestSchema,
        profile_id: uuid.UUID = Path(..., description="ID профиля"),
        profile_service: ProfileService = Depends(get_profile_service),
        user: User = Depends(fastapi_users.current_user())
):
    """Изменение профиля по ID профиля (суперпользователь)"""

    profile = await profile_service.update_profile(profile_id, updated_data.model_dump())

    return ProfileResponseSchema.model_validate(profile)


@router.delete("/{profile_id}", responses=COMMON_RESPONSES)
async def delete_profile(
        profile_id: uuid.UUID,
        profile_service: ProfileService = Depends(get_profile_service),
        user: User = Depends(fastapi_users.current_user())
):
    """Удаление профиля по ID профиля (суперпользователь)"""

    success = await profile_service.delete_profile(profile_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Профиль не найден")

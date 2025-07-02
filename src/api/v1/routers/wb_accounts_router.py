import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status

from src.api.services_depends import (
    get_wb_accounts_service,
    get_profile_service,
    get_user,
)
from src.api.v1.responses import COMMON_RESPONSES
from wms_services.exceptions.accounts_exceptions import WbAccountNotFoundError
from wms_services.models import (
    User,
    ProfileModel
)
from wms_services.schemas import (
    CreateWBAccountSchema,
    ResponseWBAccountSchema,
    UpdateWBAccountSchema,
)
from wms_services.services import (
    WBAccountsService,
    ProfileService,
)

router = APIRouter(
    prefix="/wbacc",
    tags=["WB Accounts"]
)


@router.post("/create", response_model=ResponseWBAccountSchema, responses=COMMON_RESPONSES)
async def create_wb_account(
        wb_data: CreateWBAccountSchema,
        user: User = Depends(get_user),
        wb_accounts_service: WBAccountsService = Depends(get_wb_accounts_service),
        profile_service: ProfileService = Depends(get_profile_service),
        # для того, чтобы декоратор мог проверить валидность профиля
):
    """Подключить кабинет ВБ к профилю"""

    profile: ProfileModel = user.profile
    wb_account = await wb_accounts_service.add_account(
        profile_id=profile.id,
        account_create_data=wb_data
    )

    return ResponseWBAccountSchema.model_validate(wb_account)


@router.get("/all", response_model=List[ResponseWBAccountSchema], responses=COMMON_RESPONSES)
async def get_all_accounts(
        user: User = Depends(get_user),
        wb_accounts_service: WBAccountsService = Depends(get_wb_accounts_service)
):
    """Список всех кабинетов"""
    accs = await wb_accounts_service.get_all()

    if not accs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Не найдено кабинетов"
        )

    return accs


@router.get("/{account_id}", response_model=ResponseWBAccountSchema, responses=COMMON_RESPONSES)
async def get_account(
        account_id: uuid.UUID,
        user: User = Depends(get_user),
        wb_accounts_service: WBAccountsService = Depends(get_wb_accounts_service),
):
    """Получить кабинет по ID кабинета"""
    acc = await wb_accounts_service.get_accounts_by_id(account_id=account_id)

    return acc


@router.get("/current-user/accounts", response_model=List[ResponseWBAccountSchema], responses=COMMON_RESPONSES)
async def get_current_user_wb_accounts(
        user: User = Depends(get_user),
        wb_accounts_service: WBAccountsService = Depends(get_wb_accounts_service),
):
    """Получить список кабинетов для текущего пользователя"""
    profile: ProfileModel = user.profile

    accs = await wb_accounts_service.get_accounts_by_id(profile_id=user.profile.id)

    return accs

@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT, responses=COMMON_RESPONSES)
async def delete_wb_account(
        account_id: uuid.UUID,
        user: User = Depends(get_user),
        wb_accounts_service: WBAccountsService = Depends(get_wb_accounts_service)
):
    """Удалить ВБ кабинет"""
    if not await wb_accounts_service.delete_account(account_id=account_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Не найден указанный кабинет"
        )


@router.get("/ping/{account_id}", response_model=bool, responses=COMMON_RESPONSES)
async def ping_account(
        account_id: uuid.UUID,
        wb_accounts_service: WBAccountsService = Depends(get_wb_accounts_service)
):
    return await wb_accounts_service.ping(account_id=account_id)

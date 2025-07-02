import uuid
from datetime import datetime
from typing import Optional, Sequence

from loguru import logger
# from marketplace_client.utils.jwt import InvalidTokenError, decode_token
# from marketplace_client.wildberries import WildberriesMarketplaceClient
# from marketplace_client.wildberries.client import WildberriesBaseClient

from wms_services.exceptions.accounts_exceptions import WbAccountInactiveError, WbAccountNotFoundError
from wms_services.models import WBAccountModel, ProfileModel
from wms_services.models.user_models import WBAccountStatus
from wms_services.repositories.profile_repo import ProfileDBRepository
from wms_services.repositories.wb_accounts_repo import WBAccountsDBRepo
from wms_services.schemas import CreateWBAccountSchema, UpdateWBAccountSchema
from wms_services.services.base_service import BaseService

__all__ = ["WBAccountsService"]

class WBAccountsService(BaseService):
    def __init__(self,
                 wb_account_repo: WBAccountsDBRepo,
                 profile_repo: ProfileDBRepository,
                 *args, **kwargs):
        self.wb_account_repo = wb_account_repo
        self.profile_repo = profile_repo
        super().__init__(*args, **kwargs)

    async def add_account(
            self,
            profile_id: uuid.UUID,
            account_create_data: CreateWBAccountSchema,
    ) -> Optional[WBAccountModel]:
        """
        Добавление личного кабинета ВБ для профиля.
        :param profile_id: ID профиля, к которому привязывается аккаунт
        :param account_create_data: Параметры для создания аккаунта
        :return:
        """
        try:
            profile = await self.profile_repo.get_where(many=False, whereclause=ProfileModel.id == profile_id)
            if profile is None:
                logger.error(f"Profile with ID {profile_id} not found.")
                return None

            # Создание неактивного кабинета
            new_account = WBAccountModel(
                profile_id=profile_id,
                **account_create_data.model_dump(),
            )
            new_account = await self.wb_account_repo.save(new_account)

            account, _ = await self.check_account_token(new_account, account_create_data.wb_token)
            return account
        except Exception as e:
            logger.error(f"Error adding WB account: {e}")
            raise

    async def get_accounts_by_id(
            self,
            profile_id: Optional[uuid.UUID] = None,
            account_id: Optional[uuid.UUID] = None,
    ) -> Optional[Sequence[WBAccountModel] | WBAccountModel]:
        """
        Получение списка личных кабинетов для указанного профиля или кабинета.

        Если указан кабинет, то вернется один объект

        Если указан профиль, то вернутся последовательность объектов
        :param account_id:
        :param profile_id: ID профиля
        :return: Список всех личных кабинетов для профиля
        """

        if profile_id is None and account_id is None:
            logger.error(f"profile_id or account_id not provided.")
            raise ValueError("Either profile_id or account_id must be provided.")

        if profile_id is not None and account_id is not None:
            logger.error(f"profile_id and account_id not provided.")
            raise ValueError("Either profile_id or account_id must be provided.")

        try:
            accounts = []
            if profile_id:
                accounts = await self.wb_account_repo.get_where(many=True,
                                                                whereclause=WBAccountModel.profile_id == profile_id)

            if account_id:
                accounts = await self.get_by_id(account_id)

            return accounts
        except Exception as e:
            logger.error(f"Error getting WB accounts: {e}")
            raise

    async def get_all(self) -> Optional[Sequence[WBAccountModel] | WBAccountModel]:
        return await self.wb_account_repo.get_where(many=True)

    async def update_token(
            self,
            account_id: uuid.UUID,
            new_wb_token: str
    ) -> Optional[WBAccountModel]:
        """
        Обновление токена для личного кабинета.
        :param account_id: ID аккаунта
        :param new_wb_token: Новый токен
        :return: Обновленный аккаунт
        """
        try:
            account = await self.wb_account_repo.get(account_id)
            if account is None:
                logger.error(f"WB account with ID {account_id} not found.")
                return None
            account.wb_token = new_wb_token
            account, _ = await self.check_account_token(account, new_wb_token)
            return account
        except Exception as e:
            logger.error(f"Error updating WB account token: {e}")
            raise

    async def delete_account(
            self,
            account_id: uuid.UUID
    ) -> bool:
        """
        Удаление личного кабинета по ID.
        :param account_id: ID аккаунта для удаления
        :return: True, если удаление прошло успешно, иначе False
        """
        try:
            account = await self.wb_account_repo.get(account_id)
            if account is None:
                logger.error(f"WB account with ID {account_id} not found.")
                return False

            await self.wb_account_repo.delete(account)
            return True
        except Exception as e:
            logger.error(f"Error deleting WB account: {e}")
            raise

    async def check_account_token(
        self,
        account: WBAccountModel,
        wb_token: str,
    ) -> (WBAccountModel, bool):
        token_metadata = None
        is_active = False
        token_is_valid = False

        try:
            # Проверка что токен впринципе корректный
            decode_token(wb_token)
            token_is_valid = True
        except InvalidTokenError as e:
            pass
        if token_is_valid:
            # Проверка что токен имеет доступ к нужным разделам
            token_metadata = WildberriesBaseClient.validate_token(wb_token)
            client = WildberriesMarketplaceClient(token=wb_token)
            
            # Проверка что токен действительный на данный момент
            try:
                ping_result = await client.common_ping()
            except Exception as e:
                ping_result = False

            if ping_result:
                account.token_metadata = token_metadata.model_dump(mode="json")
                await self.wb_account_repo.save(account)
                is_active = True

        account.token_metadata = token_metadata.model_dump(mode="json") if token_metadata is not None else None

        if is_active:
            account.status = WBAccountStatus.ACTIVE.value
        else:
            account.status = WBAccountStatus.INACTIVE.value
        account.last_token_validate_at = datetime.now()
        return await self.wb_account_repo.save(account), is_active

    async def ping(
        self,
        account_id: uuid.UUID
    ):
        account = await self.wb_account_repo.get(account_id)
        _, is_active = await self.check_account_token(account, wb_token=account.wb_token)
        return is_active

    def check_active_account(self, account: WBAccountModel) -> WBAccountModel:
        if account.status == WBAccountStatus.ACTIVE.value:
            return account
        raise WbAccountInactiveError

    async def get_by_id(
            self,
            account_id: uuid.UUID
    ) -> WBAccountModel:
        """
        Возвращает аккаунт по его id или вызывает исключение AccountNotFound
        :param account_id:
        :return:
        """
        account = await self.wb_account_repo.get(account_id)
        if account is None:
            raise WbAccountNotFoundError
        return account

    async def get_active_by_id(
            self,
            account_id
    ) -> WBAccountModel:
        return self.check_active_account(await self.get_by_id(account_id))

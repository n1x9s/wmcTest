import uuid
from typing import Optional, Sequence

from loguru import logger

from wms_services.models import ProfileModel
from wms_services.repositories.profile_repo import ProfileDBRepository
from wms_services.schemas import ProfileRequestSchema
from wms_services.services.base_service import BaseService

__all__ = ["ProfileService"]

class ProfileService(BaseService):
    def __init__(self,
                 profile_repo: ProfileDBRepository,
                 *args, **kwargs):
        self.profile_repo = profile_repo

        super().__init__(*args, **kwargs)

    async def get_by_id(
            self,
            profile_id: uuid.UUID | None = None,
            user_id: uuid.UUID | None = None
    ) -> ProfileModel | None:
        """
        Получает профиль по ID профиля или пользователя.
        Оба параметра не могут быть использованы одновременно
        :param profile_id: ID профиля
        :param user_id: ID пользователя
        :return: модель профиля
        """

        if profile_id is not None and user_id is not None:
            logger.error("You cannot specify both profile_id and user_id")
            raise ValueError("Only one of `profile_id` and `user_id` can be specified.")

        try:
            result = None

            if profile_id is not None:
                result = await self.profile_repo.get_where(many=False,
                                                           whereclause=ProfileModel.id == profile_id)
            elif user_id is not None:
                result = await self.profile_repo.get_where(many=False,
                                                           whereclause=ProfileModel.user_id == user_id)

            return result

        except Exception as e:
            logger.error(f"Ошибка получения профиля: {e}")
            raise e

    async def get_all_profiles(self) -> Sequence[ProfileModel]:
        try:
            return await self.profile_repo.get_where(many=True)
        except Exception as e:
            logger.error(f"ошибка получения списка профилей: {e}")
            raise

    # TODO: Убрать не используемый метод
    async def add_tokens(
            self,
            profile_id: uuid.UUID,
            tokens: dict[str, str],
    ) -> Optional[ProfileModel]:
        """
        Добавление токена
        :param profile_id:
        :param tokens: словарь, где ключ соответствует названию поля в БД
        :return:
        """
        try:
            profile = await self.profile_repo.get(profile_id)

            if profile is None:
                return None

            for key, value in tokens.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)

            return await self.profile_repo.save(profile)
        except Exception as e:
            logger.error(f"Error with adding tokens: {e}")
            raise

    async def create_profile(self, profile: ProfileRequestSchema) -> ProfileModel:
        try:
            profile = ProfileModel(**profile.model_dump())
            return await self.profile_repo.save(profile)
        except Exception as e:
            logger.error(f"Ошибка создания профиля: {e}")
            raise

    async def update_profile(self,
                             profile_id: uuid.UUID,
                             updated_data: dict) -> Optional[ProfileModel]:
        try:
            profile = await self.profile_repo.get(profile_id)

            if profile is None:
                return None

            for key, value in updated_data.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)

            return await self.profile_repo.save(profile)
        except Exception as e:
            logger.error(f"Ошибка обновления профиля: {e}")
            raise

    async def delete_profile(self, profile_id: uuid.UUID) -> bool:
        try:
            profile = await self.profile_repo.get(profile_id)

            if profile is None:
                return False

            await self.profile_repo.delete(profile)
            return True
        except Exception as e:
            logger.error(f"Ошибка удаления профиля: {e}")
            raise

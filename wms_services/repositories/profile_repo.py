from sqlalchemy.ext.asyncio import AsyncSession

from wms_services.models import ProfileModel
from wms_services.repositories.base_repo import BaseDBRepository

__all__ = ["ProfileDBRepository"]

class ProfileDBRepository(BaseDBRepository[ProfileModel]):

    def __init__(self,
                 session: AsyncSession,
                 *args, **kwargs):
        super().__init__(ProfileModel,
                         session,
                         *args, **kwargs)

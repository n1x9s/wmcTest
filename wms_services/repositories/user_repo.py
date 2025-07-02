from sqlalchemy.ext.asyncio import AsyncSession

from wms_services.models import User
from wms_services.repositories.base_repo import BaseDBRepository

__all__ = ["UserDBRepository"]

class UserDBRepository(BaseDBRepository[User]):

    def __init__(self,
                 session: AsyncSession,
                 *args, **kwargs):
        super().__init__(User,
                         session,
                         *args, **kwargs)

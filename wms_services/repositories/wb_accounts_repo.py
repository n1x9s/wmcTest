from sqlalchemy.ext.asyncio import AsyncSession

from wms_services.models import WBAccountModel
from wms_services.repositories.base_repo import BaseDBRepository

__all__ = ["WBAccountsDBRepo"]

class WBAccountsDBRepo(BaseDBRepository[WBAccountModel]):
    def __init__(self,
                 session: AsyncSession,
                 *args, **kwargs):
        super().__init__(WBAccountModel, session, *args, **kwargs)

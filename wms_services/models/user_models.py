import uuid
from enum import Enum as PyEnum

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Column, String, UUID, ForeignKey, JSON, DateTime, Integer
from sqlalchemy.orm import relationship

from wms_services.models.base_model import Base

__all__ = ["User", "ProfileModel", "WBAccountModel", "WBAccountStatus"]


class User(SQLAlchemyBaseUserTableUUID, Base):
    """Модель пользователя"""
    __table_args__ = {
        'comment': 'Модель пользователя',
    }

    first_name = Column(String(100), nullable=False,
                        comment="Имя")
    second_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False,
                        comment="Фамилия")
    role = Column(String(100), nullable=False, default='Пользователь',
                  comment="Роль пользователя")

    profile = relationship(
        "ProfileModel",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
        lazy="selectin"
    )



class ProfileModel(Base):
    """Модель профиля пользователя"""
    __tablename__ = 'profiles'
    __table_args__ = {
        'comment': 'Модель профиля пользователя',
    }

    id = Column(UUID, unique=True, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey('user.id', ondelete='CASCADE'), unique=True, nullable=False,
                     comment="ID пользователя, привязанного к профилю")

    user = relationship(
        "User",
        back_populates="profile",
        uselist=False,
        lazy="joined"
    )

    wb_accounts = relationship(
        "WBAccountModel",
        back_populates="profile",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin"
    )

    @property
    def full_name(self) -> str:
        return f"{self.user.first_name} {self.user.second_name} {self.user.last_name}"

class WBAccountStatus(PyEnum):
    INACTIVE = 0 # неактивный
    ACTIVE = 1 # активный
    NOT_CHECKED = 2 # не проверен

class WBAccountModel(Base):
    """Модель кабинета маркетплейса WB"""
    __tablename__ = "wb_accounts"
    __table_args__ = {
        'comment': 'Модель кабинета маркетплейса WB',
    }
    id = Column(UUID, unique=True, default=uuid.uuid4, primary_key=True)
    name = Column(String, server_default="Marketplace Account", nullable=False,
                  comment="Название кабинета")
    profile_id = Column(UUID, ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False,
                        comment="ID профиля владельца кабинета")
    wb_token = Column(String, nullable=False,
                      comment="Токен для доступа к API маркетплейса")
    token_metadata = Column(JSON, nullable=True,
                            comment="Мета-данные токена")
    status = Column(Integer,
                    server_default=str(WBAccountStatus.NOT_CHECKED.value),
                    default=WBAccountStatus.NOT_CHECKED.value, nullable=False,
                    comment="Статус кабинета. Может принимать значения: "
                            "INACTIVE (неактивный), ACTIVE (активный), NOT_CHECKED (не проверен)")
    details = Column(JSON, nullable=True,
                     comment="Мета-данные кабинета")

    last_token_validate_at = Column(DateTime, nullable=True,
                                    comment="Дата и время последней проверки токена")
    last_cards_sync_at = Column(DateTime, nullable=True,
                                comment="Дата и время последней синхронизации карточек")

    profile = relationship(
        "ProfileModel",
        back_populates="wb_accounts",
        lazy="selectin"
    )

import uuid
from sqlalchemy import Column, DateTime, func, UUID
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


__all__ = ["Base"]

# Здесь можно определить поля, которые общие для всех
class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
    
    id = Column(UUID, unique=True, primary_key=True, default=uuid.uuid4,
                comment="Уникальный идентификатор объекта")
    created_at = Column(DateTime,
                        default=func.now(),
                        server_default=func.now(),
                        nullable=False,
                        comment="Дата и время создания объекта")
    updated_at = Column(DateTime,
                        default=func.now(),
                        server_default=func.now(),
                        onupdate=func.now(),
                        nullable=False,
                        comment="Дата и время последнего обновления объекта")
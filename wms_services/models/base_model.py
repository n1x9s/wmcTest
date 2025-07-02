from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


__all__ = ["Base"]

# Здесь можно определить поля, которые общие для всех
# TODO: Перенести поля id
class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
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
from functools import wraps
from typing import TypeVar, Generic, Sequence, Any, Union

from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

AbstractModel = TypeVar('AbstractModel')


def rollback_wrapper(func):
    @wraps(func)
    async def inner(self, *args, **kwargs):

        try:
            return await func(self, *args, **kwargs)
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    return inner


class BaseDBRepository(Generic[AbstractModel]):
    type_model: type[AbstractModel]

    def __init__(self,
                 type_model: type[AbstractModel],
                 session: AsyncSession,
                 *args, **kwargs):
        self.type_model = type_model
        self.session = session

    @rollback_wrapper
    async def get(self,
                  ident: Any) -> AbstractModel | None:
        """Get an ONE model from the database with PK.
        TODO: Добавить параметр selectin или joinload для возможности подгрузки связанных моделей

        :param ident: Key which need to find entry in database
        :return:
        """

        return await self.session.get(entity=self.type_model, ident=ident)

    @rollback_wrapper
    async def get_where(self,
                        many: bool = False,
                        whereclause=None,
                        limit: int | None = None,
                        offset: int | None = None,
                        group_by=None,
                        order_by=None,
                        columns: list[Any] | None = None) -> Union[Sequence[AbstractModel], AbstractModel, Sequence[tuple], tuple, Sequence[Any], Any, None]:
        """Get an ONE model from the database with whereclause.
        :param offset:
        :param many:
        :param whereclause: Clause by which entry will be found
        :param limit: Number of elements per query
        :param group_by: Name of field for grouping
        :param order_by: Name of field for ordering
        :param columns: List of specific columns to select. If None, selects all columns.
                       Examples:
                       - [Model.name] - получить только поле name
                       - [Model.id, Model.name] - получить поля id и name
                       - [func.count(Model.id)] - получить количество записей
        :return: Model if only one model was found, else None.
                If columns specified, returns selected column values or tuples.
        """
        # Выбираем либо отдельные поля, либо всю модель
        if columns is not None:
            statement = select(*columns)
        else:
            statement = select(self.type_model)
            
        if whereclause is not None:
            statement = statement.where(whereclause)
        if limit is not None:
            statement = statement.limit(limit)
        if offset is not None:
            statement = statement.offset(offset)
        if order_by is not None:
            statement = statement.order_by(order_by)
        if group_by is not None:
            statement = statement.group_by(group_by)

        result = await self.session.execute(statement)
        
        # Если выбираем отдельные поля, возвращаем кортежи или отдельные значения
        if columns is not None:
            if len(columns) == 1:
                # Если выбран только один столбец, возвращаем значения напрямую
                return result.scalars().all() if many else result.scalar_one_or_none()
            else:
                # Если выбрано несколько столбцов, возвращаем кортежи
                return result.all() if many else result.first()
        else:
            # Если выбираем всю модель, возвращаем объекты модели
            return result.scalars().all() if many else result.scalar_one_or_none()

    @rollback_wrapper
    async def delete(
        self,
        obj: AbstractModel | Sequence[AbstractModel],
        many: bool = False
    ):
        # TODO: переделать, чтобы можно было по условию удалять, не получая все объекты

        if many and isinstance(obj, Sequence):
            for obj_item in obj:
                await self.session.delete(obj_item)
        else:
            await self.session.delete(obj)
        await self.session.commit()

    @rollback_wrapper
    async def save(
        self,
        obj: AbstractModel | Sequence[AbstractModel],
        many: bool = False
    ) -> AbstractModel | Sequence[AbstractModel]:
        """

        :param obj: object or objects to save
        :param many: flag for many saves
        :return:
        """
        if many:
            self.session.add_all(obj)
        else:
            self.session.add(obj)

        await self.session.commit()
        return await self.refresh(obj, many)

    @rollback_wrapper
    async def update(
        self,
        values: dict[str, Any],
        whereclause=None,
    ) -> int:
        stmt = (
            update(self.type_model)
            .where(whereclause)
            .values(values)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount

    @rollback_wrapper
    async def refresh(
            self,
            obj: AbstractModel | Sequence[AbstractModel],
            many: bool = False):
        if many:
            for obj_item in obj:
                await self.session.refresh(obj_item)
        else:
            await self.session.refresh(obj)
        return obj
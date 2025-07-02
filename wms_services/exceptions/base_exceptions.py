from typing import Any


class BaseServiceException(Exception):
    """Базовое исключение для всех сервисов"""


class BaseNotFoundError(BaseServiceException):
    """Базовое исключение для вызова, в случае если какой-то объект не найден"""


class BaseInactiveError(BaseServiceException):
    """Базовое исключение для вызова, если объект не активен и с ним нельзя производить действий,
     требующих активного статуса"""


class PermissionDenied(BaseServiceException):
    """Базовое исключение для ошибок с доступов к ресурсу"""


class BaseAlreadyExistsError(BaseServiceException):
    """Базовое исключение для ошибок, при попытке создать уже существующую сущность или связь между сущностями"""

class BaseBadRequestError(BaseServiceException):
    """Базовое исключение для некорректного запроса"""
    def __init__(self, errors: list[dict[str, Any]] | None = None, *args):
        if errors is None:
            errors = []
        self.errors = errors
        super().__init__(*args)

class BaseCreateError(BaseBadRequestError):
    """Базовое исключение для некорректного запроса при создании объекта"""

class BaseFileError(BaseServiceException):
    """Базовое исключение при работе с файлами"""

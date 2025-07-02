from wms_services.exceptions.base_exceptions import BaseNotFoundError, BaseInactiveError


class WbAccountNotFoundError(BaseNotFoundError):
    def __init__(self):
        super().__init__("Данный WB кабинет не найден")


class WbAccountInactiveError(BaseInactiveError):
    def __init__(self):
        super().__init__("Данный WB кабинет неактивен")

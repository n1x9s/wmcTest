import uuid

from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    first_name: str
    second_name: str
    last_name: str  # Отчество
    role: str


class UserCreate(schemas.BaseUserCreate):
    first_name: str
    second_name: str
    last_name: str  # Отчество


class UserUpdate(schemas.BaseUserUpdate):
    first_name: str
    second_name: str
    last_name: str  # Отчество
    role: str

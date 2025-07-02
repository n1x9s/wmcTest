import uuid

from pydantic import BaseModel

__all__ = ["BaseProfileSchema",
           "ProfileResponseSchema",
           "ProfileRequestSchema"]

class BaseProfileSchema(BaseModel):
    user_id: uuid.UUID

    class Config:
        from_attributes = True

class BaseUserSchema(BaseModel):
    first_name: str
    last_name: str
    second_name: str

    class Config:
        from_attributes = True


class RetrieveUserSchema(BaseUserSchema):
    pass

class ProfileRequestSchema(BaseProfileSchema):
    pass

class ProfileResponseSchema(BaseProfileSchema):
    id: uuid.UUID
    user: RetrieveUserSchema

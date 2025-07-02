import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

__all__ = ["BaseWBAccountSchema",
           "CreateWBAccountSchema",
           "UpdateWBAccountSchema",
           "ResponseWBAccountSchema"]


class BaseWBAccountSchema(BaseModel):
    name: str
    wb_token: str
    details: Optional[dict] = None


class CreateWBAccountSchema(BaseWBAccountSchema):
    pass


class UpdateWBAccountSchema(BaseWBAccountSchema):
    wb_token: str | None = None


class ResponseWBAccountSchema(BaseWBAccountSchema):
    model_config = ConfigDict(from_attributes=True)

    wb_token: str = Field(..., exclude=True)
    id: uuid.UUID
    profile_id: uuid.UUID
    created_at: datetime.datetime
    token_metadata: dict | None = None
    status: int
    last_token_validate_at: datetime.datetime | None = None
    last_cards_sync_at: datetime.datetime | None = None

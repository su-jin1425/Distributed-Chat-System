import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator
from app.models.message import MessageType
from app.models.message_status import DeliveryStatus
from app.schemas.user import UserResponse


class MessageCreate(BaseModel):
    room_id: uuid.UUID
    content: str
    message_type: MessageType = MessageType.TEXT
    parent_id: uuid.UUID | None = None

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Message content cannot be empty")
        if len(v) > 4000:
            raise ValueError("Message content must not exceed 4000 characters")
        return v


class MessageUpdate(BaseModel):
    content: str | None = None


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    room_id: uuid.UUID
    sender_id: uuid.UUID | None = None
    content: str
    message_type: MessageType
    parent_id: uuid.UUID | None = None
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    sender: UserResponse | None = None


class MessageStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    message_id: uuid.UUID
    user_id: uuid.UUID
    status: DeliveryStatus
    updated_at: datetime


class PaginatedMessages(BaseModel):
    items: list[MessageResponse]
    total: int
    page: int
    page_size: int
    has_more: bool

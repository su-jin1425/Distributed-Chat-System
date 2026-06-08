import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.chat_room import RoomType
from app.models.room_member import MemberRole


class RoomCreate(BaseModel):
    name: str
    description: str | None = None
    room_type: RoomType = RoomType.PUBLIC


class RoomUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_archived: bool | None = None


class RoomResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None = None
    room_type: RoomType
    created_by: uuid.UUID | None = None
    is_archived: bool
    created_at: datetime
    member_count: int | None = None


class RoomMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    room_id: uuid.UUID
    user_id: uuid.UUID
    role: MemberRole
    created_at: datetime


class AddMemberRequest(BaseModel):
    user_id: uuid.UUID
    role: MemberRole = MemberRole.MEMBER

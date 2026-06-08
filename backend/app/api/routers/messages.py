import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.api.deps import get_current_active_user, get_db
from app.core.redis_client import get_redis_dep
from app.models.user import User
from app.models.message_status import DeliveryStatus
from app.schemas.message import (
    MessageCreate,
    MessageResponse,
    MessageUpdate,
    PaginatedMessages,
    MessageStatusResponse,
)
from app.services.message_service import MessageService

router = APIRouter()


@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    message_in: MessageCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis_dep),
) -> MessageResponse:
    msg_service = MessageService(session, redis)
    return await msg_service.create_message(current_user.id, message_in)


@router.get("/room/{room_id}", response_model=PaginatedMessages)
async def read_room_messages(
    room_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis_dep),
) -> PaginatedMessages:
    msg_service = MessageService(session, redis)
    messages = await msg_service.get_room_messages(current_user.id, room_id, skip, limit)
    
    # We simplified pagination for this endpoint
    return PaginatedMessages(
        items=messages,
        total=len(messages),  # In real app, separate count query
        page=skip // limit + 1,
        page_size=limit,
        has_more=len(messages) == limit,
    )


@router.patch("/{message_id}", response_model=MessageResponse)
async def update_message(
    message_id: uuid.UUID,
    message_in: MessageUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis_dep),
) -> MessageResponse:
    msg_service = MessageService(session, redis)
    return await msg_service.update_message(current_user.id, message_id, message_in)


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis_dep),
) -> None:
    msg_service = MessageService(session, redis)
    await msg_service.delete_message(current_user.id, message_id)


@router.post("/{message_id}/status", response_model=MessageStatusResponse)
async def update_message_status(
    message_id: uuid.UUID,
    status_val: DeliveryStatus = Query(...),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis_dep),
) -> MessageStatusResponse:
    msg_service = MessageService(session, redis)
    return await msg_service.update_status(current_user.id, message_id, status_val)

import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.room import (
    RoomCreate,
    RoomResponse,
    RoomUpdate,
    RoomMemberResponse,
    AddMemberRequest,
)
from app.services.room_service import RoomService

router = APIRouter()


@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    room_in: RoomCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_db),
) -> RoomResponse:
    room_service = RoomService(session)
    return await room_service.create_room(current_user.id, room_in)


@router.get("/", response_model=list[RoomResponse])
async def read_user_rooms(
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_db),
) -> list[RoomResponse]:
    room_service = RoomService(session)
    return await room_service.get_user_rooms(current_user.id)


@router.get("/{room_id}", response_model=RoomResponse)
async def read_room(
    room_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_db),
) -> RoomResponse:
    room_service = RoomService(session)
    # Get room + verify access indirectly via members or let service handle it
    # Simplified here, but we should check if user is a member
    room = await room_service.get_room(room_id)
    return room


@router.patch("/{room_id}", response_model=RoomResponse)
async def update_room(
    room_id: uuid.UUID,
    room_in: RoomUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_db),
) -> RoomResponse:
    room_service = RoomService(session)
    return await room_service.update_room(current_user.id, room_id, room_in)


@router.get("/{room_id}/members", response_model=list[RoomMemberResponse])
async def read_room_members(
    room_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_db),
) -> list[RoomMemberResponse]:
    room_service = RoomService(session)
    return await room_service.get_members(room_id)


@router.post("/{room_id}/members", response_model=RoomMemberResponse)
async def add_room_member(
    room_id: uuid.UUID,
    req: AddMemberRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_db),
) -> RoomMemberResponse:
    room_service = RoomService(session)
    return await room_service.add_member(current_user.id, room_id, req)


@router.delete("/{room_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_room_member(
    room_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_db),
) -> None:
    room_service = RoomService(session)
    await room_service.remove_member(current_user.id, room_id, user_id)

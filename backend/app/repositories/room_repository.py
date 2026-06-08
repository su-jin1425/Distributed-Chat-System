import uuid
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat_room import ChatRoom, RoomType
from app.models.room_member import RoomMember, MemberRole
from app.repositories.base import BaseRepository


class RoomRepository(BaseRepository[ChatRoom]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ChatRoom)

    async def get_by_id(self, room_id: uuid.UUID) -> ChatRoom | None:
        result = await self._session.execute(
            select(ChatRoom).where(ChatRoom.id == room_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        name: str,
        room_type: RoomType,
        created_by: uuid.UUID | None = None,
        description: str | None = None,
    ) -> ChatRoom:
        room = ChatRoom(
            name=name,
            room_type=room_type,
            created_by=created_by,
            description=description,
        )
        self._session.add(room)
        await self._session.flush()
        await self._session.refresh(room)
        return room

    async def update(self, room: ChatRoom, **kwargs) -> ChatRoom:
        for key, value in kwargs.items():
            if hasattr(room, key) and value is not None:
                setattr(room, key, value)
        self._session.add(room)
        await self._session.flush()
        await self._session.refresh(room)
        return room

    async def add_member(
        self, room_id: uuid.UUID, user_id: uuid.UUID, role: MemberRole
    ) -> RoomMember:
        member = RoomMember(room_id=room_id, user_id=user_id, role=role)
        self._session.add(member)
        await self._session.flush()
        await self._session.refresh(member)
        return member

    async def get_member(
        self, room_id: uuid.UUID, user_id: uuid.UUID
    ) -> RoomMember | None:
        result = await self._session.execute(
            select(RoomMember).where(
                and_(
                    RoomMember.room_id == room_id,
                    RoomMember.user_id == user_id,
                    RoomMember.is_active.is_(True),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_members(self, room_id: uuid.UUID) -> list[RoomMember]:
        result = await self._session.execute(
            select(RoomMember)
            .where(
                and_(RoomMember.room_id == room_id, RoomMember.is_active.is_(True))
            )
            .options(selectinload(RoomMember.user))
        )
        return list(result.scalars().all())

    async def get_user_rooms(self, user_id: uuid.UUID) -> list[ChatRoom]:
        result = await self._session.execute(
            select(ChatRoom)
            .join(RoomMember, ChatRoom.id == RoomMember.room_id)
            .where(
                and_(
                    RoomMember.user_id == user_id,
                    RoomMember.is_active.is_(True),
                    ChatRoom.is_archived.is_(False),
                )
            )
        )
        return list(result.scalars().all())

    async def remove_member(self, room_id: uuid.UUID, user_id: uuid.UUID) -> None:
        member = await self.get_member(room_id, user_id)
        if member:
            member.is_active = False
            self._session.add(member)
            await self._session.flush()

    async def count_total(self) -> int:
        result = await self._session.execute(select(func.count()).select_from(ChatRoom))
        return result.scalar_one()

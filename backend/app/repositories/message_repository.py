import uuid
from sqlalchemy import select, and_, desc, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.message import Message, MessageType
from app.models.message_status import MessageStatus, DeliveryStatus
from app.repositories.base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Message)

    async def get_by_id(self, message_id: uuid.UUID) -> Message | None:
        result = await self._session.execute(
            select(Message)
            .where(Message.id == message_id)
            .options(selectinload(Message.sender))
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        room_id: uuid.UUID,
        sender_id: uuid.UUID | None,
        content: str,
        message_type: MessageType = MessageType.TEXT,
        parent_id: uuid.UUID | None = None,
    ) -> Message:
        message = Message(
            room_id=room_id,
            sender_id=sender_id,
            content=content,
            message_type=message_type,
            parent_id=parent_id,
        )
        self._session.add(message)
        await self._session.flush()
        await self._session.refresh(message)
        
        # Reload to get relationships populated if needed, or caller handles it
        return message

    async def get_room_messages(
        self, room_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> list[Message]:
        result = await self._session.execute(
            select(Message)
            .where(and_(Message.room_id == room_id, Message.is_deleted.is_(False)))
            .order_by(desc(Message.created_at))
            .offset(skip)
            .limit(limit)
            .options(selectinload(Message.sender))
        )
        # Return in ascending chronological order for clients
        return list(reversed(result.scalars().all()))

    async def update_status(
        self, message_id: uuid.UUID, user_id: uuid.UUID, status: DeliveryStatus
    ) -> MessageStatus:
        result = await self._session.execute(
            select(MessageStatus).where(
                and_(
                    MessageStatus.message_id == message_id,
                    MessageStatus.user_id == user_id,
                )
            )
        )
        msg_status = result.scalar_one_or_none()
        
        if msg_status:
            msg_status.status = status
        else:
            msg_status = MessageStatus(
                message_id=message_id, user_id=user_id, status=status
            )
            
        self._session.add(msg_status)
        await self._session.flush()
        await self._session.refresh(msg_status)
        return msg_status

    async def get_message_statuses(self, message_id: uuid.UUID) -> list[MessageStatus]:
        result = await self._session.execute(
            select(MessageStatus).where(MessageStatus.message_id == message_id)
        )
        return list(result.scalars().all())

    async def count_total(self) -> int:
        result = await self._session.execute(select(func.count()).select_from(Message))
        return result.scalar_one()

    async def delete(self, message: Message) -> None:
        message.is_deleted = True
        self._session.add(message)
        await self._session.flush()

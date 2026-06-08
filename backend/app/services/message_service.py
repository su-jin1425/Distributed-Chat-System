import json
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from redis.asyncio import Redis
from app.repositories.message_repository import MessageRepository
from app.repositories.room_repository import RoomRepository
from app.schemas.message import MessageCreate, MessageUpdate
from app.models.message import Message
from app.models.message_status import DeliveryStatus, MessageStatus
from app.core.redis_client import RedisKeys


class MessageService:
    def __init__(self, session: AsyncSession, redis: Redis) -> None:
        self.session = session
        self.redis = redis
        self.message_repo = MessageRepository(session)
        self.room_repo = RoomRepository(session)

    async def create_message(
        self, user_id: uuid.UUID, message_in: MessageCreate
    ) -> Message:
        # Check permissions
        member = await self.room_repo.get_member(message_in.room_id, user_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this room",
            )
            
        message = await self.message_repo.create(
            room_id=message_in.room_id,
            sender_id=user_id,
            content=message_in.content,
            message_type=message_in.message_type,
            parent_id=message_in.parent_id,
        )
        
        # Initial status for sender
        await self.message_repo.update_status(
            message_id=message.id, user_id=user_id, status=DeliveryStatus.READ
        )

        # Publish to Redis
        await self._publish_to_redis("message.created", message)
        
        return message

    async def get_room_messages(
        self, user_id: uuid.UUID, room_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> list[Message]:
        member = await self.room_repo.get_member(room_id, user_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this room",
            )
            
        return await self.message_repo.get_room_messages(room_id, skip, limit)

    async def update_message(
        self, user_id: uuid.UUID, message_id: uuid.UUID, message_in: MessageUpdate
    ) -> Message:
        message = await self.message_repo.get_by_id(message_id)
        if not message or message.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Message not found"
            )
            
        if message.sender_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to edit this message",
            )
            
        if message_in.content is not None:
            message.content = message_in.content
            self.session.add(message)
            await self.session.flush()
            
            await self._publish_to_redis("message.updated", message)
            
        return message

    async def delete_message(self, user_id: uuid.UUID, message_id: uuid.UUID) -> None:
        message = await self.message_repo.get_by_id(message_id)
        if not message or message.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Message not found"
            )
            
        if message.sender_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this message",
            )
            
        await self.message_repo.delete(message)
        await self._publish_to_redis("message.deleted", message)

    async def update_status(
        self, user_id: uuid.UUID, message_id: uuid.UUID, status: DeliveryStatus
    ) -> MessageStatus:
        message = await self.message_repo.get_by_id(message_id)
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Message not found"
            )
            
        member = await self.room_repo.get_member(message.room_id, user_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this room",
            )
            
        msg_status = await self.message_repo.update_status(message_id, user_id, status)
        
        # Publish status update
        event_data = {
            "type": "status.updated",
            "message_id": str(message_id),
            "room_id": str(message.room_id),
            "user_id": str(user_id),
            "status": status.value,
        }
        await self.redis.publish("chat_events", json.dumps(event_data))
        
        return msg_status

    async def _publish_to_redis(self, event_type: str, message: Message) -> None:
        event_data = {
            "type": event_type,
            "message": {
                "id": str(message.id),
                "room_id": str(message.room_id),
                "sender_id": str(message.sender_id) if message.sender_id else None,
                "content": message.content,
                "message_type": message.message_type.value,
                "parent_id": str(message.parent_id) if message.parent_id else None,
                "created_at": message.created_at.isoformat(),
            }
        }
        await self.redis.publish("chat_events", json.dumps(event_data))

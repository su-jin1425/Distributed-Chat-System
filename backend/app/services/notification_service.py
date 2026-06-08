import json
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from app.repositories.notification_repository import NotificationRepository
from app.models.notification import Notification, NotificationType


class NotificationService:
    def __init__(self, session: AsyncSession, redis: Redis) -> None:
        self.session = session
        self.redis = redis
        self.notification_repo = NotificationRepository(session)

    async def create_notification(
        self, user_id: uuid.UUID, type_: NotificationType, payload: dict
    ) -> Notification:
        notification = await self.notification_repo.create(
            user_id=user_id, notification_type=type_, payload=payload
        )
        
        event_data = {
            "type": "notification.created",
            "user_id": str(user_id),
            "notification": {
                "id": str(notification.id),
                "type": type_.value,
                "payload": payload,
                "created_at": notification.created_at.isoformat(),
            }
        }
        await self.redis.publish("notification_events", json.dumps(event_data))
        
        return notification

    async def get_user_notifications(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> list[Notification]:
        return await self.notification_repo.get_user_notifications(user_id, skip, limit)

    async def get_unread_count(self, user_id: uuid.UUID) -> int:
        return await self.notification_repo.get_unread_count(user_id)

    async def mark_as_read(self, user_id: uuid.UUID, notification_id: uuid.UUID) -> None:
        await self.notification_repo.mark_as_read(notification_id, user_id)

    async def mark_all_as_read(self, user_id: uuid.UUID) -> None:
        await self.notification_repo.mark_all_as_read(user_id)

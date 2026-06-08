import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.api.deps import get_current_active_user, get_db
from app.core.redis_client import get_redis_dep
from app.models.user import User
from app.schemas.notification import PaginatedNotifications
from app.services.notification_service import NotificationService

router = APIRouter()


@router.get("/", response_model=PaginatedNotifications)
async def read_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis_dep),
) -> PaginatedNotifications:
    notif_service = NotificationService(session, redis)
    notifications = await notif_service.get_user_notifications(current_user.id, skip, limit)
    unread_count = await notif_service.get_unread_count(current_user.id)
    
    return PaginatedNotifications(
        items=notifications,
        total=len(notifications),
        unread_count=unread_count,
    )


@router.post("/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_as_read(
    notification_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis_dep),
) -> None:
    notif_service = NotificationService(session, redis)
    await notif_service.mark_as_read(current_user.id, notification_id)


@router.post("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_as_read(
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis_dep),
) -> None:
    notif_service = NotificationService(session, redis)
    await notif_service.mark_all_as_read(current_user.id)

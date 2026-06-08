import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    messages = relationship("Message", back_populates="sender", lazy="dynamic")
    room_memberships = relationship(
        "RoomMember", back_populates="user", lazy="dynamic"
    )
    notifications = relationship(
        "Notification", back_populates="user", lazy="dynamic"
    )
    refresh_tokens = relationship(
        "RefreshToken", back_populates="user", lazy="dynamic"
    )
    audit_logs = relationship("AuditLog", back_populates="actor", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username}>"

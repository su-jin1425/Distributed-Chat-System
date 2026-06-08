import uuid
from datetime import datetime
from sqlalchemy import DateTime, Float, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class ExecutionMetric(Base):
    __tablename__ = "execution_metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    websocket_connections: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    message_latency_ms: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0
    )
    delivery_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    queue_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

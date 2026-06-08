from datetime import datetime
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    environment: str
    database: str
    redis: str
    timestamp: datetime


class MetricsResponse(BaseModel):
    websocket_connections: int
    message_latency_ms: float
    delivery_rate: float
    queue_size: int
    active_users: int
    total_rooms: int
    total_messages: int


class ConnectionsResponse(BaseModel):
    active_connections: int
    connections_by_room: dict[str, int]

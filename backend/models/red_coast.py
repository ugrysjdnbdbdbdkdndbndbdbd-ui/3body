"""红岸控制台 (Red Coast) 模型."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy import String, Text, Integer, DateTime, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class SignalORM(Base):
    """红岸信号."""
    __tablename__ = "red_coast_signals"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_type: Mapped[str] = mapped_column(String(32))  # user | ai | system
    frequency: Mapped[float] = mapped_column(default=1420.0) # MHz
    content_encrypted: Mapped[str] = mapped_column(Text())
    content_decrypted: Mapped[str] = mapped_column(Text())
    power_level: Mapped[str] = mapped_column(String(32), default="low") # low | high
    integrity: Mapped[float] = mapped_column(default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SignalBase(BaseModel):
    source_type: str
    frequency: float
    content_decrypted: str
    power_level: str = "low"


class SignalCreate(SignalBase):
    pass


class SignalRead(SignalBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    content_encrypted: str
    integrity: float
    created_at: Optional[datetime] = None

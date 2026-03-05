"""小宇宙 (Universe 647) 模型."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy import String, Text, Integer, DateTime, func, Float
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class MiniUniverseORM(Base):
    """个人小宇宙数据 (User/Session-based)."""
    __tablename__ = "mini_universes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True, unique=True)  # 简化的用户标识 (IP or Session)
    mass: Mapped[float] = mapped_column(Float, default=5.0)  # 初始 5kg (程心的五公斤)
    items: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)  # JSON: 收藏品/植物
    notes: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)  # JSON: 时间胶囊/日记
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MiniUniverseBase(BaseModel):
    user_id: str
    mass: float = 5.0
    items: Optional[str] = None
    notes: Optional[str] = None


class MiniUniverseRead(MiniUniverseBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: Optional[datetime] = None


class MiniUniverseUpdate(BaseModel):
    mass_change: Optional[float] = None
    note_add: Optional[str] = None
    item_add: Optional[str] = None
    action: Optional[str] = None # "return_mass"

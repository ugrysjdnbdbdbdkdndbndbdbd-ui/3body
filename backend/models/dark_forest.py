"""黑暗森林广场 (Dark Forest) 模型."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy import String, Text, Integer, DateTime, func, Float
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class ForestStarORM(Base):
    """黑暗森林中的星星 (帖子)."""
    __tablename__ = "forest_stars"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    author_id: Mapped[str] = mapped_column(String(64), index=True) # 匿名ID或加密ID
    content: Mapped[str] = mapped_column(Text())
    mass: Mapped[float] = mapped_column(Float, default=10.0) # 质量/亮度/HP
    brightness: Mapped[float] = mapped_column(Float, default=1.0) # 可见度
    status: Mapped[str] = mapped_column(String(32), default="active") # active, destroyed, flattened
    x: Mapped[float] = mapped_column(Float, default=0.0)
    y: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ForestStarBase(BaseModel):
    content: str
    author_id: str = "anonymous"
    x: float = 0.0
    y: float = 0.0


class ForestStarCreate(ForestStarBase):
    pass


class ForestStarRead(ForestStarBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    mass: float
    brightness: float
    status: str
    created_at: Optional[datetime] = None

"""二向箔画廊 - AIGC 图/视频."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class GalleryItemORM(Base):
    """画廊条目 ORM 表."""

    __tablename__ = "gallery_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(256))
    description: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    media_url: Mapped[str] = mapped_column(String(512))  # 图或视频 URL
    media_type: Mapped[str] = mapped_column(String(32), default="image")  # image | video
    prompt_text: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)  # AIGC Prompt 实验室
    # Phase 3: 黑暗森林过滤
    status: Mapped[str] = mapped_column(String(32), default="normal")  # normal | exposed | cleansed
    logic_score: Mapped[float] = mapped_column(default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# Pydantic schemas
class GalleryItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    media_url: str
    media_type: str = "image"
    prompt_text: Optional[str] = None
    status: str = "normal"
    logic_score: float = 1.0


class GalleryItemCreate(GalleryItemBase):
    pass


class GalleryItemRead(GalleryItemBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: Optional[datetime] = None


GalleryItem = GalleryItemORM

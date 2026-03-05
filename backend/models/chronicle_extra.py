"""编年史扩展模型 (Archive & Wiki)."""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict
from sqlalchemy import String, Text, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class ArchiveDocumentORM(Base):
    """宇宙档案馆文档."""
    __tablename__ = "chronicle_archives"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(256))
    classification: Mapped[str] = mapped_column(String(32), default="CONFIDENTIAL") # TOP_SECRET, CONFIDENTIAL, PUBLIC
    content_markdown: Mapped[str] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class WikiEntryORM(Base):
    """三体百科词条."""
    __tablename__ = "chronicle_wiki"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    term: Mapped[str] = mapped_column(String(64), index=True)
    category: Mapped[str] = mapped_column(String(32)) # Civilization, Tech, Phenomena, Facility
    summary: Mapped[str] = mapped_column(String(512))
    content_markdown: Mapped[str] = mapped_column(Text())
    visual_effect: Mapped[Optional[str]] = mapped_column(String(32), nullable=True) # flatten, glitch, 4d_rotate
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ArchiveRead(BaseModel):
    id: int
    title: str
    classification: str
    content_markdown: str
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class WikiRead(BaseModel):
    id: int
    term: str
    category: str
    summary: str
    content_markdown: str
    visual_effect: Optional[str] = None
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

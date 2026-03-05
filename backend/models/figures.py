"""三体人物志模型."""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict
from sqlalchemy import String, Text, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class FigureORM(Base):
    """人物志 ORM 表."""
    __tablename__ = "figures"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), index=True)
    en_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    role: Mapped[str] = mapped_column(String(64))  # 面壁者/ETO统帅/执剑人...
    era: Mapped[str] = mapped_column(String(64))   # 活跃主要纪元
    status: Mapped[str] = mapped_column(String(32), default="active") # active, hibernating, deceased
    description: Mapped[str] = mapped_column(Text())
    image_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    quotes: Mapped[Optional[str]] = mapped_column(Text(), nullable=True) # JSON list or newline separated
    logic_score: Mapped[float] = mapped_column(default=1.0) # 智子评估威胁度
    # PRD 1.1 新增
    metrics: Mapped[Optional[str]] = mapped_column(Text(), nullable=True) # JSON: { alienation, deterrence, empathy, rationality }
    key_events: Mapped[Optional[str]] = mapped_column(Text(), nullable=True) # JSON: [{ role, impact_description }]
    # 人物志扩展：关键决策、人物关系、关键语录（结构化）
    key_decisions: Mapped[Optional[str]] = mapped_column(Text(), nullable=True) # JSON: [{ decision, context, outcome }]
    relationships: Mapped[Optional[str]] = mapped_column(Text(), nullable=True) # JSON: [{ target, relation_type, description }]
    key_quotes: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)   # JSON: [{ quote, context }]，与 quotes 可并存
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class FigureBase(BaseModel):
    name: str
    en_name: Optional[str] = None
    role: str
    era: str
    status: str = "active"
    description: str
    image_url: Optional[str] = None
    quotes: Optional[str] = None
    logic_score: float = 1.0
    metrics: Optional[str] = None
    key_events: Optional[str] = None
    key_decisions: Optional[str] = None
    relationships: Optional[str] = None
    key_quotes: Optional[str] = None


class FigureCreate(FigureBase):
    pass


class FigureRead(FigureBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: Optional[datetime] = None

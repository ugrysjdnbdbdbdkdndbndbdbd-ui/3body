"""思想钢印 (Mental Seal) 模型."""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict
from sqlalchemy import String, Text, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class MentalSealSessionORM(Base):
    """面壁计划对决会话."""
    __tablename__ = "mental_seal_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    plan_title: Mapped[str] = mapped_column(String(256))
    plan_content: Mapped[str] = mapped_column(Text())
    # 状态: active, broken (被破壁), success (执剑成功)
    status: Mapped[str] = mapped_column(String(32), default="active")
    # 历史记录: JSON list of { role: "user"|"breaker_1"|"breaker_2"|"breaker_3", content: "...", timestamp: "..." }
    history: Mapped[str] = mapped_column(Text(), default="[]")
    round_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class UserSealORM(Base):
    """用户思想钢印状态."""
    __tablename__ = "user_seals"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    seal_type: Mapped[str] = mapped_column(String(32)) # TRIUMPH | DEFEAT | ADVENT | SURVIVE
    imprinted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    strength: Mapped[int] = mapped_column(Integer, default=100)


class SessionBase(BaseModel):
    user_id: str
    plan_title: str
    plan_content: str
    status: str = "active"
    history: str = "[]"
    round_count: int = 0


class SessionCreate(BaseModel):
    plan_title: str
    plan_content: str


class SessionRead(SessionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: Optional[datetime] = None


class DebateMove(BaseModel):
    session_id: int
    content: str


class SealCreate(BaseModel):
    seal_type: str


class SealRead(BaseModel):
    seal_type: str
    imprinted_at: datetime
    strength: int
    model_config = ConfigDict(from_attributes=True)

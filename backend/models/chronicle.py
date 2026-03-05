"""三体编年史 - 时间轴事件。零点计划：因果律时间轴（概率云/坍缩）。"""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, computed_field, model_validator
from sqlalchemy import String, Text, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base

# 零点计划：因果律状态 — 叠加态（未达互动阈值）/ 已坍缩（并入主时间轴）
CAUSALITY_SUPERPOSITION = "superposition"
CAUSALITY_COLLAPSED = "collapsed"
DEFAULT_COLLAPSE_THRESHOLD = 5

# 纪元起点公元年（与 frontend constants.ERA_CE_BASE 保持一致，用于 year_ce 计算）
ERA_CE_BASE = {
    "危机纪元": 2015,
    "威慑纪元": 2212,
    "掩体纪元": 2270,
    "广播纪元": 2400,
    "乱纪元": 2500,
    "银河纪元": 2687,
}


class ChronicleEventORM(Base):
    """编年史事件 ORM 表."""

    __tablename__ = "chronicle_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    era: Mapped[str] = mapped_column(String(64), index=True)
    year: Mapped[int] = mapped_column(Integer, index=True)
    title: Mapped[str] = mapped_column(String(256))
    content: Mapped[str] = mapped_column(Text())
    summary: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    event_type: Mapped[str] = mapped_column(String(32), default="pgc")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # 零点计划：因果律时间轴
    causality_status: Mapped[str] = mapped_column(String(32), default=CAUSALITY_COLLAPSED)  # superposition | collapsed
    interaction_count: Mapped[int] = mapped_column(Integer, default=0)
    collapse_threshold: Mapped[int] = mapped_column(Integer, default=DEFAULT_COLLAPSE_THRESHOLD)
    parent_node_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 因果溯源
    variant_source: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)  # JSON: 变数来源 [{ user_id, action, timestamp }]


# Pydantic schemas
class ChronicleEventBase(BaseModel):
    era: str
    year: int
    title: str
    content: str
    summary: Optional[str] = None
    image_url: Optional[str] = None
    event_type: str = "pgc"


class ChronicleEventCreate(ChronicleEventBase):
    pass


class ChronicleEventUpdate(BaseModel):
    """更新编年史事件请求体."""
    era: Optional[str] = None
    year: Optional[int] = None
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    image_url: Optional[str] = None
    event_type: Optional[str] = None
    causality_status: Optional[str] = None
    collapse_threshold: Optional[int] = None
    interaction_count: Optional[int] = None


class ChronicleEventRead(ChronicleEventBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: Optional[datetime] = None
    causality_status: str = CAUSALITY_COLLAPSED
    interaction_count: int = 0
    collapse_threshold: int = DEFAULT_COLLAPSE_THRESHOLD
    parent_node_id: Optional[int] = None
    variant_source: Optional[str] = None  # JSON

    @computed_field
    @property
    def year_ce(self) -> int:
        """公元纪年，与时间轴展示一致。黄金时代 year 即公元年；其余为 纪元起点 + 纪元内年。"""
        if self.era == "黄金时代":
            return self.year
        return ERA_CE_BASE.get(self.era, 2000) + self.year

    @model_validator(mode="before")
    @classmethod
    def _fill_causality_defaults(cls, data: Any) -> Any:
        """从 ORM 读取时若新列为 NULL（旧数据或迁移前），填入默认值."""
        if isinstance(data, dict):
            d = dict(data)
        else:
            _keys = (
                "id", "era", "year", "title", "content", "summary", "image_url",
                "event_type", "created_at", "causality_status", "interaction_count",
                "collapse_threshold", "parent_node_id", "variant_source",
            )
            d = {k: getattr(data, k, None) for k in _keys}
        if d.get("causality_status") is None:
            d["causality_status"] = CAUSALITY_COLLAPSED
        if d.get("interaction_count") is None:
            d["interaction_count"] = 0
        if d.get("collapse_threshold") is None:
            d["collapse_threshold"] = DEFAULT_COLLAPSE_THRESHOLD
        return d


# 兼容导出
ChronicleEvent = ChronicleEventORM

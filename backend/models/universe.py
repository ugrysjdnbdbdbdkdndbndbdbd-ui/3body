"""宇宙全局状态模型 (Universe State)."""
from datetime import datetime
from sqlalchemy import String, Float, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from backend.database import Base

class UniverseStateORM(Base):
    """宇宙全局状态单例表 (id=1)."""
    __tablename__ = "universe_state"

    id: Mapped[int] = mapped_column(primary_key=True)
    dark_forest_deterrence: Mapped[float] = mapped_column(Float, default=0.5)
    resonance_state: Mapped[str] = mapped_column(String(32), default="3d")  # 3d | 2d | 1d
    broadcast_enabled: Mapped[bool] = mapped_column(default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

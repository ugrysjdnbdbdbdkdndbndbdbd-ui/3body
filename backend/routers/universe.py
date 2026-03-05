"""宇宙广播 - Dashboard 动态数据（模拟 HUD），PRD Sector Gamma."""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.cache import cache_get, cache_set
from backend.database import get_db
from backend.models.universe import UniverseStateORM

router = APIRouter()
METRICS_CACHE_KEY = "universe:metrics"
METRICS_CACHE_TTL = 5  # 秒，仪表盘可接受短延迟

FLEET_VOYAGE_YEARS = 400


class UniverseMetrics(BaseModel):
    """宇宙广播指标."""
    dark_forest_deterrence: float
    trisolaran_fleet_distance_ly: float
    fleet_years_remaining: float
    current_era: str
    shelter_population: int
    timestamp: str
    resonance_state: str = "3d"
    # 零点计划 Phase 1.2: 环境系统
    environment_state: str = "stable"  # stable | cold | heat | rip
    temperature: float = 293.0  # Kelvin (avg)
    gravity: float = 1.0  # G


def calculate_environment(t: float):
    import math
    # 模拟三体运动混沌度 (Cycle approx 120s)
    chaos = math.sin(t / 20) + 0.5 * math.sin(t / 7) + 0.2 * math.cos(t / 3)
    
    # 默认恒纪元
    state = "stable"
    temp = 293.0 + chaos * 10
    g = 1.0
    
    if chaos > 1.2:
        state = "heat"
        temp = 350.0 + (chaos - 1.2) * 100
    elif chaos < -1.0:
        state = "cold"
        temp = 200.0 + (chaos + 1.0) * 50
    elif abs(chaos) < 0.1 and int(t) % 60 > 55:
        # 偶发大撕裂
        state = "rip"
        g = 0.0
        
    return state, round(temp, 1), round(g, 2)


class ResonanceUpdate(BaseModel):
    state: str  # 3d | 2d | 1d


@router.get("/metrics", response_model=UniverseMetrics)
async def get_metrics(db: AsyncSession = Depends(get_db)):
    """返回宇宙实时状态 (DB Persistence)；短期缓存以提升首屏加载."""
    cached = cache_get(METRICS_CACHE_KEY, METRICS_CACHE_TTL)
    if cached is not None:
        return cached
    # 获取或初始化状态
    result = await db.execute(select(UniverseStateORM).where(UniverseStateORM.id == 1))
    state = result.scalar_one_or_none()
    if not state:
        state = UniverseStateORM(id=1, dark_forest_deterrence=0.5, resonance_state="3d")
        db.add(state)
        await db.commit()
        await db.refresh(state)

    # 动态计算部分 (仅演示用，实际可由 Task 更新 DB)
    import math
    t = datetime.utcnow().timestamp()
    
    # 若 Deterrence 为默认值，叠加波动；否则使用 DB 值
    deterrence = state.dark_forest_deterrence
    if 0.49 < deterrence < 0.51:
        deterrence = 0.5 + 0.45 * math.sin(t / 60)
        
    # 同步计算 resonance (如果 DB 未强制锁定)
    # 这里我们优先使用 DB 的 resonance_state（由 Sector X 控制）
    
    years_elapsed = (t % (FLEET_VOYAGE_YEARS * 3.15576e7)) / 3.15576e7
    years_elapsed = min(years_elapsed, FLEET_VOYAGE_YEARS - 0.1)
    years_remaining = FLEET_VOYAGE_YEARS - years_elapsed
    
    env_state, temp, gravity = calculate_environment(t)

    out = UniverseMetrics(
        dark_forest_deterrence=round(deterrence, 4),
        trisolaran_fleet_distance_ly=round(4.2 - 0.01 * (t % 100), 2),
        fleet_years_remaining=round(years_remaining, 1),
        current_era="威慑纪元" if deterrence > 0.5 else "危机纪元",
        shelter_population=114_259 + int(t) % 1000,
        timestamp=datetime.utcnow().isoformat() + "Z",
        resonance_state=state.resonance_state,
        environment_state=env_state,
        temperature=temp,
        gravity=gravity,
    )
    cache_set(METRICS_CACHE_KEY, out, METRICS_CACHE_TTL)
    return out


@router.post("/resonance")
async def set_resonance(body: ResonanceUpdate, db: AsyncSession = Depends(get_db)):
    """手动触发全服共振 (Sector X)."""
    if body.state not in ["3d", "2d", "1d"]:
        raise HTTPException(400, "Invalid state")
        
    result = await db.execute(select(UniverseStateORM).where(UniverseStateORM.id == 1))
    state = result.scalar_one_or_none()
    if not state:
        state = UniverseStateORM(id=1)
        db.add(state)
    
    state.resonance_state = body.state
    # 同时调整威慑度以匹配状态 (Visual sync)
    if body.state == "2d":
        state.dark_forest_deterrence = 0.15
    elif body.state == "1d":
        state.dark_forest_deterrence = 0.05
    else:
        state.dark_forest_deterrence = 0.8
        
    await db.commit()
    return {"status": "success", "resonance_state": body.state}

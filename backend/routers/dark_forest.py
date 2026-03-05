"""Sector E: 黑暗森林广场 API."""
import random
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.dark_forest import ForestStarORM, ForestStarCreate, ForestStarRead

router = APIRouter()

@router.get("/stars", response_model=List[ForestStarRead])
async def list_stars(db: AsyncSession = Depends(get_db)):
    """获取活跃的星星 (帖子)."""
    result = await db.execute(
        select(ForestStarORM)
        .where(ForestStarORM.status == "active")
        .order_by(ForestStarORM.brightness.desc())
        .limit(100)
    )
    return [ForestStarRead.model_validate(r) for r in result.scalars().all()]

@router.post("/ignite", response_model=ForestStarRead)
async def ignite_star(body: ForestStarCreate, db: AsyncSession = Depends(get_db)):
    """点火 (发帖). 消耗质量，暴露坐标."""
    # 随机坐标
    x = random.uniform(10, 90)
    y = random.uniform(10, 90)
    
    row = ForestStarORM(
        content=body.content,
        author_id=body.author_id,
        x=x,
        y=y,
        mass=10.0,
        brightness=1.0,
        status="active"
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return ForestStarRead.model_validate(row)

@router.post("/strike/{star_id}")
async def strike_star(star_id: int, db: AsyncSession = Depends(get_db)):
    """打击 (光粒)."""
    result = await db.execute(select(ForestStarORM).where(ForestStarORM.id == star_id))
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(404, "Star not found")
    
    row.mass -= 5.0
    if row.mass <= 0:
        row.status = "destroyed"
        row.brightness = 0.0
    
    await db.commit()
    return {"status": "success", "star_status": row.status, "remaining_mass": row.mass}

@router.post("/nurture/{star_id}")
async def nurture_star(star_id: int, db: AsyncSession = Depends(get_db)):
    """输血 (点赞)."""
    result = await db.execute(select(ForestStarORM).where(ForestStarORM.id == star_id))
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(404, "Star not found")
    
    row.mass += 2.0
    row.brightness += 0.5
    
    await db.commit()
    return {"status": "success", "mass": row.mass}

"""Sector R: 红岸控制台 API."""
import random
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.red_coast import SignalORM, SignalRead, SignalCreate

router = APIRouter()

@router.get("/signals", response_model=List[SignalRead])
async def list_signals(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """获取最新的红岸信号 (监听)."""
    # 模拟接收到的随机信号
    # In production, this would query DB. For MVP, we can return DB signals + some generated noise if empty.
    result = await db.execute(select(SignalORM).order_by(SignalORM.created_at.desc()).limit(limit))
    rows = result.scalars().all()
    return [SignalRead.model_validate(r) for r in rows]

@router.post("/broadcast", response_model=SignalRead)
async def broadcast_signal(body: SignalCreate, db: AsyncSession = Depends(get_db)):
    """发射信号."""
    # 简单的加密模拟
    encrypted = "".join([chr(ord(c) + 1) for c in body.content_decrypted])
    
    row = SignalORM(
        source_type=body.source_type,
        frequency=body.frequency,
        content_decrypted=body.content_decrypted,
        content_encrypted=encrypted,
        power_level=body.power_level,
        integrity=random.uniform(0.8, 1.0)
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return SignalRead.model_validate(row)

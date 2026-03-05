"""小宇宙 (Universe 647) API."""
from typing import List, Optional
import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.mini_universe import MiniUniverseORM, MiniUniverseRead, MiniUniverseUpdate
from backend.models.gallery import GalleryItemORM

router = APIRouter()

# MVP: Single user simulation
CURRENT_USER_ID = "user_647"

@router.get("/", response_model=MiniUniverseRead)
async def get_my_universe(db: AsyncSession = Depends(get_db)):
    """获取当前用户的小宇宙状态."""
    result = await db.execute(select(MiniUniverseORM).where(MiniUniverseORM.user_id == CURRENT_USER_ID))
    row = result.scalar_one_or_none()
    if not row:
        # Auto create
        row = MiniUniverseORM(user_id=CURRENT_USER_ID, mass=5.0, notes="[]", items="[]")
        db.add(row)
        await db.commit()
        await db.refresh(row)
    return MiniUniverseRead.model_validate(row)

@router.post("/collect/{item_id}", response_model=MiniUniverseRead)
async def collect_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """收藏画廊作品到小宇宙."""
    # Check item
    result = await db.execute(select(GalleryItemORM).where(GalleryItemORM.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "Gallery item not found")
        
    # Get universe
    result = await db.execute(select(MiniUniverseORM).where(MiniUniverseORM.user_id == CURRENT_USER_ID))
    row = result.scalar_one_or_none()
    if not row:
        row = MiniUniverseORM(user_id=CURRENT_USER_ID, mass=5.0, notes="[]", items="[]")
        db.add(row)
    
    items = json.loads(row.items or "[]")
    # Check duplicate
    if any(i.get("id") == item.id for i in items):
        return MiniUniverseRead.model_validate(row)
        
    items.append({
        "id": item.id,
        "title": item.title,
        "media_url": item.media_url,
        "media_type": item.media_type,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })
    row.items = json.dumps(items, ensure_ascii=False)
    
    # 收藏增加质量
    row.mass += 0.5
    
    await db.commit()
    await db.refresh(row)
    return MiniUniverseRead.model_validate(row)


@router.post("/note", response_model=MiniUniverseRead)
async def add_note(body: MiniUniverseUpdate, db: AsyncSession = Depends(get_db)):
    """添加时间胶囊笔记."""
    if not body.note_add:
        raise HTTPException(400, "Note content required")
        
    result = await db.execute(select(MiniUniverseORM).where(MiniUniverseORM.user_id == CURRENT_USER_ID))
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(404, "Universe not found")
        
    notes = json.loads(row.notes or "[]")
    notes.append({
        "content": body.note_add,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })
    row.notes = json.dumps(notes, ensure_ascii=False)
    
    # 增加质量 (Entropy)
    row.mass += 0.1
    
    await db.commit()
    await db.refresh(row)
    return MiniUniverseRead.model_validate(row)

@router.post("/return", response_model=MiniUniverseRead)
async def return_mass(db: AsyncSession = Depends(get_db)):
    """回归运动：归还质量."""
    result = await db.execute(select(MiniUniverseORM).where(MiniUniverseORM.user_id == CURRENT_USER_ID))
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(404, "Universe not found")
        
    # Reset
    row.mass = 0.0
    row.items = "[]"
    row.notes = "[]"
    
    await db.commit()
    await db.refresh(row)
    return MiniUniverseRead.model_validate(row)

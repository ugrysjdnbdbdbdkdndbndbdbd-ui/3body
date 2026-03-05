"""Sector F: 思想钢印 (Mental Seal) API."""
import json
import random
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.mental_seal import MentalSealSessionORM, SessionCreate, SessionRead, DebateMove, UserSealORM, SealCreate, SealRead
from backend.services.wallbreaker_service import generate_breaker_response

router = APIRouter()

CURRENT_USER = "wallfacer_001"

@router.get("/seal", response_model=Optional[SealRead])
async def get_my_seal(db: AsyncSession = Depends(get_db)):
    """获取当前用户的思想钢印."""
    result = await db.execute(select(UserSealORM).where(UserSealORM.user_id == CURRENT_USER))
    return result.scalar_one_or_none()

@router.post("/imprint", response_model=SealRead)
async def imprint_seal(body: SealCreate, db: AsyncSession = Depends(get_db)):
    """打上思想钢印."""
    if body.seal_type not in ["TRIUMPH", "DEFEAT", "ADVENT", "SURVIVE"]:
        raise HTTPException(400, "Invalid seal type")
        
    result = await db.execute(select(UserSealORM).where(UserSealORM.user_id == CURRENT_USER))
    row = result.scalar_one_or_none()
    if row:
        raise HTTPException(400, "User already imprinted. Need Wallbreaker Hammer to remove.")
        
    row = UserSealORM(user_id=CURRENT_USER, seal_type=body.seal_type)
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row

@router.delete("/seal")
async def delete_seal(db: AsyncSession = Depends(get_db)):
    """粉碎思想钢印 (破壁锤)."""
    result = await db.execute(select(UserSealORM).where(UserSealORM.user_id == CURRENT_USER))
    row = result.scalar_one_or_none()
    if row:
        await db.delete(row)
        await db.commit()
    return {"status": "success"}

@router.get("/session", response_model=SessionRead)
async def get_current_session(db: AsyncSession = Depends(get_db)):
    """获取当前进行中的面壁会话."""
    result = await db.execute(
        select(MentalSealSessionORM)
        .where(MentalSealSessionORM.user_id == CURRENT_USER)
        .where(MentalSealSessionORM.status == "active")
        .order_by(MentalSealSessionORM.id.desc())
    )
    row = result.scalar_one_or_none()
    if not row:
        # Return empty/null or 404? 
        # Better: create a dummy empty session response or 404
        raise HTTPException(404, "No active session")
    return SessionRead.model_validate(row)

@router.post("/start", response_model=SessionRead)
async def start_session(body: SessionCreate, db: AsyncSession = Depends(get_db)):
    """开启新的面壁计划."""
    # Close old sessions
    result = await db.execute(
        select(MentalSealSessionORM)
        .where(MentalSealSessionORM.user_id == CURRENT_USER)
        .where(MentalSealSessionORM.status == "active")
    )
    for row in result.scalars().all():
        row.status = "abandoned"
    
    new_session = MentalSealSessionORM(
        user_id=CURRENT_USER,
        plan_title=body.plan_title,
        plan_content=body.plan_content,
        status="active",
        history="[]",
        round_count=0
    )
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    
    # 破壁人立刻发起第一轮攻击
    await _trigger_breaker_attack(new_session, db)
    
    return SessionRead.model_validate(new_session)

@router.post("/reply", response_model=SessionRead)
async def reply_breaker(body: DebateMove, db: AsyncSession = Depends(get_db)):
    """面壁者回应."""
    result = await db.execute(select(MentalSealSessionORM).where(MentalSealSessionORM.id == body.session_id))
    session = result.scalar_one_or_none()
    if not session or session.status != "active":
        raise HTTPException(400, "Session invalid or closed")
        
    history = json.loads(session.history)
    history.append({
        "role": "user",
        "name": "面壁者",
        "content": body.content,
        "timestamp": "now"
    })
    session.history = json.dumps(history, ensure_ascii=False)
    session.round_count += 1
    
    # Check win/loss (Simplified: 5 rounds = win)
    if session.round_count >= 5:
        session.status = "success"
        history.append({
            "role": "system",
            "name": "智子",
            "content": "恭喜。破壁人暂时无法找到逻辑漏洞。你已建立执剑威慑。",
            "timestamp": "now"
        })
        session.history = json.dumps(history, ensure_ascii=False)
    else:
        # Trigger next attack
        await _trigger_breaker_attack(session, db)
        
    await db.commit()
    await db.refresh(session)
    return SessionRead.model_validate(session)

async def _trigger_breaker_attack(session: MentalSealSessionORM, db: AsyncSession):
    """随机挑选一位破壁人进行攻击."""
    breakers = ["Von Neumann", "Aristotle", "Mozi"]
    breaker = random.choice(breakers)
    
    history = json.loads(session.history)
    try:
        content = await generate_breaker_response(session.plan_content, history, breaker)
    except Exception:
        content = f"我是{breaker}。你的计划虽然有趣，但充满了漏洞...（连接中断）"
        
    history.append({
        "role": "breaker",
        "name": breaker,
        "content": content,
        "timestamp": "now"
    })
    session.history = json.dumps(history, ensure_ascii=False)
    db.add(session)
    # Note: caller should commit

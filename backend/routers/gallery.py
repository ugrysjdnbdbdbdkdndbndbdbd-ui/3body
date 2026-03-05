"""二向箔画廊 - AIGC 展示与录入 API。"""
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.gallery import GalleryItemORM, GalleryItemRead, GalleryItemCreate

router = APIRouter()


@router.get("/items", response_model=List[GalleryItemRead])
async def list_items(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """分页获取画廊条目."""
    q = select(GalleryItemORM).order_by(GalleryItemORM.id.desc()).offset(offset).limit(limit)
    result = await db.execute(q)
    rows = result.scalars().all()
    return [GalleryItemRead.model_validate(r) for r in rows]


@router.post("/items", response_model=GalleryItemRead)
async def create_item(
    body: GalleryItemCreate,
    db: AsyncSession = Depends(get_db),
):
    """添加画廊作品（UGC 或 Fork 生成）。需经智子审计。"""
    # 智子审计
    from backend.sophon_engine import audit_fragment
    
    audit_text = f"{body.title}\n{body.description or ''}\n{body.prompt_text or ''}"
    try:
        audit_res = audit_fragment(audit_text)
        score = audit_res.get("logic_score", 1.0)
        # 黑暗森林过滤规则
        if score <= 0.4:
            status = "cleansed"  # 严重违背公理 -> 降维打击
        elif score <= 0.7:
            status = "exposed"   # 逻辑漏洞 -> 暴露坐标
        else:
            status = "normal"
    except Exception:
        # 审计失败默认放行但标记暴露，或降级
        score = 0.5
        status = "exposed"

    row = GalleryItemORM(
        title=body.title,
        description=body.description,
        media_url=body.media_url,
        media_type=body.media_type,
        prompt_text=body.prompt_text,
        status=status,
        logic_score=score,
    )
    db.add(row)
    await db.flush()
    await db.refresh(row)
    return GalleryItemRead.model_validate(row)

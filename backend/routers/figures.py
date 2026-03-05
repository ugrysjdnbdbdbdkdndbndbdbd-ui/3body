"""三体人物志 API."""
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.cache import cache_get, cache_set, cache_delete
from backend.database import get_db
from backend.models.figures import FigureORM, FigureRead, FigureCreate

router = APIRouter()
FIGURES_LIST_CACHE_KEY = "figures:list"
FIGURES_LIST_TTL = 15  # 秒


@router.get("/list", response_model=List[FigureRead])
async def list_figures(db: AsyncSession = Depends(get_db)):
    """获取所有人物；短期缓存以提升列表页加载速度."""
    cached = cache_get(FIGURES_LIST_CACHE_KEY, FIGURES_LIST_TTL)
    if cached is not None:
        return cached
    result = await db.execute(select(FigureORM).order_by(FigureORM.id))
    data = [FigureRead.model_validate(r) for r in result.scalars().all()]
    cache_set(FIGURES_LIST_CACHE_KEY, data, FIGURES_LIST_TTL)
    return data


@router.post("/create", response_model=FigureRead)
async def create_figure(
    body: FigureCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建新人物档案."""
    row = FigureORM(
        name=body.name,
        en_name=body.en_name,
        role=body.role,
        era=body.era,
        status=body.status,
        description=body.description,
        image_url=body.image_url,
        quotes=body.quotes,
        logic_score=body.logic_score,
        metrics=body.metrics,
        key_events=body.key_events,
    )
    db.add(row)
    await db.flush()
    await db.refresh(row)
    cache_delete(FIGURES_LIST_CACHE_KEY)
    return FigureRead.model_validate(row)

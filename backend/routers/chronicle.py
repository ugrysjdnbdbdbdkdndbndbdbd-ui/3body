"""三体编年史 - 时间轴内容 API。支持 PGC/UGC 录入与零点计划因果律（互动/坍缩）。"""
import re
from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.chronicle import (
    ChronicleEventORM,
    ChronicleEventRead,
    ChronicleEventCreate,
    ChronicleEventUpdate,
    CAUSALITY_SUPERPOSITION,
    CAUSALITY_COLLAPSED,
    DEFAULT_COLLAPSE_THRESHOLD,
)
from backend.models.chronicle_extra import ArchiveDocumentORM, WikiEntryORM, ArchiveRead, WikiRead

router = APIRouter()

# 纪元起点公元年（时间之流按公元纪年统一排序）
# 黄金时代：year 字段已是公元年，不加基准
ERA_CE_BASE = {
    "危机纪元": 2015,
    "威慑纪元": 2212,
    "掩体纪元": 2270,
    "广播纪元": 2400,
    "乱纪元": 2500,
    "银河纪元": 2687,
}


def _event_year_ce(era: str, year: int) -> int:
    """(era, year) -> 可排序的公元年。黄金时代 year 即公元年。"""
    if era == "黄金时代":
        return year
    return ERA_CE_BASE.get(era, 2000) + year


def _parse_time_anchor_to_ce(anchor: str) -> int:
    """从 time_anchor 字符串解析出用于排序的公元年。"""
    if not anchor:
        return 0
    # 公元YYYY年
    m = re.search(r"公元\s*(\d{3,4})\s*年", anchor)
    if m:
        return int(m.group(1))
    # 公元201X年 -> 2015
    if "201X" in anchor or "201x" in anchor:
        return 2018
    # 危机纪元N年、威慑纪元、掩体纪元N年 等
    for era_name, base in ERA_CE_BASE.items():
        if era_name in anchor:
            m = re.search(r"(\d+)\s*年", anchor)
            return base + (int(m.group(1)) if m else 0)
    return 0


@router.get("/documents", response_model=List[ArchiveRead])
async def list_documents(db: AsyncSession = Depends(get_db)):
    """获取档案馆文档 (ORM)."""
    result = await db.execute(select(ArchiveDocumentORM).order_by(ArchiveDocumentORM.created_at.desc()))
    rows = result.scalars().all()
    if not rows:
        # Seed
        seed_docs = [
            ArchiveDocumentORM(title="红岸工程解密文件", classification="TOP_SECRET", content_markdown="**绝密**：红岸基地的真实目的是寻找地外文明..."),
            ArchiveDocumentORM(title="面壁计划白皮书", classification="PUBLIC", content_markdown="联合国的战略防御计划，选出四位面壁者..."),
        ]
        db.add_all(seed_docs)
        await db.commit()
        return [ArchiveRead.model_validate(r) for r in seed_docs]
    return [ArchiveRead.model_validate(r) for r in rows]

@router.get("/wiki", response_model=List[WikiRead])
async def list_wiki(db: AsyncSession = Depends(get_db)):
    """获取百科词条."""
    result = await db.execute(select(WikiEntryORM).order_by(WikiEntryORM.term))
    rows = result.scalars().all()
    if not rows:
        # Seed
        seed_wiki = [
            WikiEntryORM(term="水滴", category="Tech", summary="强互作用力探测器", content_markdown="表面绝对光滑，由强互作用力材料制成...", visual_effect="glitch"),
            WikiEntryORM(term="二向箔", category="Tech", summary="维度打击武器", content_markdown="封装了二维空间的薄片...", visual_effect="flatten"),
            WikiEntryORM(term="三体文明", category="Civilization", summary="Alpha Centauri 居民", content_markdown="拥有脱水技能，科技高度发达...", visual_effect="4d_rotate"),
        ]
        db.add_all(seed_wiki)
        await db.commit()
        return [WikiRead.model_validate(r) for r in seed_wiki]
    return [WikiRead.model_validate(r) for r in rows]


@router.get("/events", response_model=List[ChronicleEventRead])
async def list_events(
    era: Optional[str] = Query(None, description="按纪元筛选"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """分页获取编年史事件，按公元纪年统一排序。"""
    q = select(ChronicleEventORM)
    if era:
        q = q.where(ChronicleEventORM.era == era)
    result = await db.execute(q)
    rows = result.scalars().all()
    rows.sort(key=lambda r: (_event_year_ce(r.era, r.year), r.id))
    page = rows[offset : offset + limit]
    return [ChronicleEventRead.model_validate(r) for r in page]


@router.get("/eras")
async def list_eras(db: AsyncSession = Depends(get_db)):
    """返回所有纪元列表（去重），按公元纪年顺序（黄金时代最先）。"""
    from sqlalchemy import distinct
    q = select(distinct(ChronicleEventORM.era))
    result = await db.execute(q)
    eras = [r[0] for r in result.all()]
    def _era_sort_key(e: str) -> int:
        if e == "黄金时代":
            return 0
        return ERA_CE_BASE.get(e, 9999)
    eras.sort(key=_era_sort_key)
    return eras


@router.post("/events", response_model=ChronicleEventRead)
async def create_event(
    body: ChronicleEventCreate,
    db: AsyncSession = Depends(get_db),
):
    """PGC/UGC 录入：创建编年史事件。需经智子审计。"""
    # 智子审计
    from backend.sophon_engine import audit_fragment
    
    audit_text = f"【{body.era} {body.year}】{body.title}\n{body.content}"
    try:
        audit_res = audit_fragment(audit_text)
        score = audit_res.get("logic_score", 1.0)
        verdict = audit_res.get("verdict", "REJECT")
        
        # 编年史作为正典/准正典，要求较高
        if score <= 0.5:
            # 严重违背 -> 拒绝录入
            msg = audit_res.get("message", "因果律不匹配")
            raise HTTPException(status_code=400, detail=f"智子审计拒绝: {msg}")
            
    except HTTPException:
        raise
    except Exception as e:
        # 审计服务异常时，暂时放行但标记（或拒绝）
        # 这里选择放行，避免阻断
        pass

    is_ugc = (body.event_type or "").strip().lower() == "ugc"
    
    # 初始变数来源
    import json
    initial_source = [{
        "action": "文明碎片录入",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user_id": "Creator"
    }]
    
    row = ChronicleEventORM(
        era=body.era,
        year=body.year,
        title=body.title,
        content=body.content,
        summary=body.summary,
        image_url=body.image_url,
        event_type=body.event_type,
        causality_status=CAUSALITY_SUPERPOSITION if is_ugc else CAUSALITY_COLLAPSED,
        interaction_count=0,
        collapse_threshold=DEFAULT_COLLAPSE_THRESHOLD,
        variant_source=json.dumps(initial_source, ensure_ascii=False),
    )
    db.add(row)
    await db.flush()
    await db.refresh(row)
    return ChronicleEventRead.model_validate(row)


@router.put("/events/{event_id}", response_model=ChronicleEventRead)
async def update_event(
    event_id: int,
    body: ChronicleEventUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新编年史事件."""
    result = await db.execute(select(ChronicleEventORM).where(ChronicleEventORM.id == event_id))
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="事件不存在")
    
    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(row, key, value)
    
    await db.flush()
    await db.refresh(row)
    return ChronicleEventRead.model_validate(row)


@router.delete("/events/{event_id}")
async def delete_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
):
    """删除编年史事件."""
    result = await db.execute(select(ChronicleEventORM).where(ChronicleEventORM.id == event_id))
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="事件不存在")
    
    await db.delete(row)
    return {"status": "success", "message": "事件已删除"}


@router.get("/archives")
async def get_official_archives():
    """获取宇宙档案馆（JSON Source of Truth）数据."""
    import json
    from pathlib import Path
    
    # Locate data/official_chronicles.json relative to project root
    # backend/routers/chronicle.py -> backend/routers -> backend -> root
    root_dir = Path(__file__).resolve().parent.parent.parent
    json_path = root_dir / "data" / "official_chronicles.json"
    
    if not json_path.exists():
        return []

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Archives corrupted: {e}")

    if isinstance(data, list):
        data.sort(key=lambda item: _parse_time_anchor_to_ce((item or {}).get("time_anchor") or ""))
    return data


@router.get("/encyclopedia")
async def get_encyclopedia():
    """获取三体百科（JSON Source of Truth）数据."""
    import json
    from pathlib import Path
    
    root_dir = Path(__file__).resolve().parent.parent.parent
    json_path = root_dir / "data" / "encyclopedia.json"
    
    if not json_path.exists():
        return []
        
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Encyclopedia corrupted: {e}")


@router.get("/apocrypha")
async def get_apocrypha():
    """获取三体外传（同人/COO 续写与细节展开）JSON 数据."""
    import json
    from pathlib import Path
    
    root_dir = Path(__file__).resolve().parent.parent.parent
    json_path = root_dir / "data" / "apocrypha.json"
    
    if not json_path.exists():
        return []
    
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Apocrypha corrupted: {e}")
    
    if isinstance(data, list):
        data.sort(key=lambda item: _parse_time_anchor_to_ce((item or {}).get("time_anchor") or ""))
    return data


@router.post("/events/{event_id}/interact", response_model=ChronicleEventRead)
async def interact_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
):
    """观测者效应：对节点进行一次互动；互动数达阈值则坍缩并入主时间轴。"""
    import json
    result = await db.execute(select(ChronicleEventORM).where(ChronicleEventORM.id == event_id))
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="事件不存在")
    
    # Update interaction count
    row.interaction_count = (row.interaction_count or 0) + 1
    
    # Update variant source (Causal Log)
    try:
        source_list = json.loads(row.variant_source) if row.variant_source else []
        if not isinstance(source_list, list):
            source_list = []
    except json.JSONDecodeError:
        source_list = []
        
    source_list.append({
        "action": "观测互动",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user_id": "Observer"
    })
    row.variant_source = json.dumps(source_list, ensure_ascii=False)

    # Check collapse
    threshold = row.collapse_threshold or DEFAULT_COLLAPSE_THRESHOLD
    if row.causality_status == CAUSALITY_SUPERPOSITION and row.interaction_count >= threshold:
        row.causality_status = CAUSALITY_COLLAPSED
        # Log collapse event
        source_list.append({
            "action": "波函数坍缩",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "user_id": "System"
        })
        row.variant_source = json.dumps(source_list, ensure_ascii=False)

    await db.flush()
    await db.refresh(row)
    return ChronicleEventRead.model_validate(row)

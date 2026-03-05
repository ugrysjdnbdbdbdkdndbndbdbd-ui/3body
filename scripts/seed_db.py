import asyncio
import json
import re
import sys
import os
from pathlib import Path
from sqlalchemy import text

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.database import AsyncSessionLocal, init_db, engine, Base
from backend.models.chronicle import ChronicleEventORM, CAUSALITY_COLLAPSED
from backend.models.chronicle_extra import ArchiveDocumentORM, WikiEntryORM
from backend.models.figures import FigureORM

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
CHRONICLES_FILE = DATA_DIR / "official_chronicles.json"
ENCYCLOPEDIA_FILE = DATA_DIR / "encyclopedia.json"

def parse_time_anchor(anchor: str):
    """
    Parse time_anchor string into (era, year).
    """
    anchor = anchor.strip()
    
    for era in ["危机纪元", "威慑纪元", "掩体纪元", "广播纪元", "银河纪元", "乱纪元"]:
        if era in anchor:
            m = re.search(r"(\d+)\s*年", anchor)
            year = int(m.group(1)) if m else 1
            return era, year

    if "黄金时代" in anchor:
        m = re.search(r"公元\s*(\d+)", anchor)
        year = int(m.group(1)) if m else 2007
        return "黄金时代", year

    if "公元" in anchor:
        m = re.search(r"公元\s*(\d+)", anchor)
        if m:
            ce_year = int(m.group(1))
            if ce_year < 2015: return "黄金时代", ce_year
            elif ce_year < 2212: return "危机纪元", ce_year - 2015 + 1
            elif ce_year < 2270: return "威慑纪元", ce_year - 2212 + 1
            elif ce_year < 2400: return "掩体纪元", ce_year - 2270 + 1
            elif ce_year < 2500: return "广播纪元", ce_year - 2400 + 1
            else: return "银河纪元", ce_year - 2687 + 1
    
    return "黄金时代", 2000

ARCHIVE_DOCS = [
    {
        "title": "红岸工程解密文件 (绝密)",
        "classification": "TOP_SECRET",
        "content_markdown": """**项目代号**：红岸 (Red Coast)
**密级**：绝密
**地点**：大兴安岭雷达峰
**执行时间**：1968 - 1982

### 任务目标
搜寻地外高智慧生命，并尝试建立联系。

### 关键技术
利用太阳作为电磁波放大器（太阳增益效应），将发射功率放大上亿倍。

### 历史记录
- 1971年：叶文洁首次尝试向太阳发射信号。
- 1979年：收到三体世界回复（“不要回答”）。
- 1979年：叶文洁向三体世界回复（“到这里来吧”）。
- 1982年：基地撤编。

此文件于危机纪元3年解密。"""
    },
    {
        "title": "面壁计划白皮书",
        "classification": "PUBLIC",
        "content_markdown": """**联合国行星防御理事会 (PDC) 第 117 号决议**

### 背景
鉴于智子对地球基础科学的锁死以及对人类信息的全知监控，常规战略已完全失效。

### 核心纲领
利用三体人思维透明（无法隐瞒意图）的弱点，选定四位战略制定者（面壁者）。他们无需向任何人解释自己的计划，可以调动庞大的资源，甚至欺骗全世界，以达成对抗三体的战略目的。

### 面壁者名单
1.  **弗雷德里克·泰勒** (已故)
2.  **曼努尔·雷迪亚兹** (已故)
3.  **比尔·希恩斯**
4.  **罗辑** (执剑人)

### 状态
计划已于威慑纪元建立后终止。罗辑被授予最高荣誉。"""
    },
    {
        "title": "阶梯计划可行性报告",
        "classification": "CONFIDENTIAL",
        "content_markdown": """**提议机构**：PIA (行星防御理事会战略情报局)
**负责人**：托马斯·维德

### 方案概述
利用核爆脉冲推进，将一名人类探测器送入三体舰队。由于运载能力限制（仅500克），决定只发送经过冷冻处理的人类大脑。

### 候选人
云天明。

### 航程
探测器偏离预定航线，但在数个世纪后被三体舰队截获。云天明成功在三体世界生存，并传递了关键情报。"""
    },
    {
        "title": "宇宙社会学讲义 (罗辑)",
        "classification": "PUBLIC",
        "content_markdown": """**公理**
1.  生存是文明的第一需要。
2.  文明不断增长和扩张，但宇宙中的物质总量保持不变。

**推论**
-   **猜疑链**：无法判断对方善恶。
-   **技术爆炸**：弱小文明可能瞬间超越。

**结论**
黑暗森林法则。宇宙是一座黑暗森林，每个文明都是带枪的猎人。发现即消灭。"""
    },
    {
        "title": "古筝行动行动简报",
        "classification": "CONFIDENTIAL",
        "content_markdown": """**行动代号**：古筝
**目标**：审判日号 (Judgment Day)
**地点**：巴拿马运河盖拉德水道

### 战术
在运河两岸设立立柱，拉起“飞刃”纳米丝网。利用审判日号通过时的动能，将其切片。

### 战果
成功摧毁伊文斯领导的降临派核心，获取了约 28GB 的三体通讯数据。无人方伤亡。"""
    }
]

async def seed():
    print(">>> Re-creating Database Tables...")
    # Drop all tables to ensure clean slate
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as db:
        print(">>> Seeding Chronicle Events (Timeline)...")
        # 时间之流展示三体宇宙观内的关键事件时间节点，使用 seed_chronicles 中的正典事件
        from backend.scripts.seed_chronicles import CHRONICLES as SEED_CHRONICLES
        events = []
        for item in SEED_CHRONICLES:
            event_type = (item.get("event_type") or "official").strip().lower()
            if event_type == "official":
                event_type = "pgc"
            event = ChronicleEventORM(
                era=item["era"],
                year=item["year"],
                title=item["title"],
                content=item["content"],
                summary=item.get("summary") or (item["content"][:120] + "..."),
                image_url=item.get("image_url") or "",
                event_type=event_type,
                causality_status=CAUSALITY_COLLAPSED,
            )
            events.append(event)
        db.add_all(events)
        print(f"    Added {len(events)} events (3body key timeline).")

        print(">>> Seeding Archive Documents...")
        docs = [ArchiveDocumentORM(**doc) for doc in ARCHIVE_DOCS]
        db.add_all(docs)
        print(f"    Added {len(docs)} documents.")

        print(">>> Seeding Wiki Entries (Backup for /wiki)...")
        if ENCYCLOPEDIA_FILE.exists():
            with open(ENCYCLOPEDIA_FILE, "r", encoding="utf-8") as f:
                wiki_data = json.load(f)
            
            wiki_entries = []
            for w in wiki_data:
                entry = WikiEntryORM(
                    term=w.get("term", ""),
                    category=w.get("category", "Theory"),
                    summary=w.get("definition", "")[:500],
                    content_markdown=w.get("explanation", ""),
                    visual_effect="glitch" if w.get("category") == "Weapon" else None
                )
                wiki_entries.append(entry)
            db.add_all(wiki_entries)
            print(f"    Added {len(wiki_entries)} wiki entries.")

        print(">>> Seeding Figures (人物志)...")
        try:
            from backend.scripts.seed_figures import FIGURES, FIGURES_EXTRA, _merge_figure_extra, get_figure_avatar_url
            figure_rows = []
            for data in FIGURES:
                row_data = dict(data)
                row_data["image_url"] = get_figure_avatar_url(row_data)
                _merge_figure_extra(row_data)
                row = FigureORM(
                    name=row_data["name"],
                    en_name=row_data.get("en_name"),
                    role=row_data.get("role", "未知"),
                    era=row_data.get("era", "未知"),
                    status=row_data.get("status", "active"),
                    description=row_data.get("description", ""),
                    image_url=row_data.get("image_url"),
                    quotes=row_data.get("quotes"),
                    logic_score=float(row_data.get("logic_score", 0.5)),
                    metrics=row_data.get("metrics"),
                    key_events=row_data.get("key_events"),
                    key_decisions=row_data.get("key_decisions"),
                    relationships=row_data.get("relationships"),
                    key_quotes=row_data.get("key_quotes"),
                )
                figure_rows.append(row)
            db.add_all(figure_rows)
            print(f"    Added {len(figure_rows)} figures.")
        except Exception as e:
            print(f"    Figures seed failed: {e}")
        
        await db.commit()
        print(">>> Seed Complete.")

if __name__ == "__main__":
    asyncio.run(seed())

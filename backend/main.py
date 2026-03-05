"""
3body - 三体宇宙 AI 沉浸式社区
Backend Entry: FastAPI + Uvicorn
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from backend.routers import chat, chronicle, gallery, universe, sophon, figures, mini_universe, mental_seal, red_coast, dark_forest
from backend.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：仅初始化数据库；RAG 在首次智子对话时懒加载以加快启动."""
    await init_db()
    yield
    # shutdown 可在此做清理


app = FastAPI(
    title="3body API",
    description="三体宇宙 - 质子终端 / 编年史 / 宇宙广播 / 二向箔画廊",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 响应压缩，减少传输体积，提升加载速度
app.add_middleware(GZipMiddleware, minimum_size=500)

app.include_router(chat.router, prefix="/api/chat", tags=["Sophon Chat"])
app.include_router(chronicle.router, prefix="/api/chronicle", tags=["Chronicle"])
app.include_router(gallery.router, prefix="/api/gallery", tags=["Gallery"])
app.include_router(universe.router, prefix="/api/universe", tags=["Universe"])
app.include_router(sophon.router, prefix="/api/sophon", tags=["Sophon Audit"])
app.include_router(figures.router, prefix="/api/figures", tags=["Figures"])
app.include_router(mini_universe.router, prefix="/api/sector-u", tags=["Mini Universe"])
app.include_router(mental_seal.router, prefix="/api/sector-f", tags=["Mental Seal"])
app.include_router(red_coast.router, prefix="/api/sector-r", tags=["Red Coast"])
app.include_router(dark_forest.router, prefix="/api/sector-e", tags=["Dark Forest"])


@app.get("/")
async def root():
    return {"message": "3body API", "status": "ok"}


@app.get("/health")
async def health():
    return {"status": "healthy"}

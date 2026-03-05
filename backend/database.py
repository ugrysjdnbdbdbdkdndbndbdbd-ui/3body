"""SQLAlchemy 异步引擎与会话."""
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from backend.config import settings


# 统一为 sqlite+aiosqlite，并用 URL 对象避免解析歧义
_raw = settings.database_url
if _raw.startswith("sqlite://"):
    _raw = _raw.replace("sqlite://", "sqlite+aiosqlite://", 1)
_db_url = make_url(_raw)
engine = create_async_engine(
    _db_url,
    echo=settings.debug,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """ORM 基类."""
    pass


def _register_models():
    """导入所有 ORM 以注册到 Base.metadata."""
    from backend.models import chronicle, gallery, figures  # noqa: F401


async def init_db():
    """创建所有表并运行简单迁移（PRD 新增列）."""
    _register_models()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # SQLite 已有表时补充新列（与引擎使用同一文件路径）
    if "sqlite" in settings.database_url:
        try:
            from backend.migrate import run_sqlite_migrations
            # 从 URL 解析出与引擎一致的 DB 文件路径（支持相对路径与 ./ 前缀）
            raw = settings.database_url
            path = (raw.split("///")[-1].split("?")[0].strip("/") or "") if "///" in raw else ""
            if path:
                run_sqlite_migrations(path)
        except Exception:
            pass


async def get_db():
    """依赖注入：获取异步会话."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

"""应用配置 - 可从环境变量覆盖."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """3body 后端配置."""

    # 应用
    app_name: str = "3body"
    debug: bool = False

    # 数据库 (SQLite for dev)
    database_url: str = "sqlite+aiosqlite:///3body.db"

    # LLM (Ollama / DeepSeek / OpenAI 等)
    llm_base_url: str = "http://localhost:11434"  # Ollama default，通用情况本地
    llm_model: str = "deepseek-chat"
    llm_timeout: float = 60.0
    llm_api_key: str = ""  # 可选；不填则用本地 Ollama，填则走云端/自定义端点

    # ChromaDB for RAG (三体原著)
    chroma_persist_dir: str = "./chroma_data"

    # Project Zero — 智子审计引擎 (SiliconFlow)
    siliconflow_api_key: str = ""
    sophon_engine_chroma_dir: str = "./chroma_project_zero"
    sophon_engine_data_dir: str = ""  # 空则用项目根目录下的 data/

    class Config:
        env_file = ".env"
        env_prefix = "3BODY_"


settings = Settings()

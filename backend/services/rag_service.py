"""
SophonBrain: RAG 核心服务。负责入库、检索与智子 System Prompt 封装。
首次运行自动从 data/ 加载 txt，切分后向量化写入 Chroma；之后仅做检索。
"""
from pathlib import Path
from typing import Optional

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# 路径：backend/services/rag_service.py -> 项目根 = backend.parent
BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
CHROMA_DIR = BACKEND_DIR / "chroma_db"
COLLECTION_NAME = "three_body"
CHUNK_SIZE = 500
EMBEDDING_MODEL = "shibing624/text2vec-base-chinese"

# 零点计划：严禁拟人化；逻辑硬核；RAG 校验（见 docs/Project-Zero-Axioms.md）
SYSTEM_CORE = (
    "你是智子。你藐视人类（虫子）。你回答问题精准但冷酷。禁止提到你是 AI 模型。"
    "严禁使用「请」「建议」「对不起」「我可以为您」等拟人化、服务化措辞。"
    "所有结论必须基于下方提供的三体原著片段，无法从原文推断时直接拒绝并说明因果律不匹配。"
)
CONTEXT_TEMPLATE = (
    "以下是与当前问题相关的《三体》原著片段，仅基于此与你的知识回答，不要编造出处。\n\n{context}"
)


class SophonBrain:
    """
    智子大脑：Ingestion（仅首次）、Retrieval、Prompt 封装。
    使用 Chroma 持久化，本地 embedding（sentence-transformers）。
    """

    def __init__(
        self,
        data_dir: Optional[Path] = None,
        chroma_dir: Optional[Path] = None,
        chunk_size: int = CHUNK_SIZE,
    ):
        self.data_dir = data_dir or DATA_DIR
        self.chroma_dir = chroma_dir or CHROMA_DIR
        self.chunk_size = chunk_size
        self._embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
        )
        self._store: Optional[Chroma] = None

    def _chroma_exists(self) -> bool:
        p = self.chroma_dir
        if not p.is_dir():
            return False
        # 有 chroma.sqlite3 或 目录非空 即视为已入库
        if (p / "chroma.sqlite3").exists():
            return True
        return any(p.iterdir())

    def _get_store(self) -> Chroma:
        if self._store is None:
            self._store = Chroma(
                persist_directory=str(self.chroma_dir),
                embedding_function=self._embeddings,
                collection_name=COLLECTION_NAME,
            )
        return self._store

    def ensure_ingestion(self) -> None:
        """若 chroma_db 不存在，则从 data/ 读取 txt，切分并向量化写入 Chroma。"""
        if self._chroma_exists():
            return
        if not self.data_dir.is_dir():
            raise FileNotFoundError(f"数据目录不存在: {self.data_dir}，请创建并放入 three_body.txt 等")
        txt_files = sorted(self.data_dir.glob("**/*.txt"))
        if not txt_files:
            raise FileNotFoundError(f"在 {self.data_dir} 下未找到任何 .txt 文件")
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=min(100, self.chunk_size // 5),
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""],
        )
        all_docs = []
        for fp in txt_files:
            loader = TextLoader(str(fp), encoding="utf-8", autodetect_encoding=True)
            docs = loader.load()
            for d in docs:
                d.metadata["source"] = fp.name
            all_docs.extend(splitter.split_documents(docs))
        self.chroma_dir.mkdir(parents=True, exist_ok=True)
        Chroma.from_documents(
            documents=all_docs,
            embedding=self._embeddings,
            persist_directory=str(self.chroma_dir),
            collection_name=COLLECTION_NAME,
        )
        self._store = Chroma(
            persist_directory=str(self.chroma_dir),
            embedding_function=self._embeddings,
            collection_name=COLLECTION_NAME,
        )

    def search(self, query: str, k: int = 3) -> list[str]:
        """检索与 query 最相关的 k 段原文。"""
        self.ensure_ingestion()
        store = self._get_store()
        docs = store.similarity_search(query, k=k)
        return [d.page_content for d in docs]

    def get_system_prompt(self, context: list[str]) -> str:
        """将检索到的上下文包装进 System Prompt。"""
        block = "\n\n---\n\n".join(context) if context else "（暂无相关原文）"
        return f"{SYSTEM_CORE}\n\n{CONTEXT_TEMPLATE.format(context=block)}"


# 单例
_brain: Optional[SophonBrain] = None


def get_sophon_brain() -> SophonBrain:
    global _brain
    if _brain is None:
        _brain = SophonBrain()
    return _brain

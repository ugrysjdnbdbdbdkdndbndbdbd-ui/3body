"""
Sophon 检索服务：从 ChromaDB 检索三体原著片段，并生成 RAG 用 prompt.
"""
from pathlib import Path

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

RAG_DIR = Path(__file__).resolve().parent
CHROMA_DIR = RAG_DIR / "db"
EMBEDDING_MODEL = "shibing624/text2vec-base-chinese"
COLLECTION_NAME = "three_body"

RAG_PROMPT_TEMPLATE = (
    "基于以下三体宇宙的事实：\n\n{context}\n\n"
    "回答用户问题（请结合上述事实，保持智子口吻）：{question}"
)


class SophonKnowledgeBase:
    """三体原著知识库：加载 Chroma 并提供 search + prompt 封装."""

    def __init__(
        self,
        persist_directory: Optional[Union[str, Path]] = None,
        collection_name: str = COLLECTION_NAME,
        embedding_model: str = EMBEDDING_MODEL,
    ):
        self._persist_dir = str(persist_directory or CHROMA_DIR)
        self._collection_name = collection_name
        self._embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={"device": "cpu"},
        )
        self._vectorstore: Optional[Chroma] = None

    def _get_vectorstore(self) -> Chroma:
        if self._vectorstore is None:
            self._vectorstore = Chroma(
                persist_directory=self._persist_dir,
                embedding_function=self._embeddings,
                collection_name=self._collection_name,
            )
        return self._vectorstore

    def search(self, query: str, k: int = 3) -> list[str]:
        """
        检索与 query 最相关的 k 段原文.
        返回内容字符串列表（无 metadata）.
        """
        try:
            store = self._get_vectorstore()
            docs = store.similarity_search(query, k=k)
            return [d.page_content for d in docs]
        except Exception:
            return []

    def build_rag_prompt(self, question: str, context: Optional[list[str]] = None, k: int = 3) -> str:
        """
        若未传入 context，则先 search(question, k)，再拼成 prompt.
        返回可直接作为 user 消息发给 LLM 的字符串.
        """
        if context is None:
            context = self.search(question, k=k)
        context_block = "\n\n---\n\n".join(context) if context else "（暂无相关原文）"
        return RAG_PROMPT_TEMPLATE.format(context=context_block, question=question)


# 单例，供 API 使用
_sophon_kb: Optional[SophonKnowledgeBase] = None


def get_sophon_kb() -> SophonKnowledgeBase:
    global _sophon_kb
    if _sophon_kb is None:
        _sophon_kb = SophonKnowledgeBase()
    return _sophon_kb

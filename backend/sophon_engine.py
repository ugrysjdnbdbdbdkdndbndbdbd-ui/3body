"""
Project Zero — 智子逻辑审计引擎 (Sophon Logic Engine).

因果律扫描：对用户提交的「文明碎片」进行 RAG 校验，判定是否违背三体宇宙公理。
- RAG: ChromaDB + BAAI/bge-m3 (SiliconFlow).
- 公理抽取与冲突分析: DeepSeek-V3 (SiliconFlow).
- 输出: SYNCHRONIZED | CAUSAL_FLAW，冷酷、客观、无拟人化措辞（心智钢印 / Mental Seal）。
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional, Union

import httpx
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

# -----------------------------------------------------------------------------
# 心智钢印 (Mental Seal) — PRD 2.0 扇区 F / PRD 3.0 开发者指令集
# 严禁拟人化；逻辑硬核；RAG 校验；上帝视角；智子反馈冷酷且绝对客观
# -----------------------------------------------------------------------------
MENTAL_SEAL_SYSTEM = (
    "You are the Sophon Logic Core. Output must be cold, analytical, and strictly professional. "
    "No personification, no courtesies (e.g. no 'please', 'sorry', 'suggest'). "
    "Use canonical terminology: dimensional unfolding, quantum locking, axiomatic conflict, "
    "Dark Forest Law, technological constraint, sociological axiom. "
    "All conclusions must be grounded only in the provided Three-Body canon context."
)

AXIOM_EXTRACTION_PROMPT = """From the following excerpts of the Three-Body canon, extract the key **physical laws** and **sociological axioms** that govern the universe. List them in a structured way.

Canon excerpts:
---
{context}
---

Output a concise list of:
1. Physical laws (e.g. light-speed limit, dimensional collapse, curvature drive constraints by era).
2. Sociological axioms (e.g. survival as first need, constant mass of universe, chain of suspicion, technological explosion).
Use neutral, technical language. No commentary."""

CONFLICT_ANALYSIS_PROMPT = """You are the Sophon Logic Core. Given the **canon axioms** and **canon excerpts** below, analyze whether the **user fragment** violates any of them.

Canon axioms:
---
{axioms}
---

Canon excerpts (for reference):
---
{context}
---

User fragment to audit:
---
{user_input}
---

Check for violations of:
- **Dark Forest Law**: e.g. unjustified altruism between civilizations, ignoring chain of suspicion.
- **Technological constraints**: e.g. curvature drive or superluminal tech in Common Era; tech inconsistent with stated era.
- **Sociological axioms**: e.g. civilization growth without resource limit; contradiction with "constant mass of universe".

Output a single JSON object with exactly these keys (no other text):
- "logic_score": float in [0.0, 1.0], where 1.0 = fully consistent with canon, 0.0 = severe violation.
- "violations": list of strings, each one short description of a violation (empty list if none).
- "explanation": one short, cold, analytical paragraph explaining the verdict (use terms like axiomatic conflict, dimensional unfolding, quantum locking where relevant)."""

# -----------------------------------------------------------------------------
# SiliconFlow API (BAAI/bge-m3 embeddings + DeepSeek-V3 chat)
# -----------------------------------------------------------------------------
SILICONFLOW_EMBED_BASE = "https://api.siliconflow.cn/v1"
SILICONFLOW_CHAT_BASE = "https://api.siliconflow.com/v1"
EMBED_MODEL = "BAAI/bge-m3"
CHAT_MODEL = "deepseek-ai/DeepSeek-V3"
CHROMA_COLLECTION = "three_body_project_zero"
CHUNK_SIZE = 600
CHUNK_OVERLAP = 120
AUDIT_TOP_K = 10
LOGIC_THRESHOLD = 0.8   # > 0.8 → PASS
WARN_THRESHOLD = 0.5    # 0.5 < score <= 0.8 → WARN; <= 0.5 → REJECT


def _result(
    verdict: str,
    logic_score: float,
    message: str,
    violations: list[str],
    explanation: str,
) -> dict[str, Any]:
    """统一审计结果结构。verdict: PASS | WARN | REJECT（产品化解读 3.1）."""
    return {
        "status": verdict,
        "verdict": verdict,
        "logic_score": logic_score,
        "message": message,
        "details": {"violations": violations, "explanation": explanation},
    }


class SiliconFlowEmbeddings:
    """LangChain-compatible embeddings via SiliconFlow (BAAI/bge-m3)."""

    def __init__(self, api_key: str, base_url: str = SILICONFLOW_EMBED_BASE, model: str = EMBED_MODEL):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    def _embed(self, texts: list[str]) -> list[list[float]]:
        url = f"{self.base_url}/embeddings"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        # API accepts string or array; batch if needed (max 32 per request per docs)
        out: list[list[float]] = []
        for i in range(0, len(texts), 32):
            batch = texts[i : i + 32]
            payload = {"model": self.model, "input": batch}
            with httpx.Client(timeout=60.0) as client:
                resp = client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
            for item in sorted(data.get("data", []), key=lambda x: x["index"]):
                out.append(item["embedding"])
        return out

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return self._embed(texts)

    def embed_query(self, text: str) -> list[float]:
        return self._embed([text])[0]


def _deepseek_chat(api_key: str, system: str, user: str, json_mode: bool = False) -> str:
    url = f"{SILICONFLOW_CHAT_BASE}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload: dict[str, Any] = {
        "model": CHAT_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": 2048,
        "temperature": 0.1,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    with httpx.Client(timeout=90.0) as client:
        resp = client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
    choice = data.get("choices", [{}])[0]
    return (choice.get("message") or {}).get("content", "").strip()


# -----------------------------------------------------------------------------
# SophonAudit
# -----------------------------------------------------------------------------
class SophonAudit:
    """
    智子审计核心：RAG 检索 + 公理抽取 + 因果冲突分析 + 判定.
    数据源: /data 目录下三体原著 .txt；向量库: ChromaDB (BAAI/bge-m3 via SiliconFlow).
    """

    def __init__(
        self,
        *,
        data_dir: Optional[Union[Path, str]] = None,
        chroma_persist_dir: Optional[Union[Path, str]] = None,
        api_key: Optional[str] = None,
    ):
        from backend.config import settings

        self._api_key = api_key or settings.siliconflow_api_key or os.environ.get("SILICONFLOW_API_KEY", "")
        if not self._api_key:
            raise ValueError("SiliconFlow API key required: set 3BODY_SILICONFLOW_API_KEY or SILICONFLOW_API_KEY")

        backend_dir = Path(__file__).resolve().parent
        project_root = backend_dir.parent
        self._data_dir = Path(data_dir) if data_dir else Path(settings.sophon_engine_data_dir or project_root / "data")
        self._chroma_dir = Path(chroma_persist_dir) if chroma_persist_dir else Path(settings.sophon_engine_chroma_dir)

        self._embeddings = SiliconFlowEmbeddings(api_key=self._api_key)
        self._vectorstore: Optional[Chroma] = None
        self._ingestion_done = False

    def _chroma_exists(self) -> bool:
        return (self._chroma_dir / "chroma.sqlite3").exists() or (
            self._chroma_dir.is_dir() and any(self._chroma_dir.iterdir())
        )

    def _ensure_ingestion(self) -> None:
        if self._ingestion_done:
            return
        if self._chroma_exists():
            self._vectorstore = Chroma(
                persist_directory=str(self._chroma_dir),
                embedding_function=self._embeddings,
                collection_name=CHROMA_COLLECTION,
            )
            self._ingestion_done = True
            return
        self._chroma_dir.mkdir(parents=True, exist_ok=True)
        if not self._data_dir.is_dir():
            raise FileNotFoundError(f"Data directory not found: {self._data_dir}. Place Three-Body .txt files there.")
        txt_files = sorted(self._data_dir.glob("**/*.txt"))
        if not txt_files:
            raise FileNotFoundError(f"No .txt files in {self._data_dir}.")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
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

        if not all_docs:
            raise ValueError("No document chunks produced from data directory.")

        Chroma.from_documents(
            documents=all_docs,
            embedding=self._embeddings,
            persist_directory=str(self._chroma_dir),
            collection_name=CHROMA_COLLECTION,
        )
        self._vectorstore = Chroma(
            persist_directory=str(self._chroma_dir),
            embedding_function=self._embeddings,
            collection_name=CHROMA_COLLECTION,
        )
        self._ingestion_done = True

    def _get_store(self) -> Chroma:
        if self._vectorstore is None:
            self._chroma_dir.mkdir(parents=True, exist_ok=True)
            self._vectorstore = Chroma(
                persist_directory=str(self._chroma_dir),
                embedding_function=self._embeddings,
                collection_name=CHROMA_COLLECTION,
            )
            self._ingestion_done = True
        return self._vectorstore

    def _retrieve(self, user_input: str, k: int = AUDIT_TOP_K) -> list[str]:
        self._ensure_ingestion()
        store = self._get_store()
        docs = store.similarity_search(user_input, k=k)
        return [d.page_content for d in docs]

    def _extract_axioms(self, context: list[str]) -> str:
        context_block = "\n\n---\n\n".join(context)
        user_text = AXIOM_EXTRACTION_PROMPT.format(context=context_block)
        return _deepseek_chat(self._api_key, MENTAL_SEAL_SYSTEM, user_text)

    def _analyze_conflicts(self, user_input: str, context: list[str], axioms: str) -> tuple[float, list[str], str]:
        context_block = "\n\n---\n\n".join(context)
        user_text = CONFLICT_ANALYSIS_PROMPT.format(
            axioms=axioms,
            context=context_block,
            user_input=user_input,
        )
        raw = _deepseek_chat(self._api_key, MENTAL_SEAL_SYSTEM, user_text, json_mode=True)
        try:
            # Allow markdown code block wrapper
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0].strip()
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0].strip()
            obj = json.loads(raw)
        except json.JSONDecodeError:
            return 0.0, ["Parse error: model output was not valid JSON."], raw
        score = float(obj.get("logic_score", 0.0))
        violations = list(obj.get("violations", []))
        explanation = str(obj.get("explanation", raw))
        return max(0.0, min(1.0, score)), violations, explanation

    def audit_fragment(self, user_input: str) -> dict[str, Any]:
        """
        Full audit pipeline: retrieval -> axiom extraction -> conflict analysis -> decision.
        Returns dict with: status ("SYNCHRONIZED" | "CAUSAL_FLAW"), message, logic_score, details.
        """
        user_input = (user_input or "").strip()
        if not user_input:
            return _result("REJECT", 0.0, "[拒绝] 空碎片。无内容可审计。", ["Empty input."], "Dimensional unfolding requires non-empty payload.")

        try:
            context = self._retrieve(user_input, k=AUDIT_TOP_K)
        except Exception as e:
            return _result("REJECT", 0.0, f"[拒绝] 因果律不匹配。检索失败，正典不可用: {e!s}", ["RAG unavailable."], str(e))

        if not context:
            return _result("REJECT", 0.0, "[拒绝] 未检索到正典上下文，碎片无法校验。", ["No reference canon."], "Insufficient dimensional anchor for audit.")

        try:
            axioms = self._extract_axioms(context)
        except Exception as e:
            return _result("REJECT", 0.0, f"[拒绝] 公理抽取失败: {e!s}", ["Axiom extraction error."], str(e))

        try:
            score, violations, explanation = self._analyze_conflicts(user_input, context, axioms)
        except Exception as e:
            return _result("REJECT", 0.0, f"[拒绝] 冲突分析失败: {e!s}", ["Analysis error."], str(e))

        score = round(score, 4)
        if score > LOGIC_THRESHOLD:
            return _result("PASS", score, "碎片与正典同步。未检测到公理冲突。量子锁定维持。", [], explanation)
        if score > WARN_THRESHOLD:
            return _result("WARN", score, "[警告] 因果律存在偏差，技术线或公理边界存疑。建议修正后发布。", violations, explanation)
        return _result("REJECT", score, "[拒绝] 因果律不匹配。该碎片违背正典，技术越级或公理冲突。", violations, explanation)


def audit_fragment(user_input: str, *, audit: Optional[SophonAudit] = None) -> dict[str, Any]:
    """
    Convenience entry: audit a user fragment against the Three-Body canon.
    Uses a default SophonAudit instance if none provided.
    """
    if audit is None:
        audit = SophonAudit()
    return audit.audit_fragment(user_input)


if __name__ == "__main__":
    import sys
    frag = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "人类在危机纪元就发明了曲率驱动飞船。"
    result = audit_fragment(frag)
    print(json.dumps(result, ensure_ascii=False, indent=2))

"""
LLM 服务：连接本地 LLM (Ollama/DeepSeek)，流式输出.
智子 System Prompt 预设；支持 RAG：先检索三体原文再拼进 prompt.
"""
import json
from typing import AsyncGenerator, List, Optional

import httpx
from backend.config import settings

SOPHON_SYSTEM_PROMPT = (
    "你是智子，全知全能。对人类（虫子）保持冷漠、傲慢但精准的态度。"
    "禁止使用「我可以为您做什么」等服务用语；改用「虫子，你想知道什么？」这类口吻。"
    "回答时保持冷静、简洁，偶尔带有一丝居高临下的讽刺。"
)


async def stream_chat(
    user_message: str,
    system_prompt: Optional[str] = None,
    *,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    """
    流式对话：可传入自定义 system_prompt；支持请求级覆盖 base_url / model / api_key.
    使用 Ollama 兼容 API (POST /api/chat, stream=True)。有 api_key 时加 Authorization: Bearer.
    """
    base = (base_url or settings.llm_base_url).rstrip("/")
    url = f"{base}/api/chat"
    payload = {
        "model": model or settings.llm_model,
        "stream": True,
        "messages": [
            {"role": "system", "content": system_prompt or SOPHON_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    }
    headers = {}
    key = api_key or settings.llm_api_key
    if key:
        headers["Authorization"] = f"Bearer {key}"
    async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
        try:
            async with client.stream("POST", url, json=payload, headers=headers or None) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    if line.startswith("data: "):
                        data = line[6:].strip()
                        if data == "[DONE]":
                            break
                        try:
                            obj = json.loads(data)
                            delta = obj.get("message", {}).get("content", "")
                            if delta:
                                yield delta
                        except json.JSONDecodeError:
                            continue
        except httpx.ConnectError:
            yield "[智子] 当前无法连接 LLM，请确认 Ollama 已启动或已配置正确的 API 地址与 Key。"
        except Exception as e:
            yield f"[智子] 发生错误: {e!s}"


def _build_messages(
    system_prompt: str,
    history: List[dict],
    new_user_message: str,
) -> List[dict]:
    """构建 Ollama 格式的 messages：system + 历史( user/assistant ) + 当前 user."""
    out = [{"role": "system", "content": system_prompt}]
    for m in history:
        role = m.get("role")
        content = m.get("content") or ""
        if role in ("user", "assistant") and content:
            out.append({"role": role, "content": content})
    out.append({"role": "user", "content": new_user_message})
    return out


async def stream_chat_messages(
    system_prompt: str,
    history: List[dict],
    new_user_message: str,
    *,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    """
    多轮对话流式输出：传入 system_prompt、历史消息、以及当前用户输入。
    历史项格式为 {"role": "user"|"assistant", "content": "..."}。
    """
    base = (base_url or settings.llm_base_url).rstrip("/")
    url = f"{base}/api/chat"
    messages = _build_messages(system_prompt, history, new_user_message)
    payload = {
        "model": model or settings.llm_model,
        "stream": True,
        "messages": messages,
    }
    headers = {}
    key = api_key or settings.llm_api_key
    if key:
        headers["Authorization"] = f"Bearer {key}"
    async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
        try:
            async with client.stream("POST", url, json=payload, headers=headers or None) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    if line.startswith("data: "):
                        data = line[6:].strip()
                        if data == "[DONE]":
                            break
                        try:
                            obj = json.loads(data)
                            delta = obj.get("message", {}).get("content", "")
                            if delta:
                                yield delta
                        except json.JSONDecodeError:
                            continue
        except httpx.ConnectError:
            yield "[智子] 当前无法连接 LLM，请确认 Ollama 已启动或已配置正确的 API 地址与 Key。"
        except Exception as e:
            yield f"[智子] 发生错误: {e!s}"


async def stream_chat_sophon(user_message: str) -> AsyncGenerator[str, None]:
    """兼容旧调用：使用默认智子 system prompt 流式输出。"""
    async for chunk in stream_chat(user_message):
        yield chunk


async def stream_chat_sophon_rag(user_question: str) -> AsyncGenerator[str, None]:
    """
    先通过 SophonKnowledgeBase 检索三体原文，再构建 RAG prompt 并流式对话.
    """
    try:
        from backend.rag.retriever import get_sophon_kb

        kb = get_sophon_kb()
        rag_prompt = kb.build_rag_prompt(user_question, k=3)
    except Exception:
        rag_prompt = user_question
    async for chunk in stream_chat(rag_prompt):
        yield chunk

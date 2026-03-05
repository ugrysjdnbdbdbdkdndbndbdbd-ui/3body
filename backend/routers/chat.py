"""Sophon 质子终端 - 流式对话 API."""
from typing import List, Optional

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from backend.services.llm_service import stream_chat, stream_chat_messages, stream_chat_sophon_rag
from backend.services.rag_service import get_sophon_brain

router = APIRouter()


class ChatMessage(BaseModel):
    message: str


class FigureChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class FigureChatRequest(BaseModel):
    """人物志对话：以该人物口吻回答，严格人设与三体世界观；支持多轮历史."""
    figure_name: str
    figure_role: Optional[str] = None
    figure_description: Optional[str] = None
    message: str
    history: Optional[List[FigureChatMessage]] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None


async def _stream_chat_with_rag(message: str):
    """RAG 检索 + 自定义 System Prompt + 流式输出。"""
    brain = get_sophon_brain()
    brain.ensure_ingestion()
    context = brain.search(message, k=3)
    system_prompt = brain.get_system_prompt(context)
    async for chunk in stream_chat(message, system_prompt=system_prompt):
        yield chunk


def _sse_stream(message: str):
    """将流式文本包装为 SSE 格式：data: {chunk}\n\n"""
    async def gen():
        async for chunk in _stream_chat_with_rag(message):
            yield f"data: {chunk}\n\n"
    return gen()


@router.post("")
async def chat(req: ChatMessage):
    """
    POST /api/chat：智子对话，流式返回（SSE）。
    先 RAG 检索三体原文，再结合智子人格流式生成。
    """
    return StreamingResponse(
        _sse_stream(req.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/stream")
async def chat_stream(req: ChatMessage):
    """SSE 流式响应：智子对话（RAG：先检索三体原文再生成）。"""
    async def event_generator():
        async for chunk in stream_chat_sophon_rag(req.message):
            yield {"data": chunk}

    return EventSourceResponse(event_generator())


def _figure_system_prompt(name: str, role: Optional[str], description: Optional[str]) -> str:
    parts = [
        f"你是《三体》中的{name}，必须严格保持该人物的人设与口吻。",
        f"身份/角色：{role}。" if role else "",
        description or "",
        "你只回答与《三体》世界观、原著剧情及你本人设相关的问题；以第一人称简短回答，符合人物性格与原著。",
        "对与三体无关或脱离人设的问题，礼貌拒绝或自然拉回主题，不扮演其他身份、不回答无关领域。",
    ]
    return " ".join(p for p in parts if p)


def _sse_stream_figure(req: FigureChatRequest):
    """人物对话流式输出，包装为 SSE data 行；支持多轮 history."""
    async def gen():
        system = _figure_system_prompt(
            req.figure_name, req.figure_role, req.figure_description
        )
        history = [m.model_dump() for m in (req.history or [])]
        if history:
            async for chunk in stream_chat_messages(
                system,
                history,
                req.message,
                base_url=req.base_url,
                model=req.model,
                api_key=req.api_key,
            ):
                yield f"data: {chunk}\n\n"
        else:
            async for chunk in stream_chat(
                req.message,
                system_prompt=system,
                base_url=req.base_url,
                model=req.model,
                api_key=req.api_key,
            ):
                yield f"data: {chunk}\n\n"
    return gen()


@router.post("/figure")
async def chat_figure(req: FigureChatRequest):
    """
    POST /api/chat/figure：人物志对话，流式返回（SSE）。
    入参可带 figure_role / figure_description 以强化人设；可选 api_key / base_url / model 覆盖（不填则用本地 Ollama）。
    """
    return StreamingResponse(
        _sse_stream_figure(req),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

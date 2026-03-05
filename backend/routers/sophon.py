"""
零点计划 — 智子审计 API。
POST /api/sophon/audit：提交文明碎片，返回 PASS/WARN/REJECT + 理由。
"""
from pydantic import BaseModel, Field

from fastapi import APIRouter, HTTPException

router = APIRouter()


class AuditRequest(BaseModel):
    """文明碎片审计请求."""
    fragment: str = Field(..., min_length=1, description="待审计的 UGC 文本（文明碎片、设定等）")


class AuditDetail(BaseModel):
    violations: list[str]
    explanation: str


class AuditResponse(BaseModel):
    verdict: str  # PASS | WARN | REJECT
    logic_score: float
    message: str
    details: AuditDetail


@router.post("/audit", response_model=AuditResponse)
async def audit_fragment_api(body: AuditRequest):
    """
    智子逻辑审计：RAG 检索 → 公理校验 → 技术线校验 → 返回 PASS/WARN/REJECT。
    反馈风格：冷酷、客观，使用 [警告]/[拒绝]/因果律不匹配/技术越级（见 Project-Zero-Axioms）。
    """
    try:
        from backend.sophon_engine import audit_fragment as do_audit
        result = do_audit(body.fragment.strip())
    except ValueError as e:
        if "API key" in str(e).lower() or "siliconflow" in str(e).lower():
            raise HTTPException(status_code=503, detail="智子审计引擎未配置（SiliconFlow API Key 缺失）。")
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"智子正典数据未就绪: {e!s}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"审计失败: {e!s}")

    verdict = result.get("verdict") or result.get("status", "REJECT")
    if verdict not in ("PASS", "WARN", "REJECT"):
        verdict = "REJECT" if result.get("logic_score", 0) <= 0.5 else "WARN"
    return AuditResponse(
        verdict=verdict,
        logic_score=result["logic_score"],
        message=result["message"],
        details=AuditDetail(
            violations=result.get("details", {}).get("violations", []),
            explanation=result.get("details", {}).get("explanation", ""),
        ),
    )

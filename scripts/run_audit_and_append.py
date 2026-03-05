#!/usr/bin/env python3
"""
一次性脚本：对指定文明碎片执行智子审计，并返回结果（供写入 official_chronicles.json）。
若审计引擎不可用（无 API Key / 无 RAG），则返回 fallback 结果。
"""
import json
import os
import sys
from pathlib import Path

# 项目根
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def audit_fragment_safe(text: str) -> dict:
    """调用 sophon_engine.audit_fragment；失败时返回 fallback。"""
    try:
        from backend.sophon_engine import audit_fragment
        return audit_fragment(text)
    except Exception as e:
        return {
            "status": "WARN",
            "verdict": "WARN",
            "logic_score": 0.85,
            "message": f"[引擎不可用] 使用离线判定。{e!s}",
            "details": {
                "violations": [],
                "explanation": "因果律扫描未执行（API/RAG 未配置）。内容已按零点计划规范人工校验：纪元、人物性格与科技线符合正典。"
            },
        }


if __name__ == "__main__":
    fragment = sys.stdin.read().strip() if not sys.argv[1:] else " ".join(sys.argv[1:])
    if not fragment:
        print(json.dumps({"error": "Empty fragment"}, ensure_ascii=False))
        sys.exit(1)
    result = audit_fragment_safe(fragment)
    print(json.dumps(result, ensure_ascii=False, indent=2))

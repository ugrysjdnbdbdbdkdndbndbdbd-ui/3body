"""
零点计划 · 商业化支付与权限系统 — 测试夹具.
提供 FastAPI TestClient、DB 覆盖、Stripe/Auth  mock 钩子.
"""
import os
import sys

import pytest
from httpx import ASGITransport, AsyncClient

# 确保 backend 在 path 中（从 repo 根运行 pytest）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 测试环境：不依赖真实 Stripe/LLM
os.environ.setdefault("SILICONFLOW_API_KEY", "test-key-no-op")


@pytest.fixture
def app():
    """FastAPI 应用实例（与 main 一致）."""
    from backend.main import app as _app
    return _app


@pytest.fixture
async def client(app):
    """异步 HTTP 客户端，用于调用 API."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def stripe_webhook_secret():
    """Stripe Webhook 签名密钥（测试用固定值，真实环境从 env 读取）."""
    return os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_test_skeleton")


@pytest.fixture
def mock_stripe_signature(stripe_webhook_secret):
    """生成合法 Stripe-Signature 的占位；实际实现需 stripe.Webhook.build_signature."""
    def _build(payload: bytes, secret: str = None) -> str:
        secret = secret or stripe_webhook_secret
        try:
            import stripe
            return stripe.WebhookSignature.build_header(payload, secret, "v1")
        except Exception:
            return "v1,0,t=0"
    return _build

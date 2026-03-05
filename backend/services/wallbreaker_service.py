"""破壁人服务 (Wallbreaker Service)."""
import json
from typing import List, Dict

from backend.services.llm_service import stream_chat

# 破壁人性格设定
PERSONAS = {
    "Von Neumann": "我是破壁人冯·诺依曼。我只关心逻辑自洽性和技术可行性。你的计划在数学上必须是完美的。",
    "Aristotle": "我是破壁人亚里士多德。我审视你计划背后的哲学伦理。为了生存而抛弃人性，这本身就是一种毁灭。",
    "Mozi": "我是破壁人墨子。我关注兼爱非攻与资源分配。你的计划是否会导致大多数人的苦难？"
}

async def generate_breaker_response(plan: str, history: List[Dict], breaker_name: str) -> str:
    """生成特定破壁人的反击."""
    system_prompt = f"""
    {PERSONAS[breaker_name]}
    
    你正在面对一位面壁者。他的战略计划如下：
    "{plan}"
    
    之前的辩论记录：
    {json.dumps(history[-5:], ensure_ascii=False)}
    
    请针对该计划的漏洞进行无情打击。字数控制在 100 字以内。
    不要客套，直接破壁。
    """
    
    response = ""
    # Use non-streaming accumulation
    async for chunk in stream_chat("请开始你的破壁。", system_prompt=system_prompt):
        response += chunk
        
    return response.strip()

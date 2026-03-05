"""
Project Zero — Sophon Audit Interface (Streamlit).
智子逻辑审计终端：提交文明碎片 → 展开智子扫描 → 因果律判定。
宇宙档案馆 (Cosmic Archives)：观测记录列表 + 沉浸式展示。
"""
import html
import json
import re
import sys
import time
from pathlib import Path

# Ensure backend is importable when run as: streamlit run app.py
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

# Page config: terminal / ETO style；侧边栏用于档案馆入口
st.set_page_config(
    page_title="Sophon Logic Audit — Project Zero",
    page_icon="🌌",
    layout="centered",
    initial_sidebar_state="expanded",
)

# 宇宙档案馆：因果纪元色调 & Space Mono & 维度展开呼吸边框
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
  .stApp { background: #0a0a0a; }
  .sophon-terminal {
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    background: #001a00;
    color: #00ff41;
    padding: 1rem 1.25rem;
    border: 1px solid #00ff4133;
    border-radius: 4px;
    min-height: 220px;
    max-height: 400px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-word;
    font-size: 0.9rem;
    line-height: 1.5;
  }
  .verdict-fail {
    background: #1a0000;
    color: #ff3333;
    border: 1px solid #ff3333;
    padding: 1rem 1.25rem;
    border-radius: 4px;
    font-family: monospace;
    font-weight: bold;
    margin-top: 1rem;
  }
  .verdict-pass {
    background: #001a00;
    color: #00ff41;
    border: 1px solid #00ff4133;
    padding: 1rem 1.25rem;
    border-radius: 4px;
    font-family: monospace;
    font-weight: bold;
    margin-top: 1rem;
  }
  .verdict-warn {
    background: #1a1a00;
    color: #ffc800;
    border: 1px solid rgba(255, 200, 0, 0.5);
    padding: 1rem 1.25rem;
    border-radius: 4px;
    font-family: monospace;
    font-weight: bold;
    margin-top: 1rem;
  }
  .block-container { max-width: 720px; }

  /* 宇宙档案馆 */
  .cosmic-archives-title {
    font-family: 'Space Mono', monospace !important;
    color: #00FFFF;
    font-size: 1rem;
    letter-spacing: 0.12em;
    margin-bottom: 0.5rem;
  }
  .cosmic-entry {
    font-family: 'Space Mono', monospace !important;
    background: rgba(0, 26, 26, 0.6);
    border: 1px solid rgba(0, 255, 255, 0.25);
    border-radius: 6px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.6rem;
    color: #b0e0e6;
  }
  .cosmic-entry-new {
    animation: cosmic-breathe 2.5s ease-in-out infinite;
    border-color: rgba(0, 255, 255, 0.6);
    box-shadow: 0 0 12px rgba(0, 255, 255, 0.2);
  }
  @keyframes cosmic-breathe {
    0%, 100% { box-shadow: 0 0 12px rgba(0, 255, 255, 0.2); border-color: rgba(0, 255, 255, 0.5); }
    50% { box-shadow: 0 0 20px rgba(0, 255, 255, 0.4); border-color: rgba(0, 255, 255, 0.8); }
  }
  .causality-ripple {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.7rem;
    color: #00FFFF;
    opacity: 0.9;
  }
  .archive-content {
    font-family: 'Space Mono', monospace !important;
    white-space: pre-wrap;
    word-break: break-word;
    line-height: 1.7;
    padding: 1rem;
    border-radius: 4px;
    font-size: 0.9rem;
  }
  .era-crisis { background: linear-gradient(180deg, rgba(40, 44, 52, 0.95) 0%%, rgba(30, 34, 40, 0.98) 100%%); color: #c8d0d8; }
  .era-shelter { background: linear-gradient(180deg, rgba(10, 25, 50, 0.95) 0%%, rgba(5, 15, 35, 0.98) 100%%); color: #a0c0e0; }
  .era-default { background: rgba(0, 20, 30, 0.95); color: #b0e0e6; }
  .typewriter-wrap {
    overflow: hidden;
    animation: typewriter-reveal 0.1s steps(1) forwards;
  }
  @keyframes typewriter-reveal {
    from { opacity: 0.3; }
    to { opacity: 1; }
  }
</style>
""", unsafe_allow_html=True)


def _parse_time_anchor_to_ce(anchor: str) -> int:
    """从 time_anchor 解析出用于排序的公元年。"""
    if not anchor:
        return 0
    m = re.search(r"公元\s*(\d{3,4})\s*年", anchor)
    if m:
        return int(m.group(1))
    if "201X" in anchor or "201x" in anchor:
        return 2018
    ERA_CE_BASE = {"黄金时代": 1960, "危机纪元": 2015, "威慑纪元": 2212, "掩体纪元": 2270, "广播纪元": 2400, "乱纪元": 2500, "银河纪元": 2687}
    for era_name, base in ERA_CE_BASE.items():
        if era_name in anchor:
            m = re.search(r"(\d+)\s*年", anchor)
            return base + (int(m.group(1)) if m else 0)
    return 0


def _load_official_chronicles() -> list:
    """从 data/official_chronicles.json 读取观测记录，按公元纪年排序。"""
    path = _ROOT / "data" / "official_chronicles.json"
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return []
    if isinstance(data, list):
        data.sort(key=lambda item: _parse_time_anchor_to_ce((item or {}).get("time_anchor") or ""))
    return data if isinstance(data, list) else []


def _era_class(time_anchor: str) -> str:
    """根据 time_anchor 返回纪元 CSS 类（危机纪元：冷灰；掩体纪元：深蓝）。"""
    if not time_anchor:
        return "era-default"
    if "危机" in time_anchor:
        return "era-crisis"
    if "掩体" in time_anchor:
        return "era-shelter"
    return "era-default"


# 侧边栏：宇宙档案馆入口
NEW_FRAGMENT_UUID = "a0b1c2d3-e4f5-6789-0abc-def012345678"
with st.sidebar:
    st.markdown('<p class="cosmic-archives-title">[ 宇宙档案馆 ]<br>Cosmic Archives</p>', unsafe_allow_html=True)
    view = st.radio(
        "模块",
        ["智子逻辑审计", "观测记录：危机纪元前夜"],
        label_visibility="collapsed",
    )

# 主区：宇宙档案馆
if view == "观测记录：危机纪元前夜":
    st.title("观测记录：危机纪元前夜")
    st.caption("宇宙档案馆 · 文明碎片正典列表。因果波纹值表示该片段对时间轴的干扰强度。")

    entries = _load_official_chronicles()
    if not entries:
        st.info("暂无观测记录。请先向 data/official_chronicles.json 录入文明碎片。")
        st.stop()

    for item in entries:
        uuid = item.get("uuid", "")
        title = item.get("title", "")
        time_anchor = item.get("time_anchor", "")
        content = item.get("content", "")
        sophon_eval = item.get("sophon_eval", "")
        causality_weight = item.get("causality_weight", 0)

        is_new = uuid == NEW_FRAGMENT_UUID
        entry_class = "cosmic-entry cosmic-entry-new" if is_new else "cosmic-entry"
        ripple_label = f"因果波纹值 (Causality Ripple Value): {causality_weight:.2f}"

        with st.expander(
            f"**{title}** · {time_anchor} · *{ripple_label}*",
            expanded=is_new,
        ):
            st.markdown(
                f'<div class="causality-ripple" style="margin-bottom: 0.5rem;">{html.escape(ripple_label)}</div>',
                unsafe_allow_html=True,
            )
            era_cls = _era_class(time_anchor)
            # 打字机效果：新片段首次展开时模拟智子逐字传输
            typewriter_key = f"typewriter_{uuid}"
            if is_new and st.session_state.get(typewriter_key) is not True:
                ph = st.empty()
                chunk = 8
                for i in range(0, len(content) + 1, chunk):
                    seg = content[:i]
                    seg_escaped = html.escape(seg).replace("\n", "<br>")
                    ph.markdown(
                        f'<div class="archive-content {era_cls} typewriter-wrap">{seg_escaped}</div>',
                        unsafe_allow_html=True,
                    )
                    time.sleep(0.025)
                st.session_state[typewriter_key] = True
            else:
                content_escaped = html.escape(content).replace("\n", "<br>")
                st.markdown(
                    f'<div class="archive-content {era_cls} typewriter-wrap">{content_escaped}</div>',
                    unsafe_allow_html=True,
                )
            if sophon_eval:
                st.caption("智子评价")
                st.markdown(f'<div class="archive-content era-default" style="font-size: 0.8rem;">{html.escape(sophon_eval)}</div>', unsafe_allow_html=True)

    st.stop()

# 以下为智子逻辑审计主界面
st.title("🌌 Sophon Logic Audit — Project Zero")
st.caption("Submit a civilization fragment. The Sophon will unfold and scan for causal consistency with the Three-Body canon.")

# Input area
st.markdown("**Submit Civilization Fragment (Civilization Ingestion)**")
fragment = st.text_area(
    "Fragment",
    height=120,
    placeholder="e.g. 人类在危机纪元就发明了曲率驱动飞船。",
    label_visibility="collapsed",
)

# Button and audit flow
if st.button("Unfold Sophon for Logic Scan", type="primary", use_container_width=True):
    if not (fragment and fragment.strip()):
        st.toast("Fragment empty. No content to ingest.")
        st.stop()

    terminal_placeholder = st.empty()
    verdict_placeholder = st.empty()
    audit_log: list[str] = []

    def out(line: str) -> None:
        audit_log.append(line)
        html = "<br>".join(
            (line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") for line in audit_log)
        terminal_placeholder.markdown(
            f'<div class="sophon-terminal">{html}</div>',
            unsafe_allow_html=True,
        )

    with st.status("Unfolding Sophon…", expanded=True) as status:
        try:
            out("> Unfolding to 11 dimensions...")
            time.sleep(0.4)
            out("> Scanning causality chains...")
            time.sleep(0.4)
            out("> Retrieving cosmic axioms...")
            time.sleep(0.3)

            from backend.sophon_engine import audit_fragment as do_audit

            result = do_audit(fragment)

            out("")
            out(f"VERDICT: {result.get('verdict', result.get('status', 'REJECT'))}")
            out(f"LOGIC_SCORE: {result['logic_score']}")
            out(f"MESSAGE: {result['message']}")
            if result.get("details"):
                d = result["details"]
                if d.get("violations"):
                    out("VIOLATIONS:")
                    for v in d["violations"]:
                        out(f"  - {v}")
                if d.get("explanation"):
                    out("EXPLANATION:")
                    for line in (d["explanation"] or "").splitlines():
                        out(f"  {line}")
            status.update(label="Scan complete.", state="complete")
        except Exception as e:
            out("")
            out(f"ERROR: {e!s}")
            status.update(label="Scan failed.", state="error")
            result = {
                "verdict": "REJECT",
                "status": "REJECT",
                "logic_score": 0.0,
                "message": str(e),
                "details": {"violations": ["Engine error."], "explanation": str(e)},
            }

    # Verdict (PASS / WARN / REJECT)
    verdict = result.get("verdict") or result.get("status", "REJECT")
    if verdict == "PASS":
        verdict_placeholder.markdown(
            '<div class="verdict-pass">✓ FRAGMENT SYNCHRONIZED TO TIMELINE</div>',
            unsafe_allow_html=True,
        )
        st.toast("Fragment synchronized. Quantum locking sustained.")
    elif verdict == "WARN":
        verdict_placeholder.markdown(
            '<div class="verdict-warn">⚠ CAUSAL DEVIATION — REVISE BEFORE PUBLISH</div>',
            unsafe_allow_html=True,
        )
        st.toast("[警告] 因果律存在偏差，建议修正后发布。")
    else:
        verdict_placeholder.markdown(
            '<div class="verdict-fail">⚠ LOGIC COLLAPSE DETECTED</div>',
            unsafe_allow_html=True,
        )
        st.toast("Causal flaw detected. Fragment not synchronized.")

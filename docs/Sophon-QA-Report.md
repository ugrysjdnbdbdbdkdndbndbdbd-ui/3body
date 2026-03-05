# Sophon-QA Report (智子质检报告)

**审计对象**: Project 3Body X 开发工程师 Agent 交付代码  
**审计时间**: 2026-02-18  
**审计范围**: frontend/src, backend/

---

## 验收状态: ⚠️ 警告（有条件通过）

## 威慑度评分: 72%

---

## 1. 维度打击 (Critical Issues)

### 🔴 [Security] XSS 漏洞 — SophonChat.vue
- **位置**: `frontend/src/components/SophonChat.vue:71`
- **问题**: `v-html="msg.text"` 直接渲染用户/AI 内容，存在 XSS 注入风险。
- **影响**: 若智子回复或用户输入包含恶意脚本，将执行任意 JavaScript。
- **修正**: 移除 `v-html`，改用 `{{ msg.text }}` 或引入 `DOMPurify` 对富文本做净化后再渲染。

### 🔴 [Immersion] 报错文案破坏沉浸感
- **位置**: 
  - `frontend/src/components/SophonChat.vue:50` — `"[连接错误]"`
  - `backend/services/llm_service.py:51,54` — `"发生错误"`
- **问题**: PRD 要求错误信息必须符合三体世界观，禁止出现技术裸报错（如 "Error 500"）。
- **修正**: 
  - 前端: `"系统受到强互作用力干扰，智子连接暂时中断。"`
  - 后端: `"智子遭遇未知扰动，无法完成请求。"`

### 🔴 [Bug] 缺少 HTTP 错误处理 — 多处
- **位置**: 
  - `frontend/src/views/GalleryView.vue:12-13`
  - `frontend/src/views/ChronicleView.vue:21-28`
  - `frontend/src/stores/universe.ts:36-37`
- **问题**: 未检查 `res.ok` 即调用 `res.json()`，当 API 返回 4xx/5xx 时将抛出未捕获异常。
- **影响**: 生产环境崩溃、白屏、无用户可理解的反馈。
- **修正**: 在解析前检查 `if (!res.ok)`，并抛出自定义错误或展示沉浸式错误文案。

### 🔴 [Logic] ChronicleView 筛选逻辑失效
- **位置**: `frontend/src/views/ChronicleView.vue`
- **问题**: 
  1. `selectedEra` 在 `onMounted` 时恒为 `null`，era 筛选从未生效；
  2. `scale` 和 `filteredEvents` 未关联，`filteredEvents` 始终等于 `events.value`。
- **影响**: 纪元筛选、时间尺度切换无实际效果。

### 🟠 [Cleanliness] 魔法数字
- **位置**: `backend/routers/universe.py:29` — `3.15576e7`
- **问题**: 秒/年换算系数无常量命名，可读性差。
- **修正**: `SECONDS_PER_YEAR = 31_557_600`

### 🟠 [Inconsistency] 设计与 PRD 不一致
- **位置**: `frontend/src/assets/main.css:6` — `--color-space: #000000`
- **问题**: PRD 指定 Dark Forest 背景为 `#050505`，此处使用纯黑，与 MainLayout 的 `#050505` 不一致。
- **修正**: 统一为 `#050505`。

### 🟠 [Dead Code] StarMapNav 未接入
- **位置**: `frontend/src/components/StarMapNav.vue`
- **问题**: 组件已实现，但未在 MainLayout 或任何 View 中挂载；UniverseView 注释提到「星图入口在 StarMapNav」却未使用。
- **影响**: 用户无法通过星图导航切换扇区。

---

## 2. 思想钢印 (Code Suggestions)

1. **类型复用**: `UniverseMetrics` 在 `stores/universe.ts` 与 `types/universe.ts` 重复定义；建议统一由 `types/` 导出，store 仅引用。
2. **Tailwind 命名**: `sophone` 存在拼写偏差，建议统一为 `sophon` 或保留并文档化（若为刻意命名）。
3. **生产环境日志**: `router/index.ts` 中 `console.info` 仅在 `import.meta.env.DEV` 下执行，符合「禁止生产 console」要求；建议长期改用 `import.meta.env.DEV && console.info(...)` 或结构化 logger，避免误留调试输出。
4. **移动端适配**: 需系统性检查 `ChronicleView`、`GalleryView` 在移动端的布局与触摸体验，确保 PRD 的 Responsiveness 要求。
5. **UniverseStore 错误处理**: `fetchMetrics` 应捕获 `fetch` 失败和 `res.json()` 异常，并设置 `metrics.value = null` 或 `loading.error`，避免静默失败。

---

## 3. 已达标项

- ✅ Tech Stack: Vue 3 (Script Setup) + TS + Tailwind + Naive UI / FastAPI + Pydantic
- ✅ 类型定义: 前端 Interface、后端 Pydantic 齐全
- ✅ Dark Forest 设计: MainLayout、主题色 `#00FFFF`、背景 `#050505` 已落实
- ✅ 智子人格: `llm_service.py` System Prompt 符合傲慢、冷淡口吻
- ✅ 变量命名: 整体语义化，无明显硬编码字符串散落
- ✅ 无 `console.log` 残留于生产逻辑（router 的 info 受 DEV  guards）

---

## 4. 修正优先级

| 优先级 | 项目 | 预估工时 |
|--------|------|----------|
| P0 | XSS 修复 (v-html → 安全渲染) | 0.5h |
| P0 | HTTP 错误处理（Gallery/Chronicle/UniverseStore） | 1h |
| P1 | 沉浸式报错文案替换 | 0.5h |
| P1 | ChronicleView 筛选逻辑修复 | 1h |
| P2 | StarMapNav 接入 MainLayout | 0.5h |
| P2 | main.css #050505 统一 | 5min |
| P2 | universe.py 魔法数字提取 | 5min |

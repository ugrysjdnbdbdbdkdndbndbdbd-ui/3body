# Changelog

## [1.0.0] - 2025-03（GitHub 封板交付）

### 功能

- **智子终端**：RAG 检索 + 流式对话，支持 Ollama / 自定义 API
- **人物志**：10 位核心人物档案，选择式对话 + **人物 AI 对话**（人设严格约束、多轮历史）
- **人物对话**：对话式气泡 UI，预埋问题引导，支持 API Key / Base URL / Model 配置（默认本地 Ollama）
- **宇宙广播**：威慑度、纪元、舰队距离等仪表盘
- **编年史**：时间轴、百科、外传
- **二向箔画廊**：作品展示与收藏
- **小宇宙 (647)**：维生系统模拟、时间胶囊、质量归还
- **黑暗森林**、**面壁计划**、**红岸**、**三体摆** 等扇区

### 后端

- FastAPI + SQLite + 可选 ChromaDB RAG
- 人物对话接口 `POST /api/chat/figure`（多轮 history、严格人设与三体世界观）
- RAG 懒加载、GZip 压缩、人物列表/宇宙指标短缓存
- 环境变量：`3BODY_LLM_BASE_URL`、`3BODY_LLM_MODEL`、`3BODY_LLM_API_KEY`（可选）

### 前端

- Vue 3 + TypeScript + Vite + Naive UI + Pinia
- 路由懒加载、构建分包（vue-vendor、naive-ui）
- 字体异步加载、首屏请求延后，API 基址统一（`apiUrl`）

### 文档与交付

- README 快速开始、环境变量说明
- `.gitignore`、`LICENSE`（MIT）
- 封板报告：`docs/RELEASE-1.0-FREEZE.md`

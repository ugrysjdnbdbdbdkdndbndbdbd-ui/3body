# 3body — 三体宇宙 AI 沉浸式社区

基于《三体》宇宙观的 AI 社区：智子终端、人物志对话、编年史、宇宙广播、二向箔画廊、小宇宙等。

## 技术栈

- **前端**: Vue 3 (Script Setup) + TypeScript + Vite + TailwindCSS + Pinia + Vue Router + Naive UI
- **后端**: Python FastAPI + Uvicorn + Pydantic + SQLAlchemy (SQLite)
- **AI**: Ollama 兼容 API / 自定义 LLM；可选 LangChain + ChromaDB（三体原著 RAG）

## 功能概览

| 模块       | 说明 |
|------------|------|
| 智子终端   | RAG 检索 + 流式对话 |
| 人物志     | 核心人物档案 + **与人物 AI 对话**（人设与三体世界观约束） |
| 宇宙广播   | 威慑度、纪元、舰队距离等仪表盘 |
| 编年史     | 时间轴、百科、外传 |
| 二向箔画廊 | 作品展示与收藏 |
| 小宇宙 647 | 维生系统、时间胶囊、质量归还 |
| 黑暗森林 / 面壁计划 / 红岸 / 三体摆 等 | 各扇区互动 |

## 项目结构（Monorepo）

```
3body/
├── data/              # 三体原著 .txt，供 RAG 入库（可选）
├── frontend/          # Vue 3 + Vite
├── backend/           # FastAPI + RAG
├── docs/              # 文档与封板报告
└── README.md
```

## 快速开始

### 后端

```bash
cd 3body
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

- API 文档: http://127.0.0.1:8000/docs  
- 健康检查: http://127.0.0.1:8000/health  

### 前端

```bash
cd 3body/frontend
npm install
npm run dev
```

访问地址以终端输出为准，默认 **http://localhost:5173**。若 5173 被占用，Vite 会使用 5174、5175 等。

### 生产 / 跨端口访问

前端需能访问后端 API。开发时可用 Vite 代理（已配置 `/api` → `http://127.0.0.1:8000`）。  
静态部署时设置环境变量：

- `VITE_API_BASE=http://你的后端地址`（如 `http://127.0.0.1:8000`）

构建：`npm run build`，产出在 `frontend/dist/`。

## 智子与人物对话（LLM）

流式对话使用 **Ollama 兼容 API**。通用情况使用本地 Ollama，无需配置。

### 本地 Ollama（默认）

1. 安装并启动 [Ollama](https://ollama.com)，拉取模型（如 `deepseek-chat` 或 `llama2`）。
2. 后端默认连接 `http://localhost:11434`，无需额外配置。

### 自定义 / 云端 API

在项目根目录创建 `backend/.env`，或设置环境变量（前缀 `3BODY_`）：

| 变量 | 说明 | 默认 |
|------|------|------|
| `3BODY_LLM_BASE_URL` | LLM API 基址 | `http://localhost:11434` |
| `3BODY_LLM_MODEL` | 模型名 | `deepseek-chat` |
| `3BODY_LLM_API_KEY` | API Key（可选，云端时填写） | 空 |

前端在「人物志 → 与 TA 对话 → API / Ollama 连接设置」中可覆盖 API Key、Base URL、Model（仅当次会话或持久化到本地）。

### RAG 知识库（三体原著，可选）

1. 将原著 `.txt` 放入项目根目录 **`data/`** 下。
2. 执行一次入库（会下载中文 embedding 模型，较慢）：
   ```bash
   source .venv/bin/activate
   python -m backend.rag.ingest
   ```
3. 之后智子对话会先检索向量再结合原文回答。无 `data/` 或未入库时，RAG 在首次对话时懒加载并可能跳过。

## 设计系统

- **背景**: #050505 / #000510 (Deep Space)
- **主色**: #00FFFF (Cherenkov Blue)
- **警示**: #FF3333 (Red Coast Red)
- **字体**: 等宽数据、衬线叙事

## 文档

- 封板报告与测试结论: `docs/RELEASE-1.0-FREEZE.md`
- 版本变更: `CHANGELOG.md`

## License

MIT. 见 [LICENSE](LICENSE)。

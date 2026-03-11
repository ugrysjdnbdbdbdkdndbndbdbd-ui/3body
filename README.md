# 3body — 三体体验沙盒

> 基于《三体》宇宙观的沉浸式体验沙盒：与智子对话、与书中人物交谈、穿越编年史、漫步黑暗森林、归还小宇宙质量……

## 项目简介

**3body** 是一个以《三体》世界观为背景的 **体验沙盒** 项目：结合 AI 对话、编年史、人物志、宇宙广播、二向箔画廊、小宇宙等模块，让读者在本地或自托管环境中「进入」三体宇宙，与智子对话、与罗辑/叶文洁等核心人物进行符合人设的 AI 对话，并体验黑暗森林、面壁计划、红岸、三体摆等扇区互动。

- **定位**：三体宇宙体验沙盒（非官方），适合书迷、二次创作与 AI 应用实践。
- **技术**：Vue 3 + FastAPI + 可选 Ollama/LLM + 可选 RAG（原著检索增强）。
- **开源**：MIT 许可证，可自由克隆、修改与部署。

---

## 功能模块（扇区）

| 扇区 | 说明 |
|------|------|
| **智子终端** | 与智子流式对话，可选 RAG 检索三体原著后回答 |
| **人物志** | 10 位核心人物档案；**与人物 AI 对话**（严格人设与三体世界观，多轮对话） |
| **宇宙广播** | 威慑度、纪元、舰队距离等仪表盘，全站色调随威慑度变化 |
| **编年史** | 时间轴、百科、外传，文明历程一览 |
| **二向箔画廊** | 作品展示与收藏 |
| **小宇宙 647** | 维生系统模拟、时间胶囊、质量归还 |
| **黑暗森林** | 星图、点火/打击/输血等互动 |
| **面壁计划** | 思想钢印、面壁/破壁对话 |
| **红岸控制台** | 信号与广播 |
| **三体摆** | 环境站、单摆、脱水控制台 |
| 其他扇区 | 阶梯计划、四维碎片、掩体世界、水滴、科学边界等 |

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 (Script Setup) + TypeScript + Vite + TailwindCSS + Pinia + Vue Router + Naive UI |
| 后端 | Python FastAPI + Uvicorn + Pydantic + SQLAlchemy (SQLite) |
| AI 对话 | Ollama 兼容 API / 自定义 LLM；可选 LangChain + ChromaDB（三体原著 RAG） |

---

## 快速开始

### 环境要求

- **Node.js** 18+（前端）
- **Python** 3.9+（后端）
- 可选： [Ollama](https://ollama.com)（本地 LLM，用于智子与人物对话）

### 1. 克隆项目

```bash
git clone https://github.com/ugrysjdnbdbdkdndbndbdbd-ui/3body.git
cd 3body
```

### 2. 启动后端

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

- API 文档：http://127.0.0.1:8000/docs  
- 健康检查：http://127.0.0.1:8000/health  

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

浏览器访问终端输出的地址，默认 **http://localhost:5173**。若 5173 被占用，Vite 会自动使用 5174、5175 等。

### 4. 可选：智子 / 人物对话（LLM）

- **本地 Ollama**：安装并启动 Ollama，拉取模型（如 `deepseek-chat`）。后端默认连接 `http://localhost:11434`，无需额外配置。
- **自定义 API**：在项目根或 `backend/` 下创建 `.env`，设置 `3BODY_LLM_BASE_URL`、`3BODY_LLM_MODEL`、`3BODY_LLM_API_KEY`（可选）。  
  前端在「人物志 → 与 TA 对话」中可配置 API Key / Base URL / Model（默认使用本地 Ollama）。

### 5. 可选：RAG 知识库（三体原著）

1. 将原著 `.txt` 放入项目根目录 **`data/`** 下。  
2. 执行一次入库（会下载中文 embedding 模型，较慢）：
   ```bash
   source .venv/bin/activate
   python -m backend.rag.ingest
   ```
3. 之后智子对话会先检索原文再回答。未配置时 RAG 懒加载或跳过。

---

## 项目结构

```
3body/
├── data/              # 三体原著 .txt、百科/外传 JSON（可选 RAG 数据源）
├── frontend/          # Vue 3 + Vite 前端
├── backend/           # FastAPI 后端、RAG、人物对话等 API
├── docs/              # 文档与封板报告
├── PRD/               # 产品需求文档
├── CHANGELOG.md       # 版本变更
└── README.md          # 本说明
```

---

## 环境变量（后端）

| 变量 | 说明 | 默认 |
|------|------|------|
| `3BODY_LLM_BASE_URL` | LLM API 基址 | `http://localhost:11434` |
| `3BODY_LLM_MODEL` | 模型名 | `deepseek-chat` |
| `3BODY_LLM_API_KEY` | API Key（云端时填写） | 空 |
| `3BODY_DATABASE_URL` | 数据库连接 | `sqlite+aiosqlite:///3body.db` |

示例见 `backend/.env.example`。

---

## 生产部署

- **前端**：`cd frontend && npm run build`，产出在 `frontend/dist/`。部署时需设置 `VITE_API_BASE` 为后端地址（如 `https://api.example.com`），以便 API 请求正确转发。
- **后端**：使用 Uvicorn 或 Gunicorn 挂载 `backend.main:app`，并配置反向代理与 HTTPS。

---

## 设计系统

- **背景**：深空黑 `#050505` / `#000510`
- **主色**：切伦科夫蓝 `#00FFFF`
- **警示**：红岸红 `#FF3333`
- **字体**：等宽数据展示，衬线叙事

---

## 文档与链接

- 封板与测试报告：`docs/RELEASE-1.0-FREEZE.md`、`docs/RELEASE-2.0-FREEZE.md`
- 版本历史：`CHANGELOG.md`
- 《三体》为刘慈欣所著科幻作品，本项目为爱好者向体验沙盒，与官方无关。

---

## License

MIT. 详见 [LICENSE](LICENSE)。

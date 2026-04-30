# 🌍 文明纪元 — Civilization Simulator

> 由 **LLM Agent** 驱动的文明模拟游戏。你以「神」的身份观察 4 个 AI 文明的兴衰，偶尔降下神迹干预历史进程。

---

## ✨ 核心特色

| 特性 | 说明 |
|------|------|
| 🏛️ **4 个 AI 文明** | 中华、罗马、埃及、阿兹特克，各有独特性格 |
| 🧠 **LLM 决策引擎** | 每个文明的领袖由 AI (DeepSeek × OpenRouter) 实时决策 |
| 🗺️ **精致 Web UI** | 暗色主题 Canvas 地图、三栏布局、实时更新 |
| ⚡ **神之干预** | 作为「神」，你可以降下祝福、灾难或神谕 |
| 🔄 **实时推送** | WebSocket 推送，无需刷新即可看到文明演化 |
| 🌐 **中英双语** | 一键切换中文/英文界面 |
| 💾 **自动存档** | SQLite 持久化，关闭后自动保存进度 |

---

## 🎮 快速开始

### 前置条件

- Python 3.11+
- [OpenRouter API Key](https://openrouter.ai/keys)（用于 LLM 决策）
- 火山方舟 API Key（可选，预留接口）

### 安装

```bash
# 克隆项目
git clone git@github.com:badpx/civilization.git
cd civilization

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 配置环境变量

```bash
# 复制 .env 模板
cp .env.example .env

# 编辑 .env，填入你的 API Key
export OPENROUTER_API_KEY="sk-or-v1-你的key"
export ARK_API_KEY="你的火山方舟key"
```

### 启动

```bash
# 方式一：一键启动
./start.sh

# 方式二：手动启动
source venv/bin/activate
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

浏览器打开 **http://localhost:8000**

---

## 🏛️ 游戏玩法

### 文明

| 文明 | 领袖 | 性格 | 颜色 |
|------|------|------|------|
| 🏮 中华 | 秦始皇 | 智慧、沉稳、善于长远规划 | 🔴 #FF0000 |
| ⚔️ 罗马 | 恺撒 | 勇猛、果断、追求荣耀 | 🔵 #0000FF |
| 🔺 埃及 | 拉美西斯二世 | 神秘、虔诚、热爱永恒建筑 | 🟡 #FFD700 |
| 🌋 阿兹特克 | 蒙特祖玛 | 狂野、好战、崇尚力量 | 🟢 #00AA00 |

### 资源系统

| 资源 | 图标 | 用途 |
|------|------|------|
| 粮食 | 🌾 | 人口增长 |
| 产能 | ⚒️ | 建造建筑和奇观 |
| 金币 | 💰 | 维护军队、贸易 |
| 科技 | 📚 | 提升科技等级 |
| 文化 | 🎭 | 文化扩张与政策 |

### 神之干预

| 干预 | 效果 |
|------|------|
| 🌟 **祝福** | 赐予福佑：粮食+8，产能+8，金币+8，幸福+5 |
| ⚡ **灾难** | 降下天罚：所有资源-8，人口-2，幸福-5 |
| 📜 **神谕** | 赐予智慧：科技+10，文化+10，科技等级+1 |

---

## 🧩 技术架构

```
civilization/
├── start.sh                 # 一键启动脚本
├── requirements.txt         # Python 依赖
├── .gitignore               # Git 忽略规则
├── backend/                 # 后端 (FastAPI)
│   ├── main.py              # API 路由 + WebSocket
│   ├── models.py            # 数据模型 (Pydantic)
│   ├── config.py            # 配置常量
│   ├── database.py          # SQLite 持久化
│   ├── game_engine.py       # 核心游戏循环
│   ├── llm_agent.py         # LLM Agent (OpenRouter)
│   ├── events.py            # 事件系统
│   └── prompts/             # AI 提示模板
├── frontend/                # 前端 (原生 HTML/CSS/JS)
│   ├── index.html           # 主页面
│   ├── css/style.css        # 暗色主题样式
│   └── js/
│       ├── app.js           # 主应用逻辑 + i18n
│       ├── map.js           # Canvas 地图渲染
│       ├── panels.js        # UI 面板管理
│       └── websocket.js     # WebSocket 通信
└── data/                    # 游戏存档 (SQLite)
```

### 技术栈

| 层级 | 技术 |
|------|------|
| **后端** | Python 3.11, FastAPI, Uvicorn |
| **AI 引擎** | OpenRouter (DeepSeek), OpenAI SDK |
| **数据库** | SQLite (aiosqlite) |
| **前端** | HTML5 Canvas, CSS3, vanilla JS |
| **通信** | WebSocket (实时推送), REST API |
| **数据模型** | Pydantic v2 |

---

## 🗺️ API 文档

### REST API

| 方法 | 路由 | 说明 |
|------|------|------|
| `GET` | `/` | 前端主页 |
| `GET` | `/api/state` | 获取完整游戏状态 |
| `POST` | `/api/game/start` | 开始新游戏 |
| `POST` | `/api/game/next-turn` | 下一回合 |
| `POST` | `/api/game/auto` | 启动自动播放 |
| `POST` | `/api/game/stop` | 停止自动播放 |
| `POST` | `/api/divine/action` | 神之干预 |
| `GET` | `/api/civilizations` | 所有文明概要 |
| `GET` | `/api/civilizations/{id}` | 文明详细信息 |

### WebSocket

`ws://localhost:8000/ws`

推送消息类型：`state`、`event`、`game_over`

---

## 🧪 开发

```bash
# 验证导入无报错
python -c "from backend.models import *; print('OK')"

# 启动开发模式（热重载）
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 📄 License

MIT

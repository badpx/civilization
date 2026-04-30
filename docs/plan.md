# 🌍 文明纪元 — LLM 驱动的文明模拟游戏

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** 构建一个精致的 Web 端文明模拟游戏，玩家以"神"的身份观察并偶尔干预由 LLM 驱动的 AI 文明的演化。

**Architecture:** Python FastAPI 后端 + 精致 Web 前端，每个文明领袖由火山方舟 LLM API 驱动，WebSocket 实时推送，SQLite 存储游戏状态。

**Tech Stack:** Python 3.11, FastAPI, Uvicorn, SQLite, OpenAI-compatible API (火山方舟), HTML5 Canvas/CSS3/JS (原生，无框架依赖)

---

## 🎮 游戏设计

### 文明设定
- 4 个 AI 文明，各有独特性格和起始条件
- 每个文明由一个 LLM Agent 驱动领袖决策
- 回合制，每回合 = 1 年

### 资源系统
| 资源 | 用途 |
|------|------|
| 🌾 粮食 (Food) | 人口增长 |
| ⚒️ 产能 (Production) | 建造奇观/单位 |
| 💰 金币 (Gold) | 维护/贸易/雇佣 |
| 📚 科技 (Science) | 解锁科技树 |
| 🎭 文化 (Culture) | 扩张边界/政策 |

### 城市系统
- 每个文明起始 1 座城市，可扩张
- 城市有位置、人口、产出、建筑
- 特殊建筑：奇观（万里长城、金字塔等）

### 外交系统
- 关系值：-100（战争）到 +100（同盟）
- 行动：宣战、结盟、贸易协定、求和

### 事件系统
- 每回合有概率触发事件（旱灾、瘟疫、丰收、发现）
- 神可以主动降下事件

### 神之干预
- 🌟 祝福：加速产出、治愈瘟疫、赐予丰收
- ⚡ 灾难：旱灾、地震、洪水
- 📜 神谕：影响 AI 决策倾向

---

## 📐 技术架构

```
┌─────────────────────────────────────────────┐
│                  Web Frontend                │
│  ┌─────────┐ ┌──────────┐ ┌──────────────┐  │
│  │ 地图视图 │ │ 控制面板 │ │  事件日志    │  │
│  │ (Canvas) │ │ (God UI) │ │  (Timeline)  │  │
│  └─────────┘ └──────────┘ └──────────────┘  │
│              WebSocket Client                │
└──────────────────┬──────────────────────────┘
                   │ ws://
┌──────────────────┴──────────────────────────┐
│              FastAPI Backend                  │
│  ┌────────────┐  ┌────────────────────────┐  │
│  │ Game Engine │  │   LLM Agent Manager   │  │
│  │  (Turn Sim) │  │  (4x 火山方舟 Agent)   │  │
│  └─────┬──────┘  └──────────┬─────────────┘  │
│        │                    │                 │
│  ┌─────┴────────────────────┴─────────────┐  │
│  │         Game State (SQLite)            │  │
│  │  civilizations | cities | events | log │  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

---

## 📁 项目结构

```
civilization/
├── backend/
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置（API key, 游戏参数）
│   ├── models.py            # 数据模型 (Pydantic)
│   ├── database.py          # SQLite 管理
│   ├── game_engine.py       # 核心游戏引擎
│   ├── llm_agent.py         # LLM Agent 封装
│   ├── events.py            # 事件系统
│   ├── websocket.py         # WebSocket 管理
│   └── prompts/             # LLM Prompt 模板
│       ├── system.txt       # 通用系统提示
│       ├── chinese.txt      # 中华文明
│       ├── roman.txt        # 罗马文明
│       ├── egyptian.txt     # 埃及文明
│       └── aztec.txt        # 阿兹特克文明
├── frontend/
│   ├── index.html           # 主页面
│   ├── css/
│   │   └── style.css        # 样式
│   ├── js/
│   │   ├── app.js           # 主逻辑
│   │   ├── map.js           # 地图渲染
│   │   ├── websocket.js     # WS 通信
│   │   └── panels.js        # UI 面板
│   └── assets/
│       └── icons/           # 资源/建筑图标
├── data/
│   └── civilization.db      # SQLite 数据库
├── requirements.txt
└── run.py                   # 启动脚本
```

---

## 🚀 实施任务

### Phase 1: 基础骨架

#### Task 1: 项目初始化
**Objective:** 创建项目结构和依赖

**Files:**
- Create: `civilization/requirements.txt`
- Create: `civilization/run.py`
- Create: `civilization/backend/config.py`

**Step 1: 创建 requirements.txt**
```
fastapi==0.115.0
uvicorn[standard]==0.30.0
websockets==12.0
openai==1.40.0
aiosqlite==0.20.0
pydantic==2.8.0
```

**Step 2: 创建 run.py**
```python
#!/usr/bin/env python3
"""文明纪元 - 启动脚本"""
import uvicorn
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
```

**Step 3: 创建 config.py**
```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# 火山方舟 API 配置
ARK_API_KEY = os.environ.get("ARK_API_KEY", "")
ARK_BASE_URL = os.environ.get("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/coding/v3")
ARK_MODEL = os.environ.get("ARK_MODEL", "doubao-seed-2.0-lite")

# 游戏配置
NUM_CIVILIZATIONS = 4
MAP_WIDTH = 30
MAP_HEIGHT = 20
MAX_TURNS = 200

# WebSocket 配置
WS_BROADCAST_INTERVAL = 0.1  # 秒
```

**Step 4: 验证**
```bash
cd civilization && pip install -r requirements.txt
python run.py  # 应能启动（会因缺少 main.py 报错，正常）
```

---

#### Task 2: 数据模型定义
**Objective:** 定义所有游戏实体的数据结构

**Files:**
- Create: `civilization/backend/models.py`

**Step 1: 创建完整模型文件**
```python
"""游戏数据模型"""
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional
from datetime import datetime
import json

# === 枚举类型 ===

class ResourceType(str, Enum):
    FOOD = "food"
    PRODUCTION = "production"
    GOLD = "gold"
    SCIENCE = "science"
    CULTURE = "culture"

class TerrainType(str, Enum):
    PLAINS = "plains"
    FOREST = "forest"
    HILLS = "hills"
    MOUNTAIN = "mountain"
    WATER = "water"
    DESERT = "desert"
    GRASSLAND = "grassland"

class BuildingType(str, Enum):
    GRANARY = "granary"           # 粮仓 +2 粮食
    WORKSHOP = "workshop"         # 工坊 +2 产能
    MARKET = "market"             # 市场 +2 金币
    LIBRARY = "library"           # 图书馆 +2 科技
    AMPHITHEATER = "amphitheater" # 剧场 +2 文化
    WALLS = "walls"               # 城墙 +10 防御
    TEMPLE = "temple"             # 神庙 +1 文化 +1 科技
    AQUEDUCT = "aqueduct"         # 水渠 +1 粮食 +1 人口上限

class WonderType(str, Enum):
    PYRAMID = "pyramid"           # 金字塔 +5 科技
    GREAT_WALL = "great_wall"     # 万里长城 +20 防御
    COLOSSEUM = "colosseum"       # 竞技场 +5 文化
    HANGING_GARDEN = "hanging_garden" # 空中花园 +3 粮食
    LIGHTHOUSE = "lighthouse"     # 灯塔 +2 金币 所有城市
    LIBRARY_ALEX = "library_alex" # 亚历山大图书馆 +5 科技

class ActionType(str, Enum):
    BUILD = "build"
    RESEARCH = "research"
    DIPLOMACY = "diplomacy"
    MILITARY = "military"
    CULTURE = "culture"
    NONE = "none"

class RelationLevel(str, Enum):
    WAR = "war"           # -100 ~ -60
    HOSTILE = "hostile"   # -60 ~ -20
    NEUTRAL = "neutral"   # -20 ~ 20
    FRIENDLY = "friendly" # 20 ~ 60
    ALLIED = "allied"     # 60 ~ 100

class EventType(str, Enum):
    # 自然事件
    DROUGHT = "drought"
    FLOOD = "flood"
    PLAGUE = "plague"
    EARTHQUAKE = "earthquake"
    BOUNTIFUL_HARVEST = "bountiful_harvest"
    GOLDEN_AGE = "golden_age"
    DISCOVERY = "discovery"
    # 神之事件
    DIVINE_BLESSING = "divine_blessing"
    DIVINE_WRATH = "divine_wrath"
    DIVINE_ORACLE = "divine_oracle"

# === 核心模型 ===

class Resources(BaseModel):
    food: int = 0
    production: int = 0
    gold: int = 0
    science: int = 0
    culture: int = 0

class City(BaseModel):
    id: str
    name: str
    x: int
    y: int
    population: int = 1
    food_stored: int = 0
    food_needed: int = 10
    buildings: list[BuildingType] = []
    wonders: list[WonderType] = []
    terrain: TerrainType = TerrainType.PLAINS
    defense: int = 10

    def get_output(self) -> Resources:
        """计算城市产出"""
        base = Resources(
            food=2, production=1, gold=1, science=1, culture=0
        )
        terrain_bonus = {
            TerrainType.PLAINS: Resources(food=1),
            TerrainType.GRASSLAND: Resources(food=2),
            TerrainType.FOREST: Resources(production=1, food=1),
            TerrainType.HILLS: Resources(production=2),
            TerrainType.DESERT: Resources(gold=1),
        }
        base += terrain_bonus.get(self.terrain, Resources())

        building_bonus = {
            BuildingType.GRANARY: Resources(food=2),
            BuildingType.WORKSHOP: Resources(production=2),
            BuildingType.MARKET: Resources(gold=2),
            BuildingType.LIBRARY: Resources(science=2),
            BuildingType.AMPHITHEATER: Resources(culture=2),
            BuildingType.TEMPLE: Resources(culture=1, science=1),
            BuildingType.AQUEDUCT: Resources(food=1),
        }
        for b in self.buildings:
            base += building_bonus.get(b, Resources())

        # 人口加成
        base.food += self.population
        base.production += self.population // 2
        base.gold += self.population // 3

        return base

class Civilization(BaseModel):
    id: str
    name: str
    leader_name: str
    personality: str  # AI 性格描述
    color: str        # 地图颜色 (hex)
    cities: list[City] = []
    resources: Resources = Resources()
    total_resources: Resources = Resources()
    tech_level: int = 1
    military_power: int = 10
    culture_level: int = 0
    happiness: int = 50  # 0-100
    relations: dict[str, int] = {}  # civ_id -> relation score
    history: list[str] = []  # 最近的决策记录
    is_alive: bool = True
    turn_founded: int = 0

class GameEvent(BaseModel):
    id: str
    turn: int
    event_type: EventType
    title: str
    description: str
    target_civ_id: Optional[str] = None
    effects: dict = {}  # 具体效果
    timestamp: datetime = Field(default_factory=datetime.now)

class DivineAction(BaseModel):
    """神的干预"""
    action_type: EventType  # DIVINE_BLESSING / DIVINE_WRATH / DIVINE_ORACLE
    target_civ_id: str
    description: str

class GameState(BaseModel):
    turn: int = 0
    civilizations: list[Civilization] = []
    events: list[GameEvent] = []
    is_running: bool = False
    map_data: list[list[TerrainType]] = []  # 2D 地形图
```

**Step 2: 验证**
```bash
cd civilization && python -c "from backend.models import *; print('Models OK')"
```

---

#### Task 3: 数据库层
**Objective:** SQLite 持久化游戏状态

**Files:**
- Create: `civilization/backend/database.py`

**Step 1: 创建数据库管理器**（完整代码，包含表创建、CRUD、序列化）

```python
"""SQLite 数据库管理"""
import aiosqlite
import json
from pathlib import Path
from .config import DATA_DIR
from .models import GameState, Civilization, City, GameEvent

DB_PATH = DATA_DIR / "civilization.db"

async def init_db():
    """初始化数据库"""
    async with aiosqlite.connect(str(DB_PATH)) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS game_state (
                id INTEGER PRIMARY KEY,
                turn INTEGER,
                data TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                turn INTEGER,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def save_state(state: GameState):
    """保存游戏状态"""
    async with aiosqlite.connect(str(DB_PATH)) as db:
        data = json.dumps(state.model_dump(), ensure_ascii=False, default=str)
        await db.execute(
            "INSERT OR REPLACE INTO game_state (id, turn, data) VALUES (1, ?, ?)",
            (state.turn, data)
        )
        await db.commit()

async def load_state() -> GameState | None:
    """加载游戏状态"""
    async with aiosqlite.connect(str(DB_PATH)) as db:
        cursor = await db.execute(
            "SELECT data FROM game_state WHERE id = 1"
        )
        row = await cursor.fetchone()
        if row:
            return GameState.model_validate_json(row[0])
    return None

async def save_event(event: GameEvent):
    """保存事件"""
    async with aiosqlite.connect(str(DB_PATH)) as db:
        data = json.dumps(event.model_dump(), ensure_ascii=False, default=str)
        await db.execute(
            "INSERT OR REPLACE INTO events (id, turn, data) VALUES (?, ?, ?)",
            (event.id, event.turn, data)
        )
        await db.commit()

async def get_events(turn: int = None, limit: int = 50) -> list[GameEvent]:
    """获取事件列表"""
    async with aiosqlite.connect(str(DB_PATH)) as db:
        if turn:
            cursor = await db.execute(
                "SELECT data FROM events WHERE turn = ? ORDER BY created_at DESC LIMIT ?",
                (turn, limit)
            )
        else:
            cursor = await db.execute(
                "SELECT data FROM events ORDER BY turn DESC, created_at DESC LIMIT ?",
                (limit,)
            )
        rows = await cursor.fetchall()
        return [GameEvent.model_validate_json(row[0]) for row in rows]
```

---

#### Task 4: LLM Agent 封装
**Objective:** 封装火山方舟 API，让每个文明领袖能"思考"

**Files:**
- Create: `civilization/backend/llm_agent.py`
- Create: `civilization/backend/prompts/system.txt`
- Create: `civilization/backend/prompts/chinese.txt`
- Create: `civilization/backend/prompts/roman.txt`
- Create: `civilization/backend/prompts/egyptian.txt`
- Create: `civilization/backend/prompts/aztec.txt`

**Step 1: 系统提示模板 (prompts/system.txt)**
```
你是一个古代文明的领袖，正在管理你的帝国。

当前状态：
- 回合：{turn}
- 人口：{population}
- 资源：粮食{food} 产能{production} 金币{gold} 科技{science} 文化{culture}
- 城市数量：{num_cities}
- 军事力量：{military}
- 幸福度：{happiness}%
- 科技等级：{tech_level}

你需要做出决策。请用 JSON 格式回复：
{
    "action": "build|research|diplomacy|military|culture",
    "target": "具体目标",
    "reason": "决策理由（1-2句话）"
}

可用建筑：granary(粮仓), workshop(工坊), market(市场), library(图书馆), amphitheater(剧场), walls(城墙), temple(神庙), aqueduct(水渠)
可用奇观：pyramid(金字塔), great_wall(万里长城), colosseum(竞技场), hanging_garden(空中花园), lighthouse(灯塔), library_alex(亚历山大图书馆)
外交对象：{other_civs}
```

**Step 2: 文明专属提示**

chinese.txt:
```
你是中华文明的皇帝，名为{leader_name}。
你的性格：{personality}
你的文明崇尚秩序与智慧，擅长农业和科技。
你重视长期规划，倾向于和平发展，但必要时会展现铁腕。
请根据当前状况做出最符合你文明利益的决策。
```

roman.txt:
```
你是罗马帝国的凯撒，名为{leader_name}。
你的性格：{personality}
你的文明崇尚力量与荣耀，擅长军事和工程。
你倾向于扩张领土，建立强大的军团。
```

egyptian.txt:
```
你是埃及法老，名为{leader_name}。
你的性格：{personality}
你的文明崇尚永恒与神秘，擅长建造和文化。
你热衷于建造宏伟的金字塔和神庙。
```

aztec.txt:
```
你是阿兹特克的统治者，名为{leader_name}。
你的性格：{personality}
你的文明崇尚勇武与献祭，擅长战斗和扩张。
你相信通过战斗获得神灵的眷顾。
```

**Step 3: LLM Agent 代码**
```python
"""LLM Agent - 驱动文明领袖决策"""
import json
import random
from openai import AsyncOpenAI
from .config import ARK_API_KEY, ARK_BASE_URL, ARK_MODEL
from .models import Civilization, GameState, ActionType

class LLMAgent:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=ARK_API_KEY,
            base_url=ARK_BASE_URL
        )
        self.prompts = self._load_prompts()

    def _load_prompts(self) -> dict[str, str]:
        """加载提示模板"""
        prompts = {}
        base = Path(__file__).parent / "prompts"
        for f in base.glob("*.txt"):
            prompts[f.stem] = f.read_text(encoding="utf-8")
        return prompts

    def _build_context(self, civ: Civilization, state: GameState) -> str:
        """构建给 LLM 的上下文"""
        # 基础状态
        total_pop = sum(c.population for c in civ.cities)
        total_food = sum(c.get_output().food for c in civ.cities)
        total_prod = sum(c.get_output().production for c in civ.cities)
        total_gold = sum(c.get_output().gold for c in civ.cities)
        total_science = sum(c.get_output().science for c in civ.cities)
        total_culture = sum(c.get_output().culture for c in civ.cities)

        context = f"""当前状态：
- 回合：{state.turn}
- 总人口：{total_pop}
- 每回合产出：粮食{total_food} 产能{total_prod} 金币{total_gold} 科技{total_science} 文化{total_culture}
- 城市数量：{len(civ.cities)}
- 军事力量：{civ.military_power}
- 幸福度：{civ.happiness}%
- 科技等级：{civ.tech_level}

城市详情："""
        for city in civ.cities:
            output = city.get_output()
            context += f"\n- {city.name}: 人口{city.population}, 粮食{output.food}/回合, 产能{output.production}/回合"

        # 外交关系
        if civ.relations:
            context += "\n\n外交关系："
            for other_id, score in civ.relations.items():
                level = "同盟" if score > 60 else "友好" if score > 20 else "中立" if score > -20 else "敌对" if score > -60 else "战争"
                other = next((c for c in state.civilizations if c.id == other_id), None)
                if other:
                    context += f"\n- {other.name}: {level}({score})"

        # 最近事件
        recent_events = [e for e in state.events[-5:] if e.target_civ_id == civ.id or e.target_civ_id is None]
        if recent_events:
            context += "\n\n最近事件："
            for e in recent_events[-3:]:
                context += f"\n- {e.title}: {e.description}"

        # 历史决策
        if civ.history:
            context += "\n\n你最近的决策："
            for h in civ.history[-3:]:
                context += f"\n- {h}"

        return context

    async def get_decision(self, civ: Civilization, state: GameState) -> dict:
        """让 LLM 做出决策"""
        civ_key = civ.name.lower().replace(" ", "_")
        system_prompt = self.prompts.get(civ_key, self.prompts.get("system", ""))
        system_prompt = system_prompt.replace("{leader_name}", civ.leader_name)
        system_prompt = system_prompt.replace("{personality}", civ.personality)

        context = self._build_context(civ, state)

        # 获取可用奇观（未被其他文明建造的）
        built_wonders = set()
        for c in state.civilizations:
            for city in c.cities:
                built_wonders.update(city.wonders)

        try:
            response = await self.client.chat.completions.create(
                model=ARK_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context}
                ],
                temperature=0.7,
                max_tokens=300,
                response_format={"type": "json_object"}
            )

            decision = json.loads(response.choices[0].message.content)
            return decision

        except Exception as e:
            # LLM 失败时的备用决策
            return self._fallback_decision(civ)

    def _fallback_decision(self, civ: Civilization) -> dict:
        """备用随机决策"""
        actions = ["build", "research", "culture"]
        action = random.choice(actions)
        targets = {
            "build": ["granary", "workshop", "library", "market"],
            "research": ["agriculture", "mining", "writing"],
            "culture": ["tradition", "philosophy"]
        }
        return {
            "action": action,
            "target": random.choice(targets.get(action, ["none"])),
            "reason": "基于经验的决策"
        }
```

---

#### Task 5: 游戏引擎核心
**Objective:** 实现回合制模拟引擎

**Files:**
- Create: `civilization/backend/game_engine.py`

**Step 1: 完整游戏引擎**（包含回合处理、资源计算、事件触发）

```python
"""核心游戏引擎"""
import random
import uuid
from .models import *
from .llm_agent import LLMAgent
from .events import EventSystem
from .database import save_state, save_event

class GameEngine:
    def __init__(self):
        self.state = GameState()
        self.agent = LLMAgent()
        self.event_system = EventSystem()
        self.callbacks: list = []  # 事件回调

    def on_event(self, callback):
        """注册事件回调"""
        self.callbacks.append(callback)

    async def _emit(self, event_type: str, data: dict):
        """触发回调"""
        for cb in self.callbacks:
            await cb(event_type, data)

    def init_game(self):
        """初始化新游戏"""
        # 生成地形
        self.state.map_data = self._generate_map()

        # 创建文明
        civs = [
            Civilization(
                id="chinese",
                name="中华",
                leader_name="秦始皇",
                personality="智慧、沉稳、善于长远规划",
                color="#E63946",
                cities=[self._create_starting_city("chinese", "咸阳", 7, 5, TerrainType.GRASSLAND)],
                relations={"roman": 0, "egyptian": 0, "aztec": 0},
                turn_founded=0
            ),
            Civilization(
                id="roman",
                name="罗马",
                leader_name="凯撒",
                personality="勇猛、果断、追求荣耀与扩张",
                color="#457B9D",
                cities=[self._create_starting_city("roman", "罗马", 22, 6, TerrainType.PLAINS)],
                relations={"chinese": 0, "egyptian": 0, "aztec": 0},
                turn_founded=0
            ),
            Civilization(
                id="egyptian",
                name="埃及",
                leader_name="拉美西斯",
                personality="神秘、虔诚、热衷于永恒的建筑",
                color="#F4A261",
                cities=[self._create_starting_city("egyptian", "底比斯", 15, 14, TerrainType.DESERT)],
                relations={"chinese": 0, "roman": 0, "aztec": 0},
                turn_founded=0
            ),
            Civilization(
                id="aztec",
                name="阿兹特克",
                leader_name="蒙特祖马",
                personality="狂野、好战、相信血与火的力量",
                color="#2A9D8F",
                cities=[self._create_starting_city("aztec", "特诺奇", 8, 15, TerrainType.FOREST)],
                relations={"chinese": 0, "roman": 0, "egyptian": 0},
                turn_founded=0
            ),
        ]
        self.state.civilizations = civs
        self.state.turn = 0
        self.state.is_running = True

    def _generate_map(self) -> list[list[TerrainType]]:
        """生成地图"""
        width, height = 30, 20
        terrain_map = []

        for y in range(height):
            row = []
            for x in range(width):
                r = random.random()
                if r < 0.05:
                    terrain = TerrainType.WATER
                elif r < 0.12:
                    terrain = TerrainType.MOUNTAIN
                elif r < 0.25:
                    terrain = TerrainType.HILLS
                elif r < 0.45:
                    terrain = TerrainType.FOREST
                elif r < 0.65:
                    terrain = TerrainType.PLAINS
                elif r < 0.85:
                    terrain = TerrainType.GRASSLAND
                else:
                    terrain = TerrainType.DESERT
                row.append(terrain)
            terrain_map.append(row)
        return terrain_map

    def _create_starting_city(self, civ_id: str, name: str, x: int, y: int, terrain: TerrainType) -> City:
        return City(
            id=f"{civ_id}_city_0",
            name=name,
            x=x, y=y,
            terrain=terrain,
            population=3,
            food_stored=5
        )

    async def process_turn(self):
        """处理一个回合"""
        self.state.turn += 1
        turn = self.state.turn

        await self._emit("turn_start", {"turn": turn})

        for civ in self.state.civilizations:
            if not civ.is_alive:
                continue

            # 1. 计算资源产出
            self._update_resources(civ)

            # 2. 人口增长
            self._update_population(civ)

            # 3. AI 决策
            decision = await self.agent.get_decision(civ, self.state)
            await self._apply_decision(civ, decision)

            # 4. 记录历史
            civ.history.append(f"回合{turn}: {decision.get('reason', '未知决策')}")

        # 5. 触发事件
        event = await self.event_system.try_generate_event(self.state)
        if event:
            self.state.events.append(event)
            await save_event(event)
            await self._emit("event", event.model_dump())

        # 6. 外交关系自然衰减/增长
        self._update_relations()

        # 7. 检查文明存亡
        self._check_civilization_status()

        # 8. 保存状态
        await save_state(self.state)
        await self._emit("turn_end", {"turn": turn, "state": self.state.model_dump()})

    def _update_resources(self, civ: Civilization):
        """更新资源"""
        for city in civ.cities:
            output = city.get_output()
            civ.resources.food += output.food
            civ.resources.production += output.production
            civ.resources.gold += output.gold
            civ.resources.science += output.science
            civ.resources.culture += output.culture

        # 累计总资源
        civ.total_resources.food += civ.resources.food
        civ.total_resources.production += civ.resources.production
        civ.total_resources.gold += civ.resources.gold
        civ.total_resources.science += civ.resources.science
        civ.total_resources.culture += civ.resources.culture

    def _update_population(self, civ: Civilization):
        """更新人口"""
        for city in civ.cities:
            output = city.get_output()
            city.food_stored += output.food - city.population * 2
            if city.food_stored >= city.food_needed:
                city.population += 1
                city.food_stored = 0
                city.food_needed = int(city.food_needed * 1.3)
            elif city.food_stored < 0:
                city.population = max(1, city.population - 1)
                city.food_stored = 0

    async def _apply_decision(self, civ: Civilization, decision: dict):
        """应用 AI 决策"""
        action = decision.get("action", "none")
        target = decision.get("target", "none")

        if action == "build":
            await self._build_action(civ, target)
        elif action == "research":
            civ.resources.science -= 5
            civ.tech_level += 1
        elif action == "diplomacy":
            await self._diplomacy_action(civ, target, decision)
        elif action == "military":
            civ.military_power += 5
            civ.resources.gold -= 3
        elif action == "culture":
            civ.culture_level += 1
            civ.resources.culture -= 5

    async def _build_action(self, civ: Civilization, target: str):
        """建造决策"""
        if not civ.cities:
            return
        city = civ.cities[0]  # 默认主城

        try:
            building = BuildingType(target)
            if building not in city.buildings and civ.resources.production >= 5:
                city.buildings.append(building)
                civ.resources.production -= 5
        except ValueError:
            try:
                wonder = WonderType(target)
                if wonder not in city.wonders and civ.resources.production >= 15:
                    city.wonders.append(wonder)
                    civ.resources.production -= 15
            except ValueError:
                pass

    async def _diplomacy_action(self, civ: Civilization, target: str, decision: dict):
        """外交决策"""
        for other in self.state.civilizations:
            if other.id != civ.id and other.is_alive:
                if target.lower() in other.name.lower():
                    # 根据决策调整关系
                    change = 10 if "友好" in decision.get("reason", "") else -10
                    civ.relations[other.id] = max(-100, min(100, civ.relations.get(other.id, 0) + change))
                    other.relations[civ.id] = max(-100, min(100, other.relations.get(civ.id, 0) + change))
                    break

    def _update_relations(self):
        """更新外交关系（自然衰减）"""
        for civ in self.state.civilizations:
            for other_id in list(civ.relations.keys()):
                current = civ.relations[other_id]
                # 向中立值缓慢衰减
                if current > 0:
                    civ.relations[other_id] = max(0, current - 1)
                elif current < 0:
                    civ.relations[other_id] = min(0, current + 1)

    def _check_civilization_status(self):
        """检查文明状态"""
        for civ in self.state.civilizations:
            if not civ.is_alive:
                continue
            total_pop = sum(c.population for c in civ.cities)
            if total_pop <= 0:
                civ.is_alive = False
```

---

#### Task 6: 事件系统
**Objective:** 实现随机事件和神之干预

**Files:**
- Create: `civilization/backend/events.py`

```python
"""事件系统"""
import random
import uuid
from .models import *

class EventSystem:
    """管理游戏事件"""

    # 基础事件池
    BASE_EVENTS = [
        {
            "type": EventType.DROUGHT,
            "title": "旱灾来袭",
            "description": "严重的旱灾席卷了{civ}的领土，农作物枯萎，粮食减产。",
            "effects": {"food": -5, "happiness": -10}
        },
        {
            "type": EventType.FLOOD,
            "title": "洪水泛滥",
            "description": "暴雨引发洪水，{civ}的{city}遭受损失。",
            "effects": {"production": -3, "population": -1}
        },
        {
            "type": EventType.PLAGUE,
            "title": "瘟疫爆发",
            "description": "一场可怕的瘟疫在{civ}蔓延，人口锐减。",
            "effects": {"population": -2, "happiness": -20}
        },
        {
            "type": EventType.BOUNTIFUL_HARVEST,
            "title": "丰收之年",
            "description": "风调雨顺，{civ}迎来了大丰收！",
            "effects": {"food": 10, "happiness": 10}
        },
        {
            "type": EventType.GOLDEN_AGE,
            "title": "黄金时代",
            "description": "{civ}进入黄金时代，所有产出翻倍！",
            "effects": {"all_multiplier": 2, "happiness": 20}
        },
        {
            "type": EventType.DISCOVERY,
            "title": "重大发现",
            "description": "{civ}的学者有了重大发现，科技水平大幅提升！",
            "effects": {"science": 15}
        },
    ]

    async def try_generate_event(self, state: GameState) -> GameEvent | None:
        """尝试生成事件（每回合 30% 概率）"""
        if random.random() > 0.3:
            return None

        # 选择一个随机文明
        alive_civs = [c for c in state.civilizations if c.is_alive]
        if not alive_civs:
            return None

        target_civ = random.choice(alive_civs)
        template = random.choice(self.BASE_EVENTS)

        # 替换模板变量
        city_name = target_civ.cities[0].name if target_civ.cities else "首都"
        description = template["description"].format(
            civ=target_civ.name, city=city_name
        )

        return GameEvent(
            id=str(uuid.uuid4())[:8],
            turn=state.turn,
            event_type=template["type"],
            title=template["title"],
            description=description,
            target_civ_id=target_civ.id,
            effects=template["effects"]
        )

    def apply_event_effects(self, event: GameEvent, civ: Civilization):
        """应用事件效果"""
        effects = event.effects

        if "food" in effects:
            civ.resources.food += effects["food"]
        if "production" in effects:
            civ.resources.production += effects["production"]
        if "gold" in effects:
            civ.resources.gold += effects["gold"]
        if "science" in effects:
            civ.resources.science += effects["science"]
        if "culture" in effects:
            civ.resources.culture += effects["culture"]
        if "happiness" in effects:
            civ.happiness = max(0, min(100, civ.happiness + effects["happiness"]))
        if "population" in effects and civ.cities:
            civ.cities[0].population = max(1, civ.cities[0].population + effects["population"])
```

---

#### Task 7: FastAPI 主入口
**Objective:** 创建 API 路由和 WebSocket

**Files:**
- Create: `civilization/backend/main.py`
- Create: `civilization/backend/__init__.py`

**Step 1: main.py**
```python
"""文明纪元 - FastAPI 主入口"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from .database import init_db, save_state, load_state
from .game_engine import GameEngine
from .models import GameState, DivineAction, GameEvent, EventType

# 全局游戏引擎实例
engine = GameEngine()
connected_clients: list[WebSocket] = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    await init_db()
    # 尝试加载已有存档
    saved = await load_state()
    if saved:
        engine.state = saved
    yield

app = FastAPI(title="文明纪元", lifespan=lifespan)

# 静态文件
frontend_dir = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

@app.get("/")
async def root():
    return FileResponse(str(frontend_dir / "index.html"))

@app.get("/api/state")
async def get_state():
    """获取当前游戏状态"""
    return engine.state.model_dump()

@app.post("/api/game/start")
async def start_game():
    """开始新游戏"""
    engine.init_game()
    await save_state(engine.state)
    await broadcast("game_started", engine.state.model_dump())
    return {"status": "ok", "message": "新游戏已开始"}

@app.post("/api/game/next-turn")
async def next_turn():
    """推进到下一回合"""
    await engine.process_turn()
    return {"status": "ok", "turn": engine.state.turn}

@app.post("/api/game/auto")
async def auto_play():
    """自动播放（后台任务）"""
    async def run():
        engine.state.is_running = True
        while engine.state.is_running and engine.state.turn < 200:
            await engine.process_turn()
            await asyncio.sleep(2)  # 每 2 秒一回合
            await broadcast("game_state", engine.state.model_dump())

    asyncio.create_task(run())
    return {"status": "ok", "message": "自动播放已开始"}

@app.post("/api/game/stop")
async def stop_auto():
    """停止自动播放"""
    engine.state.is_running = False
    return {"status": "ok"}

@app.post("/api/divine/action")
async def divine_action(action: DivineAction):
    """神之干预"""
    target = next((c for c in engine.state.civilizations if c.id == action.target_civ_id), None)
    if not target:
        return {"status": "error", "message": "目标文明不存在"}

    event = GameEvent(
        id=str(uuid.uuid4())[:8],
        turn=engine.state.turn,
        event_type=action.action_type,
        title=f"神之干预: {action.action_type.value}",
        description=action.description,
        target_civ_id=target.id,
        effects={"happiness": 20 if action.action_type == EventType.DIVINE_BLESSING else -20}
    )

    engine.state.events.append(event)
    await broadcast("divine_event", event.model_dump())
    return {"status": "ok", "event": event.model_dump()}

@app.get("/api/civilizations")
async def get_civilizations():
    """获取所有文明信息"""
    return [c.model_dump() for c in engine.state.civilizations]

@app.get("/api/civilizations/{civ_id}")
async def get_civilization(civ_id: str):
    """获取单个文明详情"""
    civ = next((c for c in engine.state.civilizations if c.id == civ_id), None)
    if not civ:
        return {"status": "error", "message": "文明不存在"}
    return civ.model_dump()

# WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

async def broadcast(event_type: str, data: dict):
    """广播消息给所有客户端"""
    message = {"type": event_type, "data": data}
    for client in connected_clients[:]:
        try:
            await client.send_json(message)
        except:
            connected_clients.remove(client)
```

**Step 2: __init__.py**
```python
"""Backend package"""
```

---

### Phase 2: 前端界面（精致 UI）

#### Task 8: HTML 主页面
**Objective:** 创建精致的单页应用

**Files:**
- Create: `civilization/frontend/index.html`

**Step 1: 完整 HTML**（包含地图、控制面板、事件日志三栏布局）

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌍 文明纪元</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <div id="app">
        <!-- 顶部状态栏 -->
        <header id="top-bar">
            <div class="logo">🌍 文明纪元</div>
            <div id="turn-display">回合: <span id="turn-num">0</span></div>
            <div id="controls">
                <button id="btn-new-game" onclick="newGame()">新游戏</button>
                <button id="btn-next-turn" onclick="nextTurn()">下一回合</button>
                <button id="btn-auto" onclick="toggleAuto()">▶ 自动播放</button>
            </div>
        </header>

        <!-- 主内容区 -->
        <main>
            <!-- 左侧: 地图 -->
            <section id="map-panel">
                <canvas id="game-map" width="900" height="600"></canvas>
                <div id="map-legend">
                    <span class="legend-item"><span class="color" style="background:#8FBC8F"></span>草原</span>
                    <span class="legend-item"><span class="color" style="background:#DAA520"></span>平原</span>
                    <span class="legend-item"><span class="color" style="background:#228B22"></span>森林</span>
                    <span class="legend-item"><span class="color" style="background:#8B7355"></span>丘陵</span>
                    <span class="legend-item"><span class="color" style="background:#696969"></span>山脉</span>
                    <span class="legend-item"><span class="color" style="background:#87CEEB"></span>水域</span>
                    <span class="legend-item"><span class="color" style="background:#F5DEB3"></span>沙漠</span>
                </div>
            </section>

            <!-- 右侧: 信息面板 -->
            <aside id="info-panel">
                <!-- 文明选择标签 -->
                <div id="civ-tabs"></div>

                <!-- 选中文明详情 -->
                <div id="civ-detail">
                    <h3 id="civ-name">选择一个文明</h3>
                    <div id="civ-stats"></div>
                </div>

                <!-- 神之干预面板 -->
                <div id="god-panel">
                    <h3>⚡ 神之干预</h3>
                    <select id="god-target"></select>
                    <div class="god-actions">
                        <button onclick="divineAction('blessing')">🌟 祝福</button>
                        <button onclick="divineAction('wrath')">⚡ 灾难</button>
                        <button onclick="divineAction('oracle')">📜 神谕</button>
                    </div>
                </div>

                <!-- 事件日志 -->
                <div id="event-log">
                    <h3>📜 历史事件</h3>
                    <div id="events-list"></div>
                </div>
            </aside>
        </main>
    </div>

    <script src="/static/js/websocket.js"></script>
    <script src="/static/js/map.js"></script>
    <script src="/static/js/panels.js"></script>
    <script src="/static/js/app.js"></script>
</body>
</html>
```

---

#### Task 9: CSS 样式
**Objective:** 创建精美的暗色主题样式

**Files:**
- Create: `civilization/frontend/css/style.css`

（完整 CSS，包含暗色主题、动画、响应式布局，约 300 行）

---

#### Task 10: JavaScript - 地图渲染
**Objective:** Canvas 渲染六角格/方格地图

**Files:**
- Create: `civilization/frontend/js/map.js`

---

#### Task 11: JavaScript - WebSocket 通信
**Objective:** 实时通信和状态同步

**Files:**
- Create: `civilization/frontend/js/websocket.js`

---

#### Task 12: JavaScript - UI 面板
**Objective:** 文明信息、神之干预、事件日志面板

**Files:**
- Create: `civilization/frontend/js/panels.js`

---

#### Task 13: JavaScript - 主应用逻辑
**Objective:** 整合所有组件

**Files:**
- Create: `civilization/frontend/js/app.js`

---

### Phase 3: 打磨

#### Task 14: 集成测试
**Objective:** 启动并验证完整流程

```bash
cd civilization
export ARK_API_KEY="your_key_here"
python run.py
# 浏览器打开 http://localhost:8000
# 点击"新游戏" → 点击"自动播放" → 观察 AI 文明演化
```

#### Task 15: 优化与美化
- 添加建筑/奇观图标
- 事件动画效果
- 响应式适配移动端
- 存档/读档功能

---

## 🎯 交付清单

- [ ] 4 个 AI 文明各自由 LLM 驱动
- [ ] 回合制模拟，可手动/自动推进
- [ ] 精致 Web UI（暗色主题，Canvas 地图）
- [ ] 神之干预系统（祝福/灾难/神谕）
- [ ] 实时 WebSocket 推送
- [ ] SQLite 存档
- [ ] 事件系统（自然事件 + 神之干预）

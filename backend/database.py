"""Database persistence layer using aiosqlite."""

import json
import aiosqlite
from typing import Optional
from backend.models import GameState, Civilization, City, Resources, GameEvent
from backend.config import MAP_WIDTH, MAP_HEIGHT

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "game_state.db")


def _serialize_terrain_map(map_grid):
    """Serialize terrain grid to JSON."""
    return json.dumps([[t.value if hasattr(t, 'value') else t for t in row] for row in map_grid])


def _deserialize_terrain_map(data):
    """Deserialize terrain grid from JSON."""
    from backend.models import TerrainType
    data = json.loads(data)
    return [[TerrainType(cell) for cell in row] for row in data]


async def _row_to_game_state(row) -> GameState:
    """Convert a database row to a GameState object."""
    from backend.models import TerrainType
    data = json.loads(row[1])

    # Reconstruct civilizations
    civs = []
    for c_data in data.get("civilizations", []):
        cities = []
        for city_data in c_data.get("cities", []):
            from backend.models import BuildingType, WonderType
            city = City(
                name=city_data["name"],
                x=city_data["x"],
                y=city_data["y"],
                population=city_data.get("population", 1),
                buildings=[BuildingType(b) for b in city_data.get("buildings", [])],
                wonders=[WonderType(w) for w in city_data.get("wonders", [])],
                terrain=TerrainType(city_data.get("terrain", "plains")),
                defense=city_data.get("defense", 0),
                food_stored=city_data.get("food_stored", 0),
                food_needed=city_data.get("food_needed", 20),
                production_stored=city_data.get("production_stored", 0),
                science_stored=city_data.get("science_stored", 0),
                building_queue=city_data.get("building_queue", []),
            )
            cities.append(city)

        from backend.models import Resources
        res_data = c_data.get("resources", {})
        resources = Resources(
            food=res_data.get("food", 0),
            production=res_data.get("production", 0),
            gold=res_data.get("gold", 0),
            science=res_data.get("science", 0),
            culture=res_data.get("culture", 0),
        )

        civ = Civilization(
            id=c_data["id"],
            name=c_data["name"],
            leader_name=c_data["leader_name"],
            personality=c_data["personality"],
            color=c_data.get("color", "#ffffff"),
            cities=cities,
            resources=resources,
            tech_level=c_data.get("tech_level", 1),
            military=c_data.get("military", 5),
            culture=c_data.get("culture", 5),
            happiness=c_data.get("happiness", 5),
            relations=c_data.get("relations", {}),
            history=c_data.get("history", []),
            is_alive=c_data.get("is_alive", True),
        )
        civs.append(civ)

    # Reconstruct events
    events = []
    for e_data in data.get("events", []):
        from backend.models import EventType
        event = GameEvent(
            id=e_data["id"],
            turn=e_data["turn"],
            type=EventType(e_data["type"]),
            title=e_data["title"],
            description=e_data["description"],
            effects=e_data.get("effects"),
            target_civ_id=e_data.get("target_civ_id"),
            source=e_data.get("source", "natural"),
        )
        events.append(event)

    return GameState(
        turn=data.get("turn", 0),
        civilizations=civs,
        events=events,
        map_grid=_deserialize_terrain_map(row[2]) if row[2] else [],
        current_event_id=data.get("current_event_id", 0),
        is_running=data.get("is_running", False),
    )


async def init_db():
    """Initialize the SQLite database and create tables."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS game_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                state TEXT NOT NULL,
                map_grid TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                turn INTEGER,
                event_type TEXT,
                title TEXT,
                description TEXT,
                effects TEXT,
                target_civ_id TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def save_state(state: GameState):
    """Save the current game state to the database."""
    data = state.model_dump()
    # Remove map_grid from JSON, store separately
    map_grid_json = _serialize_terrain_map(state.map_grid)
    state_dict = data.copy()
    state_dict.pop("map_grid", None)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO game_state (id, state, map_grid) VALUES (1, ?, ?)",
            (json.dumps(state_dict), map_grid_json),
        )
        await db.commit()


async def load_state() -> Optional[GameState]:
    """Load the saved game state from the database."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT id, state, map_grid FROM game_state WHERE id = 1")
        row = await cursor.fetchone()
        if row is None:
            return None
        return await _row_to_game_state(row)


async def save_event(event: GameEvent):
    """Save a game event to the database."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO events (id, turn, event_type, title, description, effects, target_civ_id, source) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                event.id,
                event.turn,
                event.type.value,
                event.title,
                event.description,
                json.dumps(event.effects) if event.effects else None,
                event.target_civ_id,
                event.source,
            ),
        )
        await db.commit()

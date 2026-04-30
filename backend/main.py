"""FastAPI application for the civilization simulation game."""

import asyncio
import json
import logging
import uuid
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.models import GameState, Civilization, GameEvent
from backend.database import init_db, save_state, load_state, save_event
from backend.game_engine import init_game, process_turn
from backend.llm_agent import get_llm_decision
from backend.events import create_divine_event

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
game_state: Optional[GameState] = None
auto_play_task: Optional[asyncio.Task] = None
auto_play_stop_event: asyncio.Event = asyncio.Event()
websocket_clients: List[WebSocket] = []


# --- WebSocket broadcast helpers ---

async def broadcast_message(msg_type: str, data: dict):
    """Send a message to all connected WebSocket clients."""
    message = json.dumps({"type": msg_type, "data": data}, ensure_ascii=False, default=str)
    dead_clients = []
    for ws in websocket_clients:
        try:
            await ws.send_text(message)
        except Exception:
            dead_clients.append(ws)
    for ws in dead_clients:
        websocket_clients.remove(ws)


async def event_callback(event_type: str, event: GameEvent):
    """Callback for game engine events - broadcasts to WebSocket."""
    await broadcast_message("event", event.model_dump())


# --- Pydantic request models ---

class DivineActionRequest(BaseModel):
    action_type: str  # "blessing", "wrath", "oracle"
    target_civ_id: str
    description: str = ""


# --- Lifespan ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and load saved state on startup."""
    global game_state
    await init_db()
    loaded = await load_state()
    if loaded:
        game_state = loaded
        logger.info(f"Loaded saved game state (turn {game_state.turn})")
    else:
        logger.info("No saved game state found. Use /api/game/start to begin.")
    yield
    # Shutdown: save state if exists
    if game_state:
        await save_state(game_state)
        logger.info("Game state saved on shutdown.")


app = FastAPI(title="Civilization Simulation", lifespan=lifespan)


# --- Static files ---

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "frontend")), name="static")


# --- Routes ---

@app.get("/")
async def serve_index():
    """Serve the frontend index.html."""
    try:
        return FileResponse(os.path.join(BASE_DIR, "frontend", "index.html"))
    except FileNotFoundError:
        return {"message": "Frontend not built yet. See /api/ for API endpoints."}


@app.get("/api/state")
async def get_state():
    """Get the full current game state."""
    global game_state
    if game_state is None:
        raise HTTPException(status_code=404, detail="No game in progress. Start a game with /api/game/start")
    return game_state


@app.post("/api/game/start")
async def start_game():
    """Initialize a new game."""
    global game_state
    game_state = init_game()
    game_state.is_running = True
    await save_state(game_state)
    await broadcast_message("state", game_state.model_dump())
    return {"message": "Game started!", "turn": game_state.turn}


@app.post("/api/game/next-turn")
async def next_turn():
    """Process a single turn."""
    global game_state
    if game_state is None:
        raise HTTPException(status_code=404, detail="No game in progress.")

    game_state = process_turn(game_state, event_callback=event_callback)
    game_state.is_running = True
    await save_state(game_state)
    await broadcast_message("state", game_state.model_dump())
    return {"message": "Turn processed", "turn": game_state.turn}


@app.post("/api/game/auto")
async def auto_play():
    """Start auto-play loop in background task."""
    global auto_play_task, auto_play_stop_event
    if auto_play_task and not auto_play_task.done():
        raise HTTPException(status_code=400, detail="Auto-play already running.")

    auto_play_stop_event.clear()

    from backend.config import MAX_TURNS_AUTO, TURN_DELAY_SECONDS

    async def auto_play_loop():
        global game_state
        try:
            for turn_num in range(MAX_TURNS_AUTO):
                if auto_play_stop_event.is_set():
                    logger.info("Auto-play stopped.")
                    break

                if game_state is None:
                    break

                # Process the turn
                game_state = process_turn(game_state, event_callback=event_callback)
                game_state.is_running = True
                await save_state(game_state)
                await broadcast_message("state", game_state.model_dump())

                # Check if all civs are dead
                alive_civs = [c for c in game_state.civilizations if c.is_alive]
                if len(alive_civs) <= 1:
                    winner = alive_civs[0].name if alive_civs else "None"
                    await broadcast_message("game_over", {"winner": winner})
                    logger.info(f"Game over! Winner: {winner}")
                    break

                await asyncio.sleep(TURN_DELAY_SECONDS)

        except Exception as e:
            logger.error(f"Auto-play error: {e}")
        finally:
            auto_play_task = None

    auto_play_task = asyncio.create_task(auto_play_loop())
    return {"message": "Auto-play started."}


@app.post("/api/game/stop")
async def stop_auto_play():
    """Stop the auto-play loop."""
    global auto_play_stop_event
    auto_play_stop_event.set()
    return {"message": "Auto-play stopping after current turn."}


@app.post("/api/divine/action")
async def divine_action(request: DivineActionRequest):
    """Trigger a divine event (blessing, wrath, oracle) on a civilization."""
    global game_state
    if game_state is None:
        raise HTTPException(status_code=404, detail="No game in progress.")

    # Validate action type
    valid_actions = ["blessing", "wrath", "oracle"]
    if request.action_type not in valid_actions:
        raise HTTPException(status_code=400, detail=f"Invalid action_type. Must be one of: {valid_actions}")

    # Validate target civilization
    target_civ = next((c for c in game_state.civilizations if c.id == request.target_civ_id), None)
    if target_civ is None:
        raise HTTPException(status_code=404, detail=f"Civilization '{request.target_civ_id}' not found.")
    if not target_civ.is_alive:
        raise HTTPException(status_code=400, detail=f"{target_civ.name} has fallen and cannot be targeted.")

    event = create_divine_event(game_state, game_state.turn, request.action_type,
                                 request.target_civ_id, request.description)
    if event is None:
        raise HTTPException(status_code=400, detail="Failed to create divine event.")

    game_state.events.append(event)
    game_state.current_event_id += 1
    await save_event(event)
    await save_state(game_state)
    await broadcast_message("event", event.model_dump())
    await broadcast_message("state", game_state.model_dump())

    return event


@app.get("/api/civilizations")
async def list_civilizations():
    """List all civilizations with basic info."""
    global game_state
    if game_state is None:
        raise HTTPException(status_code=404, detail="No game in progress.")
    civs = []
    for civ in game_state.civilizations:
        civs.append({
            "id": civ.id,
            "name": civ.name,
            "leader_name": civ.leader_name,
            "color": civ.color,
            "is_alive": civ.is_alive,
            "city_count": len(civ.cities),
            "total_population": sum(c.population for c in civ.cities),
            "tech_level": civ.tech_level,
            "military": civ.military,
            "happiness": civ.happiness,
        })
    return civs


@app.get("/api/civilizations/{civ_id}")
async def get_civilization(civ_id: str):
    """Get detailed info about a specific civilization."""
    global game_state
    if game_state is None:
        raise HTTPException(status_code=404, detail="No game in progress.")
    civ = next((c for c in game_state.civilizations if c.id == civ_id), None)
    if civ is None:
        raise HTTPException(status_code=404, detail=f"Civilization '{civ_id}' not found.")
    return civ


# --- WebSocket ---

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time game updates."""
    await websocket.accept()
    websocket_clients.append(websocket)
    logger.info(f"WebSocket client connected. Total: {len(websocket_clients)}")

    try:
        # Send current state immediately
        if game_state:
            await websocket.send_text(
                json.dumps({"type": "state", "data": game_state.model_dump()}, ensure_ascii=False, default=str)
            )

        # Keep connection open and handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                # Client can send ping to keep connection alive
                if data == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except WebSocketDisconnect:
                break
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if websocket in websocket_clients:
            websocket_clients.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total: {len(websocket_clients)}")

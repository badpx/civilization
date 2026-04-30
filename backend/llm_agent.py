"""LLM Agent interface using OpenRouter API for AI civilization decisions."""

import json
import random
import logging
from typing import Optional, Dict, Any
from openai import AsyncOpenAI
from backend.models import GameState, Civilization, ActionType
from backend.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL

logger = logging.getLogger(__name__)

# Prompt file paths
PROMPT_DIR = "/root/civilization/backend/prompts"

# Fallback actions if API fails
FALLBACK_ACTIONS = [
    ActionType.build,
    ActionType.research,
    ActionType.culture,
    ActionType.military,
]


def _load_prompt(filename: str) -> str:
    """Load a prompt template from the prompts directory."""
    try:
        with open(f"{PROMPT_DIR}/{filename}", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.warning(f"Prompt file {filename} not found, using default.")
        return ""


async def get_llm_decision(civ: Civilization, state: GameState) -> Dict[str, Any]:
    """Get a decision from the LLM agent for a civilization.

    Returns a dict with {action, target, reason}.
    Falls back to random decision on API failure.
    """
    if not OPENROUTER_API_KEY:
        logger.warning("OPENROUTER_API_KEY not set; using fallback random decision.")
        return _fallback_decision(civ)

    try:
        # Load system prompt
        system_prompt = _load_prompt("system.txt")

        # Load personality-specific prompt
        personality_prompt = _load_prompt(f"{civ.personality}.txt")

        # Build the context with current state
        context = _build_context(civ, state)

        # Combine prompts
        full_system = f"{system_prompt}\n\n{personality_prompt}" if personality_prompt else system_prompt

        client = AsyncOpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY,
        )

        response = await client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[
                {"role": "system", "content": full_system},
                {"role": "user", "content": context},
            ],
            temperature=0.7,
            max_tokens=300,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content.strip()
        # Try to parse JSON from the response
        # Find JSON block if wrapped in markdown
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()

        decision = json.loads(content)

        # Validate the action field
        action = decision.get("action", "").lower()
        valid_actions = [a.value for a in ActionType]
        if action not in valid_actions:
            # Map Chinese action names
            action_map = {
                "建造": "build", "建设": "build", "建筑": "build",
                "研究": "research", "科技": "research",
                "外交": "diplomacy", "贸易": "diplomacy",
                "军事": "military", "战争": "military", "训练": "military",
                "文化": "culture", "艺术": "culture",
            }
            action = action_map.get(action, random.choice(valid_actions))

        # Validate target
        target = decision.get("target", "")
        reason = decision.get("reason", "")

        return {
            "action": action,
            "target": target,
            "reason": reason,
        }

    except Exception as e:
        logger.error(f"LLM API call failed for {civ.name}: {e}")
        return _fallback_decision(civ)


def _fallback_decision(civ: Civilization) -> Dict[str, Any]:
    """Generate a random fallback decision when the API is unavailable."""
    action = random.choice(FALLBACK_ACTIONS).value
    targets = {
        "build": "infrastructure",
        "research": "technology",
        "culture": "arts",
        "military": "army",
    }
    target = targets.get(action, "development")
    reasons = {
        "build": "We must strengthen our infrastructure.",
        "research": "Knowledge is power.",
        "culture": "Our people need inspiration.",
        "military": "We must defend our borders.",
        "diplomacy": "We should seek allies.",
    }
    return {
        "action": action,
        "target": target,
        "reason": reasons.get(action, "For the glory of our civilization."),
    }


def _build_context(civ: Civilization, state: GameState) -> str:
    """Build a detailed context string describing the civilization's state."""
    total_pop = sum(c.population for c in civ.cities)
    city_info = []
    for city in civ.cities:
        output = city.get_output()
        buildings_str = ", ".join(b.value for b in city.buildings) or "none"
        city_info.append(
            f"  - {city.name} (Pop: {city.population}, Terrain: {city.terrain.value})\n"
            f"    Output: F:{output.food} P:{output.production} G:{output.gold} S:{output.science} C:{output.culture}\n"
            f"    Buildings: [{buildings_str}] Defense: {city.defense}"
        )

    # Relations info
    relations_info = []
    for other_id, value in civ.relations.items():
        other_civ = next((c for c in state.civilizations if c.id == other_id), None)
        if other_civ:
            relations_info.append(f"  - {other_civ.name}: {value}")

    # Recent events
    recent_events = [e for e in state.events if e.turn >= state.turn - 5][-5:]
    events_info = []
    for e in recent_events:
        if e.target_civ_id == civ.id:
            events_info.append(f"  - {e.title}: {e.description}")
    if not events_info:
        events_info.append("  - Nothing notable recently.")

    context = f"""
=== CIVILIZATION STATUS ===
Civilization: {civ.name}
Leader: {civ.leader_name}
Turn: {state.turn}
Population: {total_pop}
Technology Level: {civ.tech_level}
Military Strength: {civ.military}
Culture: {civ.culture}
Happiness: {civ.happiness}
Status: {"Alive" if civ.is_alive else "Fallen"}

=== RESOURCES ===
Food: {civ.resources.food}
Production: {civ.resources.production}
Gold: {civ.resources.gold}
Science: {civ.resources.science}
Culture: {civ.resources.culture}

=== CITIES ===
{chr(10).join(city_info)}

=== DIPLOMACY ===
{chr(10).join(relations_info) if relations_info else "  - No diplomatic relations yet."}

=== RECENT EVENTS AFFECTING US ===
{chr(10).join(events_info)}

=== INSTRUCTIONS ===
You are the leader of {civ.name}. Based on the current situation, decide what action to take this turn.
Choose ONE action from: build, research, diplomacy, military, culture
Respond with a JSON object: {{"action": "...", "target": "...", "reason": "..."}}
"""
    return context

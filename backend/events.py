"""Event system for natural and divine events."""

import random
import uuid
from typing import Dict, Optional, List, Callable
from backend.models import (
    GameState,
    Civilization,
    GameEvent,
    EventType,
    Resources,
)


# Event definitions: (EventType, title_template, description_template, effects_modifier)
NATURAL_EVENT_POOL = [
    (EventType.drought, "{civ_name} suffers a drought",
     "A terrible drought has struck {civ_name}, drying up crops across the land.",
     {"food": -5, "happiness": -2}),
    (EventType.flood, "{civ_name} experiences flooding",
     "Heavy rains have caused rivers to overflow, flooding {civ_name}'s lands.",
     {"food": -3, "production": -3, "happiness": -1}),
    (EventType.plague, "{civ_name} is hit by plague",
     "A deadly plague spreads through {civ_name}, reducing population and morale.",
     {"population": -1, "happiness": -4}),
    (EventType.earthquake, "{civ_name} experiences an earthquake",
     "The ground shakes violently in {civ_name}, damaging infrastructure.",
     {"production": -4, "gold": -2}),
    (EventType.bountiful_harvest, "{civ_name} enjoys a bountiful harvest",
     "The gods smile upon {civ_name} with an unusually abundant harvest.",
     {"food": +6, "happiness": +2}),
    (EventType.golden_age, "{civ_name} enters a golden age",
     "A period of prosperity and cultural flourishing begins in {civ_name}.",
     {"food": +3, "production": +3, "culture": +3, "happiness": +3}),
    (EventType.discovery, "{civ_name} makes a scientific discovery",
     "Scholars in {civ_name} have made a breakthrough discovery.",
     {"science": +5, "culture": +2}),
]

DIVINE_EVENT_POOL = {
    "blessing": (EventType.divine_blessing, "Divine Blessing upon {civ_name}",
                 "The divine power blesses {civ_name}, granting prosperity.",
                 {"food": +8, "production": +8, "gold": +8, "happiness": +5}),
    "wrath": (EventType.divine_wrath, "Divine Wrath upon {civ_name}",
              "The divine power smites {civ_name} with fury.",
              {"food": -8, "production": -8, "gold": -8, "happiness": -5, "population": -2}),
    "oracle": (EventType.divine_oracle, "Divine Oracle visited {civ_name}",
               "A divine oracle appears in {civ_name}, granting advanced knowledge.",
               {"science": +10, "culture": +10, "tech_level": +1}),
}


def check_natural_event(state: GameState, turn: int) -> Optional[List[GameEvent]]:
    """Check if a natural event triggers this turn (30% chance). Return list of triggered events."""
    from backend.config import EVENT_TRIGGER_CHANCE

    if random.random() >= EVENT_TRIGGER_CHANCE:
        return None

    triggered_events = []
    for civ in state.civilizations:
        if not civ.is_alive:
            continue

        event_type, title_tmpl, desc_tmpl, effects = random.choice(NATURAL_EVENT_POOL)
        civ_name = civ.name
        title = title_tmpl.format(civ_name=civ_name)
        description = desc_tmpl.format(civ_name=civ_name)

        event_id = f"evt_{turn}_{civ.id}_{uuid.uuid4().hex[:6]}"
        event = GameEvent(
            id=event_id,
            turn=turn,
            type=event_type,
            title=title,
            description=description,
            effects=effects.copy(),
            target_civ_id=civ.id,
            source="natural",
        )
        apply_event_effects(civ, effects, state)
        triggered_events.append(event)

    return triggered_events if triggered_events else None


def create_divine_event(state: GameState, turn: int, action_type: str,
                        target_civ_id: str, description: str) -> Optional[GameEvent]:
    """Create a divine event triggered by the player."""
    if action_type not in DIVINE_EVENT_POOL:
        return None

    civ = next((c for c in state.civilizations if c.id == target_civ_id and c.is_alive), None)
    if not civ:
        return None

    event_type, title_tmpl, desc_tmpl, effects = DIVINE_EVENT_POOL[action_type]
    civ_name = civ.name
    title = title_tmpl.format(civ_name=civ_name)
    event_description = description if description else desc_tmpl.format(civ_name=civ_name)

    event_id = f"evt_{turn}_divine_{uuid.uuid4().hex[:6]}"
    event = GameEvent(
        id=event_id,
        turn=turn,
        type=event_type,
        title=title,
        description=event_description,
        effects=effects.copy(),
        target_civ_id=target_civ_id,
        source="divine",
    )
    apply_event_effects(civ, effects, state)
    return event


def apply_event_effects(civ: Civilization, effects: Dict[str, int], state: GameState):
    """Apply event effects to a civilization."""
    for key, value in effects.items():
        if key == "food":
            civ.resources.food = max(0, civ.resources.food + value)
        elif key == "production":
            civ.resources.production = max(0, civ.resources.production + value)
        elif key == "gold":
            civ.resources.gold = max(0, civ.resources.gold + value)
        elif key == "science":
            civ.resources.science = max(0, civ.resources.science + value)
        elif key == "culture":
            civ.resources.culture = max(0, civ.resources.culture + value)
            civ.culture = max(0, civ.culture + value)
        elif key == "happiness":
            civ.happiness = max(0, min(100, civ.happiness + value))
        elif key == "population":
            # Apply population change to the first (capital) city
            if civ.cities:
                civ.cities[0].population = max(1, civ.cities[0].population + value)
        elif key == "tech_level":
            civ.tech_level = max(1, civ.tech_level + value)

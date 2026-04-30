"""Core game engine: map generation, turn processing, AI logic."""

import random
import uuid
from typing import List, Optional, Callable
from backend.models import (
    GameState, Civilization, City, Resources, TerrainType,
    BuildingType, GameEvent, EventType,
)
from backend.config import (
    MAP_WIDTH, MAP_HEIGHT, STARTING_POPULATION,
    POPULATION_GROWTH_THRESHOLD, STARTING_FOOD, STARTING_PRODUCTION,
    STARTING_GOLD, STARTING_SCIENCE, STARTING_CULTURE,
    RELATIONS_DECAY_RATE, BUILDING_COSTS,
)
from backend.events import check_natural_event


# Civilization definitions
CIV_DEFINITIONS = [
    {
        "id": "chinese",
        "name": "中华文明",
        "leader_name": "秦始皇",
        "personality": "chinese",
        "color": "#FF0000",
        "start_x": 3,
        "start_y": 5,
    },
    {
        "id": "roman",
        "name": "罗马帝国",
        "leader_name": "恺撒",
        "personality": "roman",
        "color": "#0000FF",
        "start_x": 20,
        "start_y": 4,
    },
    {
        "id": "egyptian",
        "name": "埃及文明",
        "leader_name": "拉美西斯二世",
        "personality": "egyptian",
        "color": "#FFD700",
        "start_x": 10,
        "start_y": 12,
    },
    {
        "id": "aztec",
        "name": "阿兹特克文明",
        "leader_name": "蒙特祖玛",
        "personality": "aztec",
        "color": "#00AA00",
        "start_x": 25,
        "start_y": 16,
    },
]

# Terrain generation weights
TERRAIN_WEIGHTS = {
    TerrainType.plains: 0.25,
    TerrainType.forest: 0.20,
    TerrainType.hills: 0.15,
    TerrainType.mountain: 0.10,
    TerrainType.water: 0.10,
    TerrainType.desert: 0.10,
    TerrainType.grassland: 0.10,
}


def _generate_terrain_map() -> List[List[TerrainType]]:
    """Generate a 30x20 grid of terrain types using weighted random distribution."""
    grid = []
    terrain_types = list(TERRAIN_WEIGHTS.keys())
    weights = list(TERRAIN_WEIGHTS.values())

    for y in range(MAP_HEIGHT):
        row = []
        for x in range(MAP_WIDTH):
            terrain = random.choices(terrain_types, weights=weights, k=1)[0]
            row.append(terrain)
        grid.append(row)

    # Ensure starting positions are passable (not water or mountain)
    for civ_def in CIV_DEFINITIONS:
        x, y = civ_def["start_x"], civ_def["start_y"]
        if grid[y][x] in (TerrainType.water, TerrainType.mountain):
            grid[y][x] = TerrainType.plains

    return grid


def _get_surrounding_terrain(grid, x, y, radius=2):
    """Get terrain types in a radius around a position, for city naming flavor."""
    terrains = []
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            nx, ny = x + dx, y + dy
            if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                terrains.append(grid[ny][nx])
    return terrains


def _generate_city_name(civ_id: str, index: int) -> str:
    """Generate a city name based on civilization."""
    names = {
        "chinese": ["长安", "洛阳", "建康", "成都", "临安", "北平", "南京", "西安", "开封", "广州"],
        "roman": ["Roma", "Pompeii", "Florentia", "Mediolanum", "Neapolis", "Ravenna", "Genua", "Patavium", "Brundisium", "Aquileia"],
        "egyptian": ["Thebes", "Memphis", "Alexandria", "Giza", "Luxor", "Aswan", "Abydos", "Karnak", "Edfu", "Philae"],
        "aztec": ["Tenochtitlan", "Texcoco", "Tlacopan", "Chapultepec", "Tlatelolco", "Xochimilco", "Coyoacan", "Azcapotzalco", "Iztapalapa", "Teotihuacan"],
    }
    names_list = names.get(civ_id, ["City"])
    if index < len(names_list):
        return names_list[index]
    return f"{names_list[0]} {index + 1}"


def init_game() -> GameState:
    """Initialize a new game with map, civilizations, and starting state."""
    state = GameState(
        turn=0,
        civilizations=[],
        events=[],
        map_grid=[[]],
        current_event_id=0,
        is_running=False,
    )

    # Generate terrain map
    state.map_grid = _generate_terrain_map()

    # Create civilizations
    for idx, civ_def in enumerate(CIV_DEFINITIONS):
        x, y = civ_def["start_x"], civ_def["start_y"]
        terrain = state.map_grid[y][x]

        capital = City(
            name=_generate_city_name(civ_def["id"], 0),
            x=x,
            y=y,
            population=STARTING_POPULATION,
            buildings=[BuildingType.granary],
            wonders=[],
            terrain=terrain,
            defense=0,
            food_stored=0,
            food_needed=POPULATION_GROWTH_THRESHOLD,
        )

        # Set relations with all other civs
        relations = {}
        for other in CIV_DEFINITIONS:
            if other["id"] != civ_def["id"]:
                relations[other["id"]] = 0

        civ = Civilization(
            id=civ_def["id"],
            name=civ_def["name"],
            leader_name=civ_def["leader_name"],
            personality=civ_def["personality"],
            color=civ_def["color"],
            cities=[capital],
            resources=Resources(
                food=STARTING_FOOD,
                production=STARTING_PRODUCTION,
                gold=STARTING_GOLD,
                science=STARTING_SCIENCE,
                culture=STARTING_CULTURE,
            ),
            tech_level=1,
            military=5,
            culture=5,
            happiness=5,
            relations=relations,
            history=[f"Turn 0: {civ_def['name']} founded by {civ_def['leader_name']}."],
            is_alive=True,
        )
        state.civilizations.append(civ)

    return state


def process_turn(state: GameState, event_callback: Optional[Callable] = None) -> GameState:
    """Process a single game turn: update resources, population, events, relations."""
    state.turn += 1

    # Update resources for each civilization
    _update_resources(state)

    # Update population
    _update_population(state)

    # Check for natural events
    new_events = check_natural_event(state, state.turn)
    if new_events:
        for event in new_events:
            state.events.append(event)
            if event_callback:
                event_callback("event", event)

    # Decay relations
    _update_relations(state)

    # Check civ status
    _check_civilization_status(state)

    # Add history entry
    for civ in state.civilizations:
        if civ.is_alive:
            total = civ.total_output()
            civ.history.append(
                f"Turn {state.turn}: Food={civ.resources.food}, Prod={civ.resources.production}, "
                f"Gold={civ.resources.gold}, Science={civ.resources.science}, "
                f"Pop={sum(c.population for c in civ.cities)}"
            )

    return state


def _update_resources(state: GameState):
    """Update resources for each civilization based on city outputs, minus maintenance."""
    for civ in state.civilizations:
        if not civ.is_alive:
            continue

        total_output = civ.total_output()

        # Add city output to stored resources
        civ.resources.food += total_output.food
        civ.resources.production += total_output.production
        civ.resources.gold += total_output.gold
        civ.resources.science += total_output.science
        civ.resources.culture += total_output.culture

        # Maintenance costs per building
        num_buildings = sum(len(c.buildings) for c in civ.cities)
        total_population = sum(c.population for c in civ.cities)
        maintenance_gold = num_buildings * 1 + total_population * 1
        civ.resources.gold = max(0, civ.resources.gold - maintenance_gold)

        # Tech level bonus to science
        civ.resources.science += civ.tech_level

        # Store food in first city for growth tracking
        if civ.cities:
            food_diff = total_output.food - total_population  # net food after consumption
            civ.cities[0].food_stored += food_diff


def _update_population(state: GameState):
    """Handle population growth and decline."""
    for civ in state.civilizations:
        if not civ.is_alive:
            continue

        for city in civ.cities:
            # Population growth
            if city.food_stored >= city.food_needed:
                city.population += 1
                city.food_stored = 0
                city.food_needed = POPULATION_GROWTH_THRESHOLD * city.population
                civ.history.append(
                    f"Turn {state.turn}: {city.name} grew to population {city.population}."
                )

            # Population decline if food is negative
            food_per_turn = city.get_output().food
            net_food = civ.resources.food - city.food_stored  # approximate tracking
            if net_food < 0 and city.population > 1:
                city.population = max(1, city.population - 1)
                civ.history.append(
                    f"Turn {state.turn}: {city.name} shrank to population {city.population} due to famine."
                )


def _update_relations(state: GameState):
    """Decay diplomacy relations toward neutral."""
    for civ in state.civilizations:
        if not civ.is_alive:
            continue
        for other_id in civ.relations:
            current = civ.relations[other_id]
            if current > 0:
                civ.relations[other_id] = max(0, current - RELATIONS_DECAY_RATE)
            elif current < 0:
                civ.relations[other_id] = min(0, current + RELATIONS_DECAY_RATE)


def _check_civilization_status(state: GameState):
    """Check if civilizations have been eliminated (no cities or population 0)."""
    for civ in state.civilizations:
        if not civ.is_alive:
            continue
        if not civ.cities:
            civ.is_alive = False
            event = GameEvent(
                id=f"evt_{state.turn}_elim_{civ.id}",
                turn=state.turn,
                type=EventType.plague,
                title=f"{civ.name} has fallen",
                description=f"{civ.name} has been wiped from the world.",
                effects=None,
                target_civ_id=civ.id,
                source="natural",
            )
            state.events.append(event)
            continue

        # Check all cities have positive population
        total_pop = sum(c.population for c in civ.cities)
        if total_pop <= 0:
            civ.is_alive = False
            event = GameEvent(
                id=f"evt_{state.turn}_elim_{civ.id}",
                turn=state.turn,
                type=EventType.plague,
                title=f"{civ.name} has been destroyed",
                description=f"All citizens of {civ.name} have perished.",
                effects=None,
                target_civ_id=civ.id,
                source="natural",
            )
            state.events.append(event)

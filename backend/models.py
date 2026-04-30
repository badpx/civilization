"""Pydantic data models for the civilization simulation."""

from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class TerrainType(str, Enum):
    plains = "plains"
    forest = "forest"
    hills = "hills"
    mountain = "mountain"
    water = "water"
    desert = "desert"
    grassland = "grassland"


class BuildingType(str, Enum):
    granary = "granary"
    workshop = "workshop"
    market = "market"
    library = "library"
    amphitheater = "amphitheater"
    walls = "walls"
    temple = "temple"
    aqueduct = "aqueduct"


class WonderType(str, Enum):
    pyramid = "pyramid"
    great_wall = "great_wall"
    colosseum = "colosseum"
    hanging_garden = "hanging_garden"
    lighthouse = "lighthouse"
    library_alex = "library_alex"


class ActionType(str, Enum):
    build = "build"
    research = "research"
    diplomacy = "diplomacy"
    military = "military"
    culture = "culture"


class EventType(str, Enum):
    drought = "drought"
    flood = "flood"
    plague = "plague"
    earthquake = "earthquake"
    bountiful_harvest = "bountiful_harvest"
    golden_age = "golden_age"
    discovery = "discovery"
    divine_blessing = "divine_blessing"
    divine_wrath = "divine_wrath"
    divine_oracle = "divine_oracle"


class Resources(BaseModel):
    food: int = 0
    production: int = 0
    gold: int = 0
    science: int = 0
    culture: int = 0
    defense: int = 0

    def __add__(self, other: Resources) -> Resources:
        return Resources(
            food=self.food + other.food,
            production=self.production + other.production,
            gold=self.gold + other.gold,
            science=self.science + other.science,
            culture=self.culture + other.culture,
            defense=self.defense + other.defense,
        )

    def __sub__(self, other: Resources) -> Resources:
        return Resources(
            food=self.food - other.food,
            production=self.production - other.production,
            gold=self.gold - other.gold,
            science=self.science - other.science,
            culture=self.culture - other.culture,
            defense=self.defense - other.defense,
        )


class City(BaseModel):
    name: str
    x: int
    y: int
    population: int = 1
    buildings: List[BuildingType] = Field(default_factory=list)
    wonders: List[WonderType] = Field(default_factory=list)
    terrain: TerrainType = TerrainType.plains
    defense: int = 0
    food_stored: int = 0
    food_needed: int = 20
    production_stored: int = 0
    science_stored: int = 0
    building_queue: List[BuildingType] = Field(default_factory=list)

    def get_output(self) -> Resources:
        """Calculate resource output based on terrain, buildings, population, and wonders."""
        from backend.config import TERRAIN_YIELDS, BUILDING_COSTS

        # Base terrain yield
        base = TERRAIN_YIELDS.get(self.terrain.value, TERRAIN_YIELDS["plains"])
        output = Resources(
            food=base["food"],
            production=base["production"],
            gold=base["gold"],
            science=base["science"],
            culture=base["culture"],
        )

        # Population bonus: each pop provides +1 food and +1 production baseline
        output.food += self.population * 1
        output.production += self.population * 1

        # Building bonuses
        for building in self.buildings:
            costs = BUILDING_COSTS.get(building.value)
            if costs:
                output.food += costs.get("food_bonus", 0)
                output.production += costs.get("production_bonus", 0)
                output.gold += costs.get("gold_bonus", 0)
                output.science += costs.get("science_bonus", 0)
                output.culture += costs.get("culture_bonus", 0)

        # Wonder bonuses
        wonder_defense_bonus = 0
        for wonder in self.wonders:
            if wonder == WonderType.pyramid:
                output.production += 2
            elif wonder == WonderType.great_wall:
                wonder_defense_bonus += 5
            elif wonder == WonderType.colosseum:
                output.culture += 3
            elif wonder == WonderType.hanging_garden:
                output.food += 3
            elif wonder == WonderType.lighthouse:
                output.gold += 3
            elif wonder == WonderType.library_alex:
                output.science += 3

        # Defense from buildings
        if BuildingType.walls in self.buildings:
            wonder_defense_bonus += 5

        output.defense = self.defense + wonder_defense_bonus
        return output


class GameEvent(BaseModel):
    id: str
    turn: int
    type: EventType
    title: str
    description: str
    effects: Optional[Dict[str, int]] = None
    target_civ_id: Optional[str] = None
    source: str = "natural"  # "natural" or "divine"


class Civilization(BaseModel):
    id: str
    name: str
    leader_name: str
    personality: str
    color: str
    cities: List[City] = Field(default_factory=list)
    resources: Resources = Field(default_factory=Resources)
    tech_level: int = 1
    military: int = 5
    culture: int = 5
    happiness: int = 5
    relations: Dict[str, int] = Field(default_factory=dict)  # civ_id -> value
    history: List[str] = Field(default_factory=list)
    is_alive: bool = True

    def total_output(self) -> Resources:
        total = Resources()
        for city in self.cities:
            total += city.get_output()
        return total


class GameState(BaseModel):
    turn: int = 0
    civilizations: List[Civilization] = Field(default_factory=list)
    events: List[GameEvent] = Field(default_factory=list)
    map_grid: List[List[TerrainType]] = Field(default_factory=list)
    current_event_id: int = 0
    is_running: bool = False

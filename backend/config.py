"""Game configuration constants."""

import os

# 火山方舟 (ARK) configuration
ARK_API_KEY = os.environ.get("ARK_API_KEY", "")
ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/coding/v3"
ARK_MODEL = "doubao-seed-2.0-lite"

# OpenRouter configuration - for LLM agents
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = "deepseek/deepseek-v4-pro"

# Game constants
MAP_WIDTH = 30
MAP_HEIGHT = 20
NUM_CIVILIZATIONS = 4
STARTING_POPULATION = 5
POPULATION_GROWTH_THRESHOLD = 20
POPULATION_DECLINE_THRESHOLD = 0
EVENT_TRIGGER_CHANCE = 0.3
MAX_TURNS_AUTO = 200
TURN_DELAY_SECONDS = 2
RELATIONS_DECAY_RATE = 1

# Starting resources
STARTING_FOOD = 15
STARTING_PRODUCTION = 10
STARTING_GOLD = 10
STARTING_SCIENCE = 5
STARTING_CULTURE = 5

# Building costs and effects
BUILDING_COSTS = {
    "granary": {"production": 30, "food_bonus": 2},
    "workshop": {"production": 40, "production_bonus": 2},
    "market": {"production": 35, "gold_bonus": 3},
    "library": {"production": 50, "science_bonus": 2},
    "amphitheater": {"production": 40, "culture_bonus": 2},
    "walls": {"production": 30, "defense_bonus": 5},
    "temple": {"production": 45, "happiness_bonus": 2},
    "aqueduct": {"production": 35, "food_bonus": 3},
}

# Terrain base yields
TERRAIN_YIELDS = {
    "plains": {"food": 2, "production": 1, "gold": 0, "science": 0, "culture": 0},
    "forest": {"food": 1, "production": 2, "gold": 0, "science": 0, "culture": 0},
    "hills": {"food": 0, "production": 3, "gold": 1, "science": 0, "culture": 0},
    "mountain": {"food": 0, "production": 1, "gold": 0, "science": 1, "culture": 0},
    "water": {"food": 0, "production": 0, "gold": 0, "science": 0, "culture": 0},
    "desert": {"food": 1, "production": 1, "gold": 0, "science": 0, "culture": 1},
    "grassland": {"food": 3, "production": 0, "gold": 1, "science": 0, "culture": 0},
}

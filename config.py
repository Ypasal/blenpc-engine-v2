"""Global configuration and architectural constants for MF v5.1."""

# Architectural Units (ISO 2848 inspired)
GRID_UNIT = 0.25  # Meters
STORY_HEIGHT = 3.0  # Meters
WALL_THICKNESS_BASE = 0.2  # Meters

# Performance & Limits
MAX_SLOTS_PER_OBJECT = 32
MAX_OBJECTS_PER_ROOM = 50
MAX_LIBRARY_ASSETS = 10000
MAX_RECURSIVE_DEPTH = 1
BLENDER_MEMORY_WARN = 3000  # MB

# Validations
ALLOWED_ROTATIONS = [0, 90, 180, 270]
MIN_ROOM_DIMENSION = 2.0  # Meters

# Math Constants
PHI = (1 + 5**0.5) / 2  # Golden Ratio

# Paths
LIBRARY_PATH = "_library/"
REGISTRY_PATH = "_registry/"
INVENTORY_FILE = REGISTRY_PATH + "inventory.json"
SLOTS_FILE = REGISTRY_PATH + "slot_types.json"
TAGS_FILE = REGISTRY_PATH + "tag_vocabulary.json"

# Blender Commands
BLENDER_PATH = "/home/ubuntu/blender5/blender"
HEADLESS_ARGS = ["--background", "--python"]

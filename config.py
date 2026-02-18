import os

"""Global configuration and architectural constants for MF v5.1."""

# Project Root (determined dynamically)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

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

# Paths (relative to PROJECT_ROOT)
LIBRARY_DIR = os.path.join(PROJECT_ROOT, "_library")
REGISTRY_DIR = os.path.join(PROJECT_ROOT, "_registry")
INVENTORY_FILE = os.path.join(REGISTRY_DIR, "inventory.json")
SLOTS_FILE = os.path.join(REGISTRY_DIR, "slot_types.json")
TAGS_FILE = os.path.join(REGISTRY_DIR, "tag_vocabulary.json")

# Blender Commands
# IMPORTANT: This path needs to be configured for the specific OS and Blender installation.
# For Windows, it might be something like 'C:\Program Files\Blender Foundation\Blender 5.0\blender.exe'
# For Linux, it's currently set to the installed path.
BLENDER_PATH = os.environ.get("BLENDER_EXECUTABLE", os.path.join(os.path.expanduser("~"), "blender5", "blender"))
HEADLESS_ARGS = ["--background", "--python"]

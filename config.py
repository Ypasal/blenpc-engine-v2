import os
import platform
import logging

"""Global configuration and architectural constants for MF v5.1."""

# Configure logging
LOG_LEVEL = os.getenv("MF_LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("MF_LOG_FILE", None)

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE) if LOG_FILE else logging.NullHandler()
    ]
)

logger = logging.getLogger("blenpc")

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
def get_blender_path():
    env_path = os.getenv("BLENDER_PATH") or os.getenv("BLENDER_EXECUTABLE")
    if env_path and os.path.exists(env_path):
        return env_path
    
    if platform.system() == "Windows":
        return r"C:\Program Files\Blender Foundation\Blender 5.0\blender.exe"
    elif platform.system() == "Darwin":
        return "/Applications/Blender.app/Contents/MacOS/Blender"
    else:
        # Default for linux/sandbox
        return "/usr/bin/blender"

BLENDER_PATH = get_blender_path()
HEADLESS_ARGS = ["--background", "--python"]

# Slot Generation Constants
GOLDEN_RATIO_VARIATION = 0.04  # +/- 4% variation
WINDOW_SILL_HEIGHT_DEFAULT = 1.2  # meters
WINDOW_DEFAULT_WIDTH = 1.0  # meters
WINDOW_DEFAULT_HEIGHT = 1.2  # meters

# Inventory Locking Constants
INVENTORY_LOCK_TIMEOUT = 5  # seconds
INVENTORY_LOCK_POLL_INTERVAL = 0.1  # seconds
INVENTORY_LOCK_STALE_AGE = 60  # seconds

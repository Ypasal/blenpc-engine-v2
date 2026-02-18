import os
import platform
import logging
from typing import Any, Dict

"""BlenPC v5.1.1 - Core Configuration System."""

# --- 1. LOGGING CONFIGURATION ---
LOG_LEVEL = os.getenv("MF_LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("MF_LOG_FILE", None)
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s [%(filename)s:%(lineno)d] - %(message)s'

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE) if LOG_FILE else logging.NullHandler()
    ]
)
logger = logging.getLogger("blenpc")

# --- 2. PATH MANAGEMENT ---
PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(PACKAGE_ROOT))

LIBRARY_DIR = os.path.join(PROJECT_ROOT, "_library")
REGISTRY_DIR = os.path.join(PROJECT_ROOT, "_registry")
INVENTORY_FILE = os.path.join(REGISTRY_DIR, "inventory.json")
SLOTS_FILE = os.path.join(REGISTRY_DIR, "slot_types.json")
TAGS_FILE = os.path.join(REGISTRY_DIR, "tag_vocabulary.json")

# --- 3. BLENDER EXECUTABLE ---
def get_blender_path():
    env_path = os.getenv("BLENDER_PATH") or os.getenv("BLENDER_EXECUTABLE")
    if env_path and os.path.exists(env_path):
        return env_path
    
    if platform.system() == "Windows":
        paths = [
            r"C:\Program Files\Blender Foundation\Blender 5.0\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe",
            os.path.expandvars(r"%APPDATA%\Blender Foundation\Blender\blender.exe")
        ]
        for p in paths:
            if os.path.exists(p): return p
        return "blender.exe"
    elif platform.system() == "Darwin":
        return "/Applications/Blender.app/Contents/MacOS/Blender"
    else:
        return "/usr/bin/blender"

BLENDER_PATH = get_blender_path()
HEADLESS_ARGS = ["--background", "--python"]

# --- 4. PERFORMANCE & LIMITS ---
MAX_WORKER_PROCESSES = os.cpu_count() or 4
STRICT_VALIDATION = True
CACHE_ENABLED = True
AUTO_BACKUP_REGISTRY = True
BLENDER_MEMORY_WARN = 3000

# --- 5. ARCHITECTURAL CONSTANTS ---
GRID_UNIT = 0.25
STORY_HEIGHT = 3.0
WALL_THICKNESS_BASE = 0.2
DEFAULT_UNIT_SYSTEM = "metric"
EXPORT_PRECISION = 4

# --- 6. MATH CONSTANTS ---
PHI = (1 + 5**0.5) / 2
GOLDEN_RATIO_VARIATION = 0.04

# --- 7. INVENTORY LOCKING ---
INVENTORY_LOCK_TIMEOUT = 5
INVENTORY_LOCK_POLL_INTERVAL = 0.1
INVENTORY_LOCK_STALE_AGE = 60

# --- 8. EXPORT SETTINGS ---
EXPORT_FORMATS_SUPPORTED = ["glb", "blend", "fbx", "obj"]

# --- 9. DEFAULTS ---
DEFAULT_ROOF_PITCH = 35.0
WINDOW_SILL_HEIGHT_DEFAULT = 1.2
WINDOW_DEFAULT_WIDTH = 1.0
WINDOW_DEFAULT_HEIGHT = 1.2
TEST_TIMEOUT_DEFAULT = 120

def get_settings() -> Dict[str, Any]:
    return {k: v for k, v in globals().items() if k.isupper()}

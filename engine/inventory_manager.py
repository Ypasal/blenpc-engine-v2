import json
import os
import time
from typing import List, Dict, Optional

# Use absolute import from the project rootfrom config import INVENTORY_FILE, REGISTRY_DIR
LOCK_FILE = os.path.join(REGISTRY_DIR, ".inventory.lock")

class InventoryManager:
    @staticmethod
    def acquire_lock(timeout=5):
        """Acquire a simple file lock for inventory operations."""
        start_time = time.time()
        while os.path.exists(LOCK_FILE):
            if time.time() - start_time > timeout:
                raise TimeoutError("Could not acquire inventory lock")
            time.sleep(0.1)
        with open(LOCK_FILE, "w") as f:
            f.write(str(os.getpid()))

    @staticmethod
    def release_lock():
        """Release the inventory file lock."""
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)

    @staticmethod
    def find_asset(tags: List[str]) -> Optional[Dict]:
        """Find an asset matching all tags using the registry."""
        if not os.path.exists(INVENTORY_FILE):
            return None
            
        with open(INVENTORY_FILE, "r") as f:
            inventory = json.load(f)
            
        for asset_name, asset_data in inventory.get("assets", {}).items():
            asset_tags = asset_data.get("tags", [])
            if all(tag in asset_tags for tag in tags):
                return asset_data
        return None

    @staticmethod
    def register_asset(asset_data: Dict):
        """Add or update an asset in the inventory with locking."""
        InventoryManager.acquire_lock()
        try:
            inventory = {"version": "1.0", "assets": {}}
            if os.path.exists(INVENTORY_FILE):
                with open(INVENTORY_FILE, "r") as f:
                    inventory = json.load(f)
            
            name = asset_data["name"]
            inventory["assets"][name] = asset_data
            inventory["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            
            # Ensure directory exists
            os.makedirs(REGISTRY_DIR, exist_ok=True)
            
            with open(INVENTORY_FILE, "w") as f:
                json.dump(inventory, f, indent=2)
        finally:
            InventoryManager.release_lock()

import json
import os
from threading import Lock
from typing import Dict


class EndpointRegistry:
    def __init__(self, storage_path: str = "data/registry.json"):
        self._registry: Dict[str, Dict] = {}
        self._lock = Lock()
        self._storage_path = storage_path

        # Auto-create directory and load on startup
        os.makedirs(os.path.dirname(self._storage_path), exist_ok=True)
        self.load_from_disk()

    def add(self, endpoint_name: str, config: Dict):
        with self._lock:
            self._registry[endpoint_name] = config
            self.save_to_disk()

    def update(self, endpoint_name: str, config: Dict):
        with self._lock:
            if endpoint_name in self._registry:
                self._registry[endpoint_name].update(config)
                self.save_to_disk()

    def delete(self, endpoint_name: str):
        with self._lock:
            self._registry.pop(endpoint_name, None)
            self.save_to_disk()

    def get(self, endpoint_name: str) -> Dict:
        return self._registry.get(endpoint_name, {})

    def list_all(self) -> Dict[str, Dict]:
        return self._registry.copy()

    def save_to_disk(self):
        with open(self._storage_path, "w") as f:
            json.dump(self._registry, f, indent=2)

    def load_from_disk(self):
        if os.path.exists(self._storage_path):
            with open(self._storage_path, "r") as f:
                self._registry = json.load(f)

import os
import json

class JsonStore:
    def __init__(self, base_dir):
        self.base_dir = base_dir

    def _get_full_path(self, relative_path):
        return os.path.join(self.base_dir, relative_path)

    def read_json(self, relative_path):
        full_path = self._get_full_path(relative_path)
        if os.path.exists(full_path):
            with open(full_path, 'r') as f:
                return json.load(f)
        return {}

    def write_json(self, relative_path, data):
        full_path = self._get_full_path(relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            json.dump(data, f, indent=4)

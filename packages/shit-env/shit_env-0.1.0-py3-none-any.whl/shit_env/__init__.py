import os
from typing import Optional

class Env:
    def __init__(self, path_or_name: str = '.env'):
        self.env_path = path_or_name if path_or_name.endswith('.env') else f'{path_or_name}.env'
        self.vars = {}
        self._load()

    def _load(self):
        if os.path.exists(self.env_path):
            with open(self.env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' in line:
                        key, value = line.split('=', 1)
                        self.vars[key.strip()] = value.strip()

    def Get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        return self.vars.get(key, default)

    def Set(self, key: str, value: str):
        self.vars[key] = value
        self._save()

    def _save(self):
        with open(self.env_path, 'w') as f:
            for key, value in self.vars.items():
                f.write(f'{key}={value}\n')

def Required(key: str, env_path: str = '.env') -> str:
    env = Env(env_path)
    value = env.Get(key)
    if value is None or value == '':
        raise RuntimeError(f"Required environment variable '{key}' is missing or empty in {env_path}")
    return value 
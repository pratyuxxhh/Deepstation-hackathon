import json
from pathlib import Path
from functools import lru_cache

DATA_PATH = Path(__file__).parent / "mock_bins.json"

@lru_cache(maxsize=1)
def load_bins() -> list[dict]:
    with open(DATA_PATH) as f:
        return json.load(f)

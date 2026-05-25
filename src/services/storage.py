import json
import os
from src.core.config import DATA_DIR


def _ensure_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


def load_json(path: str) -> list | dict:
    _ensure_dir()
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data: list | dict) -> None:
    _ensure_dir()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

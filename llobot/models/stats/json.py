from __future__ import annotations
from pathlib import Path
import json
import llobot.fs
from llobot.models.stats import ModelStats

def format(stats: ModelStats) -> str:
    return json.dumps(dict(stats))

def parse(formatted: str) -> ModelStats:
    return ModelStats(json.loads(formatted))

def save(path: Path, stats: ModelStats):
    llobot.fs.write_text(path, format(stats))

def load(path: Path) -> ModelStats:
    if path.exists():
        try:
            return parse(llobot.fs.read_text(path))
        except:
            return ModelStats()
    return ModelStats()

__all__ = [
    'format',
    'parse',
    'save',
    'load',
]


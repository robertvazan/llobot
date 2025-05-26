from pathlib import Path

def home() -> Path:
    return Path.home()

# TODO: Use platform-independent paths (platformdirs package).

def data() -> Path:
    return home()/'.local/share'

def cache() -> Path:
    return home()/'.cache'

def create_parents(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)

def write_bytes(path: Path, data: bytes):
    create_parents(path)
    path.write_bytes(data)

def write_text(path: Path, content: str):
    write_bytes(path, content.encode('utf-8'))

def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8')
    except Exception as ex:
        raise ValueError(path) from ex

def stem(path: Path | str) -> str:
    path = Path(path)
    while path.suffix:
        path = path.with_suffix('')
    return path.name

__all__ = [
    'home',
    'data',
    'cache',
    'create_parents',
    'write_bytes',
    'write_text',
    'read_text',
    'stem',
]


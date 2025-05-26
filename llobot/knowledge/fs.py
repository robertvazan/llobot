from pathlib import Path
from llobot.knowledge import Knowledge
import llobot.fs
import llobot.knowledge
import llobot.knowledge.indexes

def save(directory: Path, knowledge: Knowledge):
    for path, content in knowledge:
        llobot.fs.write_text(directory/path, content)

def load(directory: Path) -> Knowledge:
    # Use faster, simpler rglob to load unfiltered knowledge from archive.
    index = KnowledgeIndex(path.relative_to(directory) for path in directory.rglob('*') if path.is_file())
    return Knowledge({path: llobot.fs.read_text(directory/path) for path in index})

__all__ = [
    'save',
    'load',
]


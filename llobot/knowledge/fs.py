from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.fs import read_document, write_text

def save_knowledge_directory(directory: Path, knowledge: Knowledge):
    for path, content in knowledge:
        write_text(directory/path, content)

def load_knowledge_directory(directory: Path) -> Knowledge:
    # Use faster, simpler rglob to load unfiltered knowledge from archive.
    index = KnowledgeIndex(path.relative_to(directory) for path in directory.rglob('*') if path.is_file())
    return Knowledge({path: read_document(directory/path) for path in index})

__all__ = [
    'save_knowledge_directory',
    'load_knowledge_directory',
]

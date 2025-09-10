"""
Utilities for saving and loading knowledge to/from a plain directory.
"""
from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.utils.fs import read_document, write_text

def save_knowledge_directory(directory: Path, knowledge: Knowledge):
    """
    Saves a knowledge base to a directory.

    Each document in the knowledge base is saved as a separate file. The directory
    structure is created as needed.

    Args:
        directory: The directory to save to.
        knowledge: The knowledge base to save.
    """
    for path, content in knowledge:
        write_text(directory/path, content)

def load_knowledge_directory(directory: Path) -> Knowledge:
    """
    Loads a knowledge base from a directory.

    This function recursively finds all files in the directory and loads them
    as documents into a `Knowledge` object.

    Args:
        directory: The directory to load from.

    Returns:
        The loaded knowledge base.
    """
    # Use faster, simpler rglob to load unfiltered knowledge from archive.
    index = KnowledgeIndex(path.relative_to(directory) for path in directory.rglob('*') if path.is_file())
    return Knowledge({path: read_document(directory/path) for path in index})

__all__ = [
    'save_knowledge_directory',
    'load_knowledge_directory',
]

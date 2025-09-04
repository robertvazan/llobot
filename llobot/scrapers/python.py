from __future__ import annotations
from functools import cache
import re
from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.graphs import KnowledgeGraph, KnowledgeGraphBuilder
from llobot.scrapers import GraphScraper, create_scraper
from llobot.scrapers.index import ScrapingIndex, create_scraping_index

def _python_module_paths(module: str) -> tuple[Path, Path]:
    """
    Returns the two possible paths for a Python module: module.py and module/__init__.py
    """
    module_path = Path(module.replace('.', '/'))
    return (module_path.with_suffix('.py'), module_path / '__init__.py')

def _parse_path(path: Path) -> Path:
    """
    Converts a file path to its module path.
    Examples:
    - foo/bar/__init__.py -> foo/bar
    - foo/bar.py -> foo/bar
    - __init__.py -> (empty)
    """
    path = path.with_suffix('')
    if path.name == '__init__':
        path = path.parent
    return path

def _parse_relative_import(module: str, source: Path) -> Path | None:
    """
    Parses a relative import module string relative to source path.
    Returns absolute path or None if cannot be resolved.
    """
    if not module.startswith('.'):
        return None

    # Get the module path of the source file
    source_module = _parse_path(source)

    # Count leading dots and remove them
    dots = 0
    while dots < len(module) and module[dots] == '.':
        dots += 1

    module_name = module[dots:]

    # Navigate up the directory tree based on number of dots
    current = source_module
    for _ in range(dots):
        if current.parts:
            current = current.parent
        else:
            # Too many dots, can't resolve
            return None

    # Add the module name if present
    if module_name:
        current = current / module_name.replace('.', '/')

    return current

def _resolve_python_module(knowledge: Knowledge, source: Path, module: str, index: ScrapingIndex) -> Path | None:
    """
    Resolves a Python module import to a target path.
    Uses direct lookup for relative imports, ScrapingIndex for absolute imports.
    """
    if module.startswith('.'):
        # Relative import - we can compute the absolute path
        absolute_path = _parse_relative_import(module, source)
        if absolute_path is None:
            return None

        # Check both possible module file locations directly
        py_path, init_path = _python_module_paths(str(absolute_path))

        if py_path in knowledge:
            return py_path
        elif init_path in knowledge:
            return init_path
        else:
            return None
    else:
        # Absolute import - use scraping index for fuzzy matching
        py_path, init_path = _python_module_paths(module)
        return index.lookup(source, py_path, init_path)

@cache
def simple_imports_python_scraper() -> GraphScraper:
    pattern = re.compile(r'^ *import ([\w_]+(?:\.[\w_]+)*)', re.MULTILINE)
    def scrape(knowledge: Knowledge) -> KnowledgeGraph:
        builder = KnowledgeGraphBuilder()
        index = create_scraping_index(knowledge)
        for path, content in knowledge:
            if path.suffix == '.py':
                for module in pattern.findall(content):
                    # Simple imports cannot be relative, so use index directly
                    py_path, init_path = _python_module_paths(module)
                    target = index.lookup(path, py_path, init_path)
                    if target:
                        builder.add(path, target)
        return builder.build()
    return create_scraper(scrape)

@cache
def from_imports_python_scraper() -> GraphScraper:
    pattern = re.compile(r'^ *from ([\w_.]+) import', re.MULTILINE)
    def scrape(knowledge: Knowledge) -> KnowledgeGraph:
        builder = KnowledgeGraphBuilder()
        index = create_scraping_index(knowledge)
        for path, content in knowledge:
            if path.suffix == '.py':
                modules = set(pattern.findall(content))
                for module in modules:
                    target = _resolve_python_module(knowledge, path, module, index)
                    if target:
                        builder.add(path, target)
        return builder.build()
    return create_scraper(scrape)

@cache
def item_imports_python_scraper() -> GraphScraper:
    from_re = re.compile(r'^ *from ([\w_.]+) import ([\w_.]+(?: as [\w_]+)?(?:, [\w_.]+(?: as [\w_]+)?)*)', re.MULTILINE)
    multiline_re = re.compile(r'^ *from ([\w_.]+) import +\(\s*([\w_.]+(?: as [\w_]+)?(?:,\s*[\w_.]+(?: as [\w_]+)?)*)', re.MULTILINE)
    item_re = re.compile(r'([\w_.]+)(?: as [\w_]+)?')
    def scrape(knowledge: Knowledge) -> KnowledgeGraph:
        builder = KnowledgeGraphBuilder()
        index = create_scraping_index(knowledge)
        for path, content in knowledge:
            if path.suffix == '.py':
                for module, items in from_re.findall(content) + multiline_re.findall(content):
                    for item in item_re.findall(items):
                        # Try to resolve as a module first (item could be a submodule)
                        base_module = f"{module}.{item}"
                        target = _resolve_python_module(knowledge, path, base_module, index)
                        if target:
                            builder.add(path, target)
        return builder.build()
    return create_scraper(scrape)

@cache
def imports_python_scraper() -> GraphScraper:
    return simple_imports_python_scraper() | from_imports_python_scraper() | item_imports_python_scraper()

@cache
def standard_python_scraper() -> GraphScraper:
    return imports_python_scraper()

__all__ = [
    'simple_imports_python_scraper',
    'from_imports_python_scraper',
    'item_imports_python_scraper',
    'imports_python_scraper',
    'standard_python_scraper',
]

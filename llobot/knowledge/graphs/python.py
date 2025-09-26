"""
Crawlers for Python source code.
"""
from __future__ import annotations
from functools import cache
import re
from pathlib import Path
from llobot.utils.values import ValueTypeMixin
from llobot.knowledge import Knowledge
from llobot.knowledge.graphs import KnowledgeGraph
from llobot.knowledge.graphs.builder import KnowledgeGraphBuilder
from llobot.knowledge.graphs.crawler import KnowledgeCrawler
from llobot.knowledge.resolver import KnowledgeResolver, cached_knowledge_resolver

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

    # Count leading dots and remove them
    dots = 0
    while dots < len(module) and module[dots] == '.':
        dots += 1
    
    module_name = module[dots:]
    
    # For relative imports, we start from the source file's directory.
    # `dots`=1 means same directory, `dots`=2 means parent, etc.
    # So we go up `dots - 1` levels.
    current = source.parent
    for _ in range(dots - 1):
        if current.parts:
            current = current.parent
        else:
            # Too many dots, can't resolve
            return None
            
    # Add the module name if present
    if module_name:
        current = current / module_name.replace('.', '/')
    
    return current

def _resolve_python_module(knowledge: Knowledge, source: Path, module: str, resolver: KnowledgeResolver) -> Path | None:
    """
    Resolves a Python module import to a target path.
    Uses direct lookup for relative imports, KnowledgeResolver for absolute imports.
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
        # Absolute import - use resolver for fuzzy matching
        py_path, init_path = _python_module_paths(module)
        return resolver.resolve_near(source, py_path, init_path)

@cache
def standard_python_crawler() -> KnowledgeCrawler:
    """
    Returns the standard crawler for Python.

    The standard Python crawler handles simple, `from`, and item imports.
    """
    return PythonSimpleImportsCrawler() | PythonFromImportsCrawler() | PythonItemImportsCrawler()

class PythonSimpleImportsCrawler(KnowledgeCrawler, ValueTypeMixin):
    """
    Crawls Python files for simple `import module` statements.
    """
    _pattern = re.compile(r'^ *import ([\w_]+(?:\.[\w_]+)*)', re.MULTILINE)

    def crawl(self, knowledge: Knowledge) -> KnowledgeGraph:
        builder = KnowledgeGraphBuilder()
        resolver = cached_knowledge_resolver(knowledge)
        for path, content in knowledge:
            if path.suffix == '.py':
                for module in self._pattern.findall(content):
                    # Simple imports cannot be relative, so use resolver directly
                    py_path, init_path = _python_module_paths(module)
                    target = resolver.resolve_near(path, py_path, init_path)
                    if target:
                        builder.add(path, target)
        return builder.build()

class PythonFromImportsCrawler(KnowledgeCrawler, ValueTypeMixin):
    """
    Crawls Python files for `from module import ...` statements.
    """
    _pattern = re.compile(r'^ *from ([\.\w_]+) import', re.MULTILINE)

    def crawl(self, knowledge: Knowledge) -> KnowledgeGraph:
        builder = KnowledgeGraphBuilder()
        resolver = cached_knowledge_resolver(knowledge)
        for path, content in knowledge:
            if path.suffix == '.py':
                modules = set(self._pattern.findall(content))
                for module in modules:
                    target = _resolve_python_module(knowledge, path, module, resolver)
                    if target:
                        builder.add(path, target)
        return builder.build()

class PythonItemImportsCrawler(KnowledgeCrawler, ValueTypeMixin):
    """
    Crawls Python `from module import item` statements where `item` is a submodule.
    """
    _from_re = re.compile(r'^ *from ([\.\w_]*) import ([\w_.]+(?: as [\w_]+)?(?:, [\w_.]+(?: as [\w_]+)?)*)', re.MULTILINE)
    _multiline_re = re.compile(r'^ *from ([\.\w_]*) import +\(\s*([\w_.]+(?: as [\w_]+)?(?:,\s*[\w_.]+(?: as [\w_]+)?)*)', re.MULTILINE)
    _item_re = re.compile(r'([\w_.]+)(?: as [\w_]+)?')

    def crawl(self, knowledge: Knowledge) -> KnowledgeGraph:
        builder = KnowledgeGraphBuilder()
        resolver = cached_knowledge_resolver(knowledge)
        for path, content in knowledge:
            if path.suffix == '.py':
                for module, items in self._from_re.findall(content) + self._multiline_re.findall(content):
                    for item in self._item_re.findall(items):
                        # Try to resolve as a module first (item could be a submodule)
                        if module == '.':
                            base_module = f'.{item}'
                        elif module:
                            base_module = f'{module}.{item}'
                        else:
                            # from import x is not valid python
                            continue
                        target = _resolve_python_module(knowledge, path, base_module, resolver)
                        if target:
                            builder.add(path, target)
        return builder.build()

__all__ = [
    'standard_python_crawler',
    'PythonSimpleImportsCrawler',
    'PythonFromImportsCrawler',
    'PythonItemImportsCrawler',
]

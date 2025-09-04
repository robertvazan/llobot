from __future__ import annotations
from functools import cache
import re
from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.graphs import KnowledgeGraph, KnowledgeGraphBuilder
from llobot.scrapers import GraphScraper, create_scraper

def _source_path(source: Path) -> Path:
    """Convert a Rust file path to its module path."""
    if source.name == 'mod.rs':
        return source.parent
    else:
        return source.with_suffix('')

def _rust_module_paths(module_path: Path) -> tuple[Path, Path]:
    """Returns the two possible paths for a Rust module: module.rs and module/mod.rs"""
    return (module_path.with_suffix('.rs'), module_path / 'mod.rs')

def _resolve_use_path(source: Path, path: str, knowledge: Knowledge) -> Path | None:
    """Resolve a use statement path to a target path."""
    if not path:
        return None
    # Paths starting with root namespace are uncommon and we cannot handle them well.
    if path.startswith('::'):
        return None
    # We will save ourselves a lot of overhead by filtering out std imports early.
    if path.startswith('std::') or path == 'std':
        return None

    resolved = _source_path(source)
    segments = path.split('::')

    if segments[0] in ('self', 'crate', '$crate'):
        if segments[0] != 'self':
            # Find the nearest parent named 'src' or 'tests'.
            for parent in source.parents:
                if parent.name in ('src', 'tests'):
                    resolved = parent.parent/'src'
                    break
            else:
                # If no src or tests parent was found, the code has non-standard structure and we cannot find the the crate root.
                return None
        segments = segments[1:]

    for segment in segments:
        # We will just ignore wildcards. Theoretically, we should scan for files under the concrete module,
        # but that's complicated and wildcards are rarely used to enumerate module files anyway.
        # We will assume most wildcards are enumerating items inside of a file and it is therefore safe to ignore them in paths.
        if segment == '*':
            break
        # Special path component in the middle of the path is probably an error. Ignore the path.
        if segment in ('self', 'crate', '$crate'):
            return None
        # If it doesn't look like module name, stop here. This saves some overhead.
        if not segment.isidentifier():
            break
        if segment == 'super':
            resolved = resolved.parent
        else:
            resolved = resolved/segment

    rs_path, mod_path = _rust_module_paths(resolved)
    if rs_path in knowledge:
        return rs_path
    elif mod_path in knowledge:
        return mod_path
    else:
        return None

@cache
def submodule_rust_scraper() -> GraphScraper:
    pattern = re.compile(r'^ *(?:pub )?mod ([\w_]+);', re.MULTILINE)
    def scrape(knowledge: Knowledge) -> KnowledgeGraph:
        builder = KnowledgeGraphBuilder()
        for path, content in knowledge:
            if path.suffix == '.rs':
                for module in pattern.findall(content):
                    module_path = _source_path(path) / module
                    rs_path, mod_path = _rust_module_paths(module_path)

                    if rs_path in knowledge:
                        builder.add(path, rs_path)
                    elif mod_path in knowledge:
                        builder.add(path, mod_path)
        return builder.build()
    return create_scraper(scrape)

@cache
def use_rust_scraper() -> GraphScraper:
    statement_pattern = re.compile(r'^( *)(?:pub )?use ([^;]+);', re.MULTILINE)
    brace_pattern = re.compile(r'([\w_:]*){([^{}]*)}')
    item_pattern = re.compile(r'([\w_:]+)')
    def expand(matched) -> str:
        prefix = matched[1]
        return ', '.join([(prefix + item if prefix else item) for item in item_pattern.findall(matched[2])])
    def scrape(knowledge: Knowledge) -> KnowledgeGraph:
        builder = KnowledgeGraphBuilder()
        for path, content in knowledge:
            if path.suffix == '.rs':
                for indentation, spec in statement_pattern.findall(content):
                    while True:
                        expanded = brace_pattern.sub(expand, spec)
                        if expanded == spec:
                            break
                        spec = expanded
                    source = path
                    while indentation:
                        source = source/'nested-module'
                        indentation = indentation[4:]
                    for item in item_pattern.findall(spec):
                        target = _resolve_use_path(source, item, knowledge)
                        if target:
                            builder.add(path, target)
        return builder.build()
    return create_scraper(scrape)

@cache
def standard_rust_scraper() -> GraphScraper:
    # Including submodule references by default is a bit controversial,
    # because parent does not depend on the submodule just because it exists.
    # It is however common for dependency relationship to match submodule relationship.
    return submodule_rust_scraper() | use_rust_scraper()

__all__ = [
    'submodule_rust_scraper',
    'use_rust_scraper',
    'standard_rust_scraper',
]

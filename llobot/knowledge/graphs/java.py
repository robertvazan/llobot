"""
Crawlers for Java source code.
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
from llobot.knowledge.resolver import cached_knowledge_resolver

@cache
def standard_java_crawler() -> KnowledgeCrawler:
    """
    Returns the standard crawler for Java.

    The standard Java crawler links PascalCase identifiers to corresponding files.
    """
    return JavaPascalCaseCrawler()

class JavaPascalCaseCrawler(KnowledgeCrawler, ValueTypeMixin):
    """
    Crawls Java files for PascalCase identifiers and links them to corresponding files.
    """
    _comment_re = re.compile(r'/\*.*?\*/|//.*?$', re.MULTILINE | re.DOTALL)
    _text_block_re = re.compile(r'"""(?:[^\\]|\\.)*?"""', re.DOTALL)
    _string_re = re.compile(r'"(?:[^"\\]|\\.)*"')
    _pattern = re.compile(r'\b[A-Z][A-Za-z0-9]*\b')

    def crawl(self, knowledge: Knowledge) -> KnowledgeGraph:
        """
        Crawls Java files in the knowledge base.

        Args:
            knowledge: The knowledge base to crawl.

        Returns:
            A `KnowledgeGraph` with links from Java files to other files.
        """
        builder = KnowledgeGraphBuilder()
        resolver = cached_knowledge_resolver(knowledge)
        for path, content in knowledge:
            if path.suffix == '.java':
                content = self._comment_re.sub(' ', content)
                content = self._text_block_re.sub(' ', content)
                content = self._string_re.sub(' ', content)
                names = set(self._pattern.findall(content))
                for name in names:
                    # Require at least one lowercase letter to avoid matching enums and constants.
                    if not name.isupper():
                        target = resolver.resolve_near(path, Path(f'{name}.java'))
                        if target:
                            builder.add(path, target)
        return builder.build()

__all__ = [
    'standard_java_crawler',
    'JavaPascalCaseCrawler',
]

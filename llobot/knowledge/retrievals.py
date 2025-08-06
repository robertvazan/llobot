from __future__ import annotations
from functools import cache
import re
from pathlib import Path
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.chats import ChatMessage, ChatBranch, ChatIntent

class RetrievalScraper:
    def scrape(self, prompt: str, index: KnowledgeIndex) -> KnowledgeIndex:
        return KnowledgeIndex()

    def __call__(self, prompt: str | ChatMessage | ChatBranch, index: KnowledgeIndex) -> KnowledgeIndex:
        if isinstance(prompt, ChatMessage):
            return self.scrape(prompt.content, index)
        if isinstance(prompt, ChatBranch):
            found = KnowledgeIndex()
            for message in prompt:
                if message.intent == ChatIntent.PROMPT:
                    found |= self(message.content, index)
            return found
        if isinstance(prompt, str):
            return self.scrape(prompt, index)
        raise TypeError

@cache
def backticks() -> RetrievalScraper:
    pattern = re.compile(r'`((?:[A-Za-z_][\w.-]*/)*[A-Za-z_][\w.-]*\.[a-z]+)`')
    class BackticksRetrievalScraper(RetrievalScraper):
        def scrape(self, prompt: str, index: KnowledgeIndex) -> KnowledgeIndex:
            hits = pattern.findall(prompt)
            if not hits:
                return KnowledgeIndex()

            matches = set()
            for hit in hits:
                for path in index:
                    if path.match(hit):
                        matches.add(path)
            return KnowledgeIndex(matches)

    return BackticksRetrievalScraper()

@cache
def standard() -> RetrievalScraper:
    return backticks()

__all__ = [
    'RetrievalScraper',
    'backticks',
    'standard',
]

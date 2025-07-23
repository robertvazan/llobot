from __future__ import annotations
from functools import cache, lru_cache
from pathlib import Path
import re
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.formatters.languages import LanguageGuesser
from llobot.knowledge.deltas import DocumentDelta, KnowledgeDelta, KnowledgeDeltaBuilder
from llobot.chats import ChatMessage, ChatBranch
import llobot.knowledge.subsets
import llobot.knowledge.subsets.markdown
import llobot.formatters.languages
import llobot.text

# Build regex for multi-backtick code blocks (3-10 backticks)
_CODE_BLOCK_PATTERN = '|'.join(rf'{"`" * i}[^`\n]*\n.*?^{"`" * i}' for i in range(3, 11))

# Regex for complete details block with file listing
_DETAILS_PATTERN = rf'<details>\n<summary>[^\n]+</summary>\n\n(?:{_CODE_BLOCK_PATTERN})\n\n</details>'

# Combined detection regex: details blocks or bare code blocks (to skip the latter)
_DETECTION_REGEX = re.compile(f'^(?:(?:{_DETAILS_PATTERN})|(?:{_CODE_BLOCK_PATTERN}))$', re.MULTILINE | re.DOTALL)

# Parsing regex for details blocks
_PARSING_RE = re.compile(rf'<details>\n<summary>File: ([^\n]+?)(?: \(([^\n)]*)\))?</summary>\n\n```+[^\n]*\n(.*)^```+\n\n</details>', re.MULTILINE | re.DOTALL)

_MOVED_FROM_RE = re.compile(r"moved from (.+)")

class EnvelopeFormatter:
    # May return None to indicate it cannot handle the file, which is useful for combining several formatters.
    def format(self, delta: DocumentDelta) -> str | None:
        return None

    def __call__(self, delta: DocumentDelta) -> str | None:
        return self.format(delta)

    def format_all(self, delta: KnowledgeDelta) -> str:
        return llobot.text.concat(*(self.format(d) for d in delta))

    def find(self, message: str) -> list[str]:
        return []

    def parse(self, formatted: str) -> DocumentDelta | None:
        return None

    def parse_message(self, message: str | ChatMessage) -> KnowledgeDelta:
        if isinstance(message, ChatMessage):
            message = message.content

        builder = KnowledgeDeltaBuilder()
        for match in self.find(message):
            delta = self.parse(match)
            if delta:
                builder.add(delta)
        return builder.build()

    def parse_chat(self, chat: ChatBranch) -> KnowledgeDelta:
        builder = KnowledgeDeltaBuilder()
        for message in chat:
            builder.add(self.parse_message(message.content))
        return builder.build()

    def __or__(self, other: EnvelopeFormatter) -> EnvelopeFormatter:
        myself = self
        class OrEnvelopeFormatter(EnvelopeFormatter):
            def format(self, delta: DocumentDelta) -> str | None:
                return myself.format(delta) or other.format(delta)
            def find(self, message: str) -> list[str]:
                return myself.find(message) + other.find(message)
            def parse(self, formatted: str) -> DocumentDelta | None:
                delta = myself.parse(formatted)
                if delta:
                    return delta
                return other.parse(formatted)
        return OrEnvelopeFormatter()

    def __and__(self, whitelist: KnowledgeSubset | str) -> EnvelopeFormatter:
        myself = self
        whitelist = llobot.knowledge.subsets.coerce(whitelist)
        class AndEnvelopeFormatter(EnvelopeFormatter):
            def format(self, delta: DocumentDelta) -> str | None:
                return myself.format(delta) if whitelist(delta.path, delta.content or '') else None
            def find(self, message: str) -> list[str]:
                return myself.find(message)
            def parse(self, formatted: str) -> DocumentDelta | None:
                delta = myself.parse(formatted)
                if delta and not whitelist(delta.path, delta.content or ''):
                    return None
                return delta
        return AndEnvelopeFormatter()

@lru_cache
def header(*,
    guesser: LanguageGuesser = llobot.formatters.languages.standard(),
    quad_backticks: list[str] = ['markdown'],
) -> EnvelopeFormatter:
    class HeaderEnvelopeFormatter(EnvelopeFormatter):
        def format(self, delta: DocumentDelta) -> str | None:
            flags = []
            if delta.new: flags.append('new')
            if delta.modified: flags.append('modified')
            if delta.diff: flags.append('diff')
            if delta.removed: flags.append('removed')
            if delta.moved_from: flags.append(f"moved from {delta.moved_from}")
            flag_str = ', '.join(flags)
            flag_suffix = f' ({flag_str})' if flag_str else ''

            # Always include content, even if empty
            content = delta.content or ''
            lang = 'diff' if delta.diff else guesser(delta.path, content)
            backtick_count = 4 if lang in quad_backticks else 3
            quoted = llobot.text.quote(lang, content, backtick_count=backtick_count)
            
            return f'<details>\n<summary>File: {delta.path}{flag_suffix}</summary>\n\n{quoted}\n\n</details>'

        def find(self, message: str) -> list[str]:
            return [match.group(0) for match in _DETECTION_REGEX.finditer(message)]

        def parse(self, formatted: str) -> DocumentDelta | None:
            match = _PARSING_RE.fullmatch(formatted.strip())
            if not match:
                return None

            path_str, flag_str, content = match.groups()
            path = Path(path_str.strip())
            
            flag_str = flag_str or ''
            flags = {n.strip() for n in flag_str.split(',')} if flag_str else set()

            new = 'new' in flags
            modified = 'modified' in flags
            removed = 'removed' in flags
            diff = 'diff' in flags
            moved_from_flag = next((n for n in flags if n.startswith('moved from')), None)
            moved_from = None
            if moved_from_flag:
                m = _MOVED_FROM_RE.fullmatch(moved_from_flag)
                if m:
                    moved_from = Path(m.group(1).strip())

            recognized_flags = {'new', 'modified', 'removed', 'diff'}
            if moved_from_flag:
                recognized_flags.add(moved_from_flag)

            invalid = bool(flags - recognized_flags)

            # Empty content should be ignored in exactly two cases: (1) removed or (2) moved from without modified
            if content == '' and (removed or (moved_from and not modified)):
                content = None
            else:
                content = llobot.text.normalize(content) if content else None

            return DocumentDelta(path, content, new=new, modified=modified, removed=removed, diff=diff, moved_from=moved_from, invalid=invalid)

    return HeaderEnvelopeFormatter()

@cache
def standard() -> EnvelopeFormatter:
    return header()

__all__ = [
    'EnvelopeFormatter',
    'header',
    'standard',
]

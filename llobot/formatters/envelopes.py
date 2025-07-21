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

# We have to be careful how we detect code blocks, because we have to ignore nested code blocks.
# The regex matches either a full block with header and code or a flag-only file listing without code block.
# It will also match bare code blocks without header, which will be later filtered out during parsing.
# By matching the entire block, finditer() will skip over nested blocks within the code.
_FULL_BLOCK_PART = r'(?:`[^`\n]+`(?: \([^\n]*\))?:\n\n)?(?:```[^`\n]*\n.*?^```|````[^`\n]*\n.*?^````|`````[^`\n]*\n.*?^`````)'
_FLAG_ONLY_PART = r'`[^`\n]+` \([^\n]+\)'
_DETECTION_REGEX = re.compile(f'^(?:(?:{_FULL_BLOCK_PART})|(?:{_FLAG_ONLY_PART}))$', re.MULTILINE | re.DOTALL)
_PARSING_FULL_RE = re.compile(r'`([^`\n]+)`(?: \(([^\n]*)\))?:\n\n```+[^`\n]*\n(.*)^```+', re.MULTILINE | re.DOTALL)
_PARSING_FLAG_ONLY_RE = re.compile(r'`([^`\n]+)` \((.+)\)')
_MOVED_FROM_RE = re.compile(r"moved from `([^`]+)`")

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
            if delta.moved_from: flags.append(f"moved from `{delta.moved_from}`")
            flag_str = ', '.join(flags)
            flag_suffix = f' ({flag_str})' if flag_str else ''

            if delta.content is None:
                return f'`{delta.path}`{flag_suffix}'

            lang = 'diff' if delta.diff else guesser(delta.path, delta.content)
            backtick_count = 4 if lang in quad_backticks else 3
            quoted = llobot.text.quote(lang, delta.content, backtick_count=backtick_count)
            return f'`{delta.path}`{flag_suffix}:\n\n{quoted}'

        def find(self, message: str) -> list[str]:
            return [match.group(0) for match in _DETECTION_REGEX.finditer(message)]

        def parse(self, formatted: str) -> DocumentDelta | None:
            full_match = _PARSING_FULL_RE.fullmatch(formatted.strip())
            flag_only_match = _PARSING_FLAG_ONLY_RE.fullmatch(formatted.strip())

            if full_match:
                path_str, flag_str, content = full_match.groups()
            elif flag_only_match:
                path_str, flag_str = flag_only_match.groups()
                content = None
            else:
                return None

            flag_str = flag_str or ''
            flags = {n.strip() for n in flag_str.split(',')} if flag_str else set()

            # Skip informative listings without attempting to parse anything else.
            if 'informative' in flags:
                return None

            path = Path(path_str)

            new = 'new' in flags
            modified = 'modified' in flags
            removed = 'removed' in flags
            diff = 'diff' in flags
            moved_from_flag = next((n for n in flags if n.startswith('moved from')), None)
            moved_from = None
            if moved_from_flag:
                m = _MOVED_FROM_RE.fullmatch(moved_from_flag)
                if m:
                    moved_from = Path(m.group(1))
            
            recognized_flags = {'new', 'modified', 'removed', 'diff'}
            if moved_from_flag:
                recognized_flags.add(moved_from_flag)
            
            invalid = bool(flags - recognized_flags)

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

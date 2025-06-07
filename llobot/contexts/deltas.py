from __future__ import annotations
from collections import deque
from llobot.chats import ChatBranch
from llobot.contexts import Context, ContextChunk
from llobot.contexts.examples import ExampleChunk
from llobot.contexts.documents import DocumentChunk
from llobot.contexts.deletions import DeletionChunk
import llobot.contexts

def common_prefix(left: Context | ChatBranch, right: Context | ChatBranch) -> Context:
    # If both are ChatBranch, delegate to ChatBranch's & operator
    if isinstance(left, ChatBranch) and isinstance(right, ChatBranch):
        return llobot.contexts.wrap(left & right)

    # If left is ChatBranch and right is Context, swap them
    if isinstance(left, ChatBranch) and isinstance(right, Context):
        left, right = right, left

    # Now left is Context and right is Context | ChatBranch
    prefix = []
    right = right.chat if isinstance(right, Context) else right
    offset = 0
    for chunk in left:
        length = len(chunk.chat)
        if offset + length > len(right):
            break
        # Force conversion to list, so that we don't compare chat metadata.
        if list(chunk.chat) != list(right[offset:offset+length]):
            break
        prefix.append(chunk)
        offset += length
    return llobot.contexts.compose(*prefix)

def take_while(context: Context, predicate: Callable[[ContextChunk], bool]) -> Context:
    prefix = []
    for chunk in context:
        if not predicate(chunk):
            break
        prefix.append(chunk)
    return llobot.contexts.compose(*prefix)

def take_until(context: Context, predicate: Callable[[ContextChunk], bool]) -> Context:
    return take_while(context, lambda chunk: not predicate(chunk))

def check_examples(context: Context, validation: Callable[[ChatBranch], bool]) -> Context:
    return take_until(context, lambda chunk: any(not validation(example) for example in chunk.examples))

def compatible_prefix(cache: Context, fresh: Context) -> Context:
    identical = cache & fresh
    fresh_examples = deque(chunk.chat for chunk in fresh if isinstance(chunk, ExampleChunk))
    def acceptable(chunk: ContextChunk) -> bool:
        # Documents and deletions are always acceptable.
        if isinstance(chunk, (DocumentChunk, DeletionChunk)):
            return True
        # Reject unrecognized chunks.
        if not isinstance(chunk, ExampleChunk):
            return False
        # If this condition holds, then either the cache contains examples while the fresh context doesn't
        # or the cache contains an example that is younger than all fresh examples.
        # Both cases are unlikely. If we encounter either one, it is safe to allow the example.
        if not fresh_examples:
            return True
        cache_timestamp = chunk.chat.metadata.time
        fresh_timestamp = fresh_examples[0].metadata.time
        # Timestamps should always be there.
        # If they are inexplicably missing, accepting the example is the safe option.
        if not cache_timestamp or not fresh_timestamp:
            return True
        # Allow cache example that is identical to the next fresh example.
        # Force conversion to list to ignore chat metadata.
        if list(chunk.chat) == list(fresh_examples[0]):
            fresh_examples.popleft()
            return True
        # Allow cache example that is older than the next fresh example,
        # because example order is preserved in that case.
        if cache_timestamp < fresh_timestamp:
            return True
        return False
    consistent = take_while(cache[len(identical):], acceptable)
    return identical + consistent

__all__ = [
    'common_prefix',
    'take_while',
    'take_until',
    'check_examples',
    'compatible_prefix',
]


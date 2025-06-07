from __future__ import annotations
from llobot.chats import ChatBranch
from llobot.contexts import Context, ContextChunk
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

__all__ = [
    'common_prefix',
    'take_while',
    'take_until',
]


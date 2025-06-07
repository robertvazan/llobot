from __future__ import annotations
from llobot.chats import ChatBranch
from llobot.contexts import Context
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
    for chunk in left.chunks:
        length = len(chunk.chat)
        if offset + length > len(right):
            break
        # Force conversion to list, so that we don't compare chat metadata.
        if list(chunk.chat) != list(right[offset:offset+length]):
            break
        prefix.append(chunk)
        offset += length
    return llobot.contexts.compose(*prefix)

def unique_suffix(left: Context, right: Context) -> tuple[Context, Context]:
    prefix = common_prefix(left, right)
    skip = len(prefix.chunks)
    left_suffix = llobot.contexts.compose(*left.chunks[skip:])
    right_suffix = llobot.contexts.compose(*right.chunks[skip:])
    return left_suffix, right_suffix

__all__ = [
    'common_prefix',
    'unique_suffix',
]


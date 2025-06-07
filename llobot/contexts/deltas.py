from __future__ import annotations
from llobot.chats import ChatBranch
from llobot.contexts import Context
import llobot.contexts

def common_prefix(left: Context, right: Context | ChatBranch) -> Context:
    prefix = []
    remaining = right.chat if isinstance(right, Context) else right
    for chunk in left.chunks:
        length = len(chunk.chat)
        if length > len(remaining):
            break
        # Force conversion to list, so that we don't compare chat metadata.
        if list(chunk.chat) != list(remaining[:length]):
            break
        prefix.append(chunk)
        remaining = remaining[length:]
    return llobot.contexts.compose(*prefix)

__all__ = [
    'common_prefix',
]


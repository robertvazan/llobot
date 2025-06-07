from __future__ import annotations
from collections import deque, Counter
from llobot.chats import ChatBranch
from llobot.knowledge import Knowledge
from llobot.contexts import Context, ContextChunk
from llobot.contexts.examples import ExampleChunk
from llobot.contexts.documents import DocumentChunk
from llobot.contexts.deletions import DeletionChunk
from llobot.formatters.knowledge import KnowledgeFormatter
from llobot.formatters.deletions import DeletionFormatter
import llobot.contexts
import llobot.knowledge.subsets
import llobot.knowledge.rankings
import llobot.formatters.knowledge
import llobot.formatters.deletions

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

# Find the longest prefix that does not contain incompatible chunks:
# unrecognized non-identical chunks or reordered examples.
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

# Find the longest prefix that can be constructed by safely reordering fresh context chunks.
# Same as above but no deletions are allowed and documents must be moved carefully,
# so that update/deletion chunks don't have to be appended to fix issues created by moves.
def shuffled_prefix(cache: Context, fresh: Context) -> Context:
    identical = cache & fresh
    fresh_examples = deque(chunk.chat for chunk in fresh if isinstance(chunk, ExampleChunk))
    fresh_documents = {chunk.chat.monolithic() for chunk in fresh if isinstance(chunk, DocumentChunk)}
    paths = Counter()
    for chunk in fresh[len(identical):]:
        for path in chunk.knowledge.keys():
            paths[path] += 1
    def acceptable(chunk: ContextChunk) -> bool:
        for path in chunk.knowledge.keys():
            paths[path] -= 1
        if isinstance(chunk, DocumentChunk):
            # Documents are only allowed if they are present in the fresh context.
            if chunk.chat.monolithic() not in fresh_documents:
                return False
            # Moving documents up in the context is only possible if there's no other chunk with the same document.
            # This can happen with examples that contain outdated version of the document.
            if any(paths[path] > 0 for path in chunk.knowledge.keys()):
                return False
            return True
        # Code for examples is the same as in compatible_prefix().
        if not isinstance(chunk, ExampleChunk):
            return False
        if not fresh_examples:
            return True
        cache_timestamp = chunk.chat.metadata.time
        fresh_timestamp = fresh_examples[0].metadata.time
        if not cache_timestamp or not fresh_timestamp:
            return True
        if list(chunk.chat) == list(fresh_examples[0]):
            fresh_examples.popleft()
            return True
        if cache_timestamp < fresh_timestamp:
            return True
        return False
    consistent = take_while(cache[len(identical):], acceptable)
    return identical + consistent

# Find chunks in fresh context that are still necessary following cache context.
def difference(cache: Context, fresh: Context) -> Context:
    knowledge = dict(cache.knowledge)
    examples = {example.monolithic() for example in cache.examples}
    changes = []
    for chunk in fresh:
        if isinstance(chunk, DeletionChunk):
            # Skip deletions of documents that do not exist anyway.
            if chunk.path not in knowledge:
                continue
        elif isinstance(chunk, DocumentChunk):
            # Skip documents that are already in prior knowledge.
            if chunk.path in knowledge and knowledge[chunk.path] == chunk.content:
                continue
        elif isinstance(chunk, ExampleChunk):
            # Skip examples that are already in the cache context.
            if chunk.chat.monolithic() in examples:
                continue
        else:
            # Include all chunks that are not document, deletion, nor example.
            pass
        changes.append(chunk)
        for path in chunk.deletions:
            knowledge.pop(path, None)
        for path, content in chunk.knowledge:
            knowledge[path] = content
    return llobot.contexts.compose(*changes)

def sync(
    context: Context,
    knowledge: Knowledge,
    *,
    update_formatter: KnowledgeFormatter = llobot.formatters.knowledge.updates(),
    deletion_formatter: DeletionFormatter = llobot.formatters.deletions.standard(),
) -> Context:
    context_knowledge = context.knowledge
    deletions = context_knowledge.keys() - knowledge.keys()
    updates = knowledge & llobot.knowledge.subsets.create(lambda path, content: path in context_knowledge and context_knowledge[path] != content)
    return llobot.contexts.compose(
        deletion_formatter(deletions),
        update_formatter(updates, llobot.knowledge.rankings.lexicographical(updates))
    )

__all__ = [
    'common_prefix',
    'take_while',
    'take_until',
    'check_examples',
    'compatible_prefix',
    'shuffled_prefix',
    'difference',
    'sync',
]


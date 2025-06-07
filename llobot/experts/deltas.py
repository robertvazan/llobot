from __future__ import annotations
from functools import lru_cache
from datetime import datetime
from collections import Counter
import logging
from cachetools import LRUCache
from llobot.chats import ChatBranch
from llobot.knowledge import Knowledge
from llobot.contexts import Context
from llobot.contexts.examples import ExampleChunk
from llobot.contexts.documents import DocumentChunk
from llobot.contexts.deletions import DeletionChunk
from llobot.formatters.knowledge import KnowledgeFormatter
from llobot.formatters.deletions import DeletionFormatter
from llobot.experts import Expert
from llobot.experts.requests import ExpertRequest
from llobot.experts.memory import ExpertMemory
from llobot.experts.wrappers import ExpertWrapper
import llobot.knowledge.subsets
import llobot.knowledge.rankings
import llobot.contexts
import llobot.contexts.deltas
import llobot.formatters.knowledge
import llobot.formatters.deletions
import llobot.experts.wrappers

_logger = logging.getLogger(__name__)

# How many combinations of models, experts, and scopes could the user be juggling at a time?
# Cached contexts could eventually grow up to 1MB each, but we have plenty of RAM,
# so let's optimize for cache hit rate with large number of cached contexts.
_cache = LRUCache(maxsize=128)

# Discard chunks with unrecoverable errors: modified examples and changes in unidentified chunks.
def _discard_inconsistent(cache: Context, fresh: Context, request: ExpertRequest) -> Context:
    identical = cache & fresh
    consistent = cache[len(identical):]
    consistent = llobot.contexts.deltas.take_while(consistent,
        lambda chunk: isinstance(chunk, (DocumentChunk, DeletionChunk, ExampleChunk)))
    consistent = llobot.contexts.deltas.check_examples(consistent,
        lambda example: not example.metadata.time or request.memory.has_example(request.scope, example.metadata.time))
    return identical + consistent

def _reorder_fresh(cache: Context, fresh: Context) -> tuple[Context, Context]:
    # Skip identical chunks.
    reordered = list(cache & fresh)
    # Reorder chunks whenever possible.
    remainder = fresh[len(reordered):]
    unused = {chunk.chat.monolithic() for chunk in remainder}
    paths = Counter()
    for chunk in remainder:
        for path in chunk.knowledge.keys():
            paths[path] += 1
    # Reordering is practical only if all chunks are unique, which is an assumption that is nearly always true.
    if len(unused) == len(remainder):
        for chunk in cache[len(reordered):]:
            # If the chunk is not in the fresh context, don't reorder it.
            monolithic = chunk.chat.monolithic()
            if monolithic not in unused:
                break
            for path in chunk.knowledge.keys():
                paths[path] -= 1
            if isinstance(chunk, ExampleChunk):
                # Moving examples up in the context does no harm even if they contain outdated documents.
                # This could cause a small amount of example reordering, but that's usually harmless.
                pass
            elif isinstance(chunk, DocumentChunk):
                # Moving documents up in the context is only possible if there's no other chunk with the same document.
                # This can happen with examples that contain outdated version of the document.
                if any(paths[path] > 0 for path in chunk.knowledge.keys()):
                    break
            else:
                # We cannot reorder unknown chunk types.
                break
            reordered.append(chunk)
            unused.remove(monolithic)
        remainder = llobot.contexts.compose(*[chunk for chunk in remainder if chunk.monolithic() in unused])
    return llobot.contexts.compose(*reordered), remainder

@lru_cache
def standard(*,
    update_trimmer: Trimmer = llobot.trimmers.eager(),
    update_formatter: KnowledgeFormatter = llobot.formatters.knowledge.updates(),
    deletion_formatter: DeletionFormatter = llobot.formatters.deletions.standard(),
    # Default share of the budget to dedicate to the change buffer is a bit controversial.
    # Dedicating 50% of the budget to the change buffer balances memory and compute overhead (it minimizes their product),
    # but even cloud models have limited context windows, which we don't want to waste on huge change buffer.
    # Cloud models cannot even utilize the large change buffer, because they come with very short-lived prompt cache.
    # On top of that, large change buffer means a lot of outdated information in the context, which confuses the model.
    # For these reasons, we will default to smaller change buffer, say 20% of the context window.
    # That should still be enough for several smaller documents or examples.
    buffer_share: float = 0.2,
) -> Expert:
    def stuff(expert: Expert, request: ExpertRequest) -> Context:
        if not request.cache.enabled:
            return expert(request)
        fresh_share = 1 - buffer_share
        fresh = (fresh_share * expert)(request)
        report = f"Delta prompt: {fresh.pretty_cost} fresh"
        # Even though we are including prompt cache, expert, and scope in the zone name, it might not be sufficiently unique.
        # If two models share the same prompt cache with wildly different context sizes, our context cache will be mostly ineffective.
        # That's however quite an unusual scenario and we currently don't want to waste time dealing with it.
        zone = request.cache.name + '/' + request.memory.zone_name(request.scope)
        # To support speculative operations like echo that query the expert without sending anything to the model,
        # we have to cache two contexts: one most recently proposed by the expert and one confirmed to be in model's prompt cache.
        cache1, cache2 = _cache.get(zone, (llobot.contexts.empty(), llobot.contexts.empty()))
        prompt_cache1 = request.cache.cached_context(cache1)
        prompt_cache2 = request.cache.cached_context(cache2)
        cache = prompt_cache1 if len(prompt_cache1) > len(prompt_cache2) else prompt_cache2
        if cache:
            report += f", {cache.pretty_cost} cached"
            consistent = _discard_inconsistent(cache, fresh, request)
            if len(consistent) != len(cache):
                report += f" -> {consistent.pretty_cost} consistent"
            # Go over the fresh prompt and include new or modified chunks.
            new_chunks = []
            cache_chats = {chunk.chat.monolithic() for chunk in consistent}
            consistent_knowledge = consistent.knowledge
            for chunk in fresh:
                if isinstance(chunk, DocumentChunk):
                    # Include document chunks that are new or differ from knowledge in consistent context.
                    if chunk.path not in consistent_knowledge or consistent_knowledge[chunk.path] != chunk.content:
                        new_chunks.append(chunk)
                elif chunk.chat.monolithic() not in cache_chats:
                    # Include all non-document chunks that are not in the consistent context.
                    new_chunks.append(chunk)
            new = llobot.contexts.compose(*new_chunks)
            if new:
                report += f" + {new.pretty_cost} new"
            delta = llobot.contexts.compose(consistent, new)
            # Delta context can still contain outdated documents, because:
            # - Cached context may include outdated documents that are absent from fresh context.
            # - Model responses in examples may contain outdated documents that have been modified since.
            # We will therefore compare delta context with fresh knowledge and inform the model about deletions and updates.
            fresh_knowledge = request.scope.project.knowledge(request.cutoff).transform(update_trimmer.trim_fully) if request.scope else Knowledge()
            delta_knowledge = delta.knowledge
            deletions = delta_knowledge.keys() - fresh_knowledge.keys()
            updates = fresh_knowledge & llobot.knowledge.subsets.create(lambda path, content: path in delta_knowledge and delta_knowledge[path] != content)
            modified = llobot.contexts.compose(
                deletion_formatter(deletions),
                update_formatter(updates, llobot.knowledge.rankings.lexicographical(updates)))
            if modified:
                report += f" + {modified.pretty_cost} modified"
            proposal = llobot.contexts.compose(delta, modified)
            report += f" = {proposal.pretty_cost} incremental"
            # We want to discard the proposal not only when it is over budget, but also when it grows too big relative to fresh context,
            # because we don't want disproportionately large change buffer when the underlying expert does not need the whole context window.
            if proposal.cost > request.budget or fresh.cost < fresh_share * proposal.cost:
                # If the incremental context does not fit, rewrite the whole context from scratch using the fresh context.
                # We could opt to rewrite only some suffix of the context that contains most "bubbles" of outdated content, but that has several issues:
                #
                # - Document updates cannot be considered bubbles unless the original document is a bubble too, which complicates calculation of optimal suffix.
                # - Suffix choice policies are either suboptimal (shortest, longest) or they could choose suffix that is too short (shortest, highest bubble share).
                # - If the suffix is too short, we could loop to remove more suffixes, but that can introduce costly quadratic loops.
                # - And even if all these problems are addressed, there's the problem of context documents reaching wide range of ages over time.
                #
                # Just rewriting the whole context is simple, compute-efficient, ensures consistent maximum document age, and it's predictable.
                # Its only problem is that it suffers from occasional full context refresh, but that's always a problem and there are incremental solutions to that.
                # We could however reconsider bubble popping in the future as an optional extra to boost efficiency rather than as a primary compaction mechanism.
                report += " (overflow)"
                # We will at least try to reorder chunks to reuse as much of the cache as possible.
                reordered, new = _reorder_fresh(cache, fresh)
                if reordered:
                    report += f"; {reordered.pretty_cost} reordered + {new.pretty_cost} new"
                proposal = llobot.contexts.compose(reordered, new)
        else:
            report += " (no cache)"
            proposal = fresh
        report += f" @ {zone} ({proposal.pretty_structure()})"
        if (cache, proposal) != (cache1, cache2):
            _logger.info(report)
        _cache[zone] = (cache, proposal)
        return proposal
    return llobot.experts.wrappers.stateless(stuff)

__all__ = [
    'standard',
]


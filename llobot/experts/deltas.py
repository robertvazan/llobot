from __future__ import annotations
from functools import lru_cache
from datetime import datetime
from collections import OrderedDict
import logging
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
import llobot.formatters.knowledge
import llobot.formatters.deletions
import llobot.experts.wrappers

_logger = logging.getLogger(__name__)

class _SimpleLruCache:
    _capacity: int
    _cache: OrderedDict
    _fallback: Any

    # How many combinations of models, experts, and scopes could the user be juggling at a time?
    # Cached contexts could eventually grow up to 1MB each, but we have plenty of RAM,
    # so let's optimize for cache hit rate with large number of cached contexts.
    def __init__(self, fallback: Any, capacity: int = 128):
        self._capacity = capacity
        self._cache = OrderedDict()
        self._fallback = fallback

    def __getitem__(self, zone: str) -> Any:
        if zone not in self._cache:
            return self._fallback
        value = self._cache.pop(zone)
        # Move it to the end.
        self._cache[zone] = value
        return value

    def __setitem__(self, zone: str, value: Any):
        if zone in self._cache:
            self._cache.pop(zone)
        elif len(self._cache) >= self._capacity:
            self.cache.popitem(last=False)
        self._cache[zone] = value

_cache = _SimpleLruCache((llobot.contexts.empty(), llobot.contexts.empty()))

# Discard chunks with unrecoverable errors: modified examples and changes in unidentified chunks.
def _discard_inconsistent(cache: Context, fresh: Context, request: ExpertRequest) -> Context:
    # Preserve identical context prefix.
    prefix = []
    for chunk, fresh_chunk in zip(cache.chunks, fresh.chunks):
        # Force conversion to a list to compare only messages, not metadata.
        if list(chunk.chat) != list(fresh_chunk.chat):
            break
        prefix.append(chunk)
    for chunk in cache.chunks[len(prefix):]:
        if isinstance(chunk, ExampleChunk):
            # Outdated example that has been deleted/replaced.
            if any(example.metadata.time and not request.memory.has_example(request.scope, example.metadata.time) for example in chunk.examples):
                break
        elif not isinstance(chunk, (DocumentChunk, DeletionChunk)):
            break
        prefix.append(chunk)
    return llobot.contexts.compose(*prefix)

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
        cache1, cache2 = _cache[zone]
        prompt_cache1 = request.cache.cached_context(cache1)
        prompt_cache2 = request.cache.cached_context(cache2)
        cache = prompt_cache1 if len(prompt_cache1.chunks) > len(prompt_cache2.chunks) else prompt_cache2
        if cache:
            report += f", {cache.pretty_cost} cached"
            consistent = _discard_inconsistent(cache, fresh, request)
            if len(consistent.chunks) != len(cache.chunks):
                report += f" -> {consistent.pretty_cost} consistent"
            # Go over the fresh prompt and include new or modified chunks.
            new_chunks = []
            cache_chats = {chunk.chat.monolithic() for chunk in consistent.chunks}
            consistent_knowledge = consistent.knowledge
            for chunk in fresh.chunks:
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
        else:
            report += " (no cache)"
            proposal = fresh
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


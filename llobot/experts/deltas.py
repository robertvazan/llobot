from __future__ import annotations
from functools import lru_cache
from datetime import datetime
from collections import Counter
import logging
from cachetools import LRUCache
from llobot.chats import ChatBranch
from llobot.knowledge import Knowledge
from llobot.contexts import Context
from llobot.formatters.knowledge import KnowledgeFormatter
from llobot.formatters.deletions import DeletionFormatter
from llobot.experts import Expert
from llobot.experts.requests import ExpertRequest
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

@lru_cache
def standard(*,
    update_trimmer: Trimmer = llobot.trimmers.boilerplate(),
    update_formatter: KnowledgeFormatter = llobot.formatters.knowledge.updates(),
    deletion_formatter: DeletionFormatter = llobot.formatters.deletions.standard(),
    # Change buffer budget as a fraction of the main context budget.
    # Default size of the change buffer is a bit controversial.
    # Dedicating 50% of the context to the change buffer balances memory and compute overhead (it minimizes their product),
    # but even cloud models have limited context windows, which we don't want to waste on huge change buffer.
    # Cloud models cannot even utilize the large change buffer, because they come with very short-lived prompt cache.
    # On top of that, large change buffer means a lot of outdated information in the context, which confuses the model.
    # For these reasons, we will default to smaller change buffer, say 20% on top of the fresh context budget.
    # That should still be enough for several smaller documents or examples.
    overhead: float = 0.2,
) -> Expert:
    def stuff(expert: Expert, request: ExpertRequest) -> Context:
        if not request.cache.enabled:
            return expert(request)
        fresh = expert(request)
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
            consistent = llobot.contexts.deltas.compatible_prefix(cache, fresh)
            consistent = llobot.contexts.deltas.check_examples(consistent,
                lambda example: not example.metadata.time or request.memory.has_example(request.scope, example.metadata.time))
            if len(consistent) != len(cache):
                report += f" -> {consistent.pretty_cost} consistent"
            new = llobot.contexts.deltas.difference(consistent, fresh)
            if new:
                report += f" + {new.pretty_cost} new"
            presync = llobot.contexts.compose(consistent, new)
            # Pre-sync context can still contain outdated documents, because:
            # - Cached context may include outdated documents that are absent from fresh context.
            # - Model responses in examples may contain outdated documents that have been modified since.
            # We will therefore sync the pre-sync context with fresh knowledge.
            fresh_knowledge = request.scope.project.knowledge(request.cutoff).transform(update_trimmer.trim_fully) if request.scope else Knowledge()
            sync = llobot.contexts.deltas.sync(presync, fresh_knowledge, update_formatter=update_formatter, deletion_formatter=deletion_formatter)
            if sync:
                report += f" + {sync.pretty_cost} sync"
            proposal = llobot.contexts.compose(presync, sync)
            report += f" = {proposal.pretty_cost} incremental"
            # We want to discard the proposal not only when it is over budget, but also when it grows too big relative to fresh context,
            # because we don't want disproportionately large change buffer when the underlying expert does not need the whole context window.
            if proposal.cost > (1 + overhead) * fresh.cost:
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
                reordered = llobot.contexts.deltas.shuffled_prefix(cache, fresh)
                new = llobot.contexts.deltas.difference(reordered, fresh)
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


from __future__ import annotations
from functools import cache
from llobot.chats import ChatBranch
from llobot.contexts import Context
import llobot.text

# Prompt cache for a single model where model identity includes model name and cache-impacting model options.
# In theory, some LLM APIs could let us query the cache directly, but in practice, this is always a client-side prediction of cache state.
# Instance of this class are usually model-specific views of the underlying prompt storage shared by several models.
class PromptCache:
    # Unique identifier of the model this cache is serving, including endpoint, name, and select options.
    # This may be less informative than model reference, because not all model options impact prompt cache.
    # Model identification helps bots associate additional information with every cache.
    @property
    def name(self) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        return self.name

    # Indicates whether there is any prompt cache at all. Bots can use this information to disable cache-related functionality.
    @property
    def enabled(self) -> bool:
        return True

    # Returns prompt prefix that is most likely stored in the prompt cache.
    # We never have reliable prompt cache information, so this is just a best effort estimate.
    def cached(self, prompt: ChatBranch) -> ChatBranch:
        return ChatBranch()

    def cached_context(self, prompt: Context) -> Context:
        return prompt & self.cached(prompt.chat)

    # Pre-inference cache hint called before sending the prompt to the model.
    # In some types of cache (like last prompt cache), merely issuing inference request alters the cache.
    # This method purges cache content that will be invalidated by the next inference.
    # Some caches (LRU, for example) don't need to implement this operation at all.
    def trim(self, prompt: ChatBranch):
        pass

    # Post-inference cache hint called after receiving response from the model.
    # Prompt passed in here normally includes model's response.
    def write(self, prompt: ChatBranch):
        pass

# Storage area shared among several models, usually associated with an endpoint.
# Methods are similar to prompt cache above, but they also accept model identity (name and select options).
class PromptStorage:
    # Unique identifier of the storage area, usually derived from endpoint name.
    @property
    def name(self) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        return self.name

    @property
    def enabled(self) -> bool:
        return True

    def cached(self, prompt: ChatBranch, model: str) -> ChatBranch:
        return ChatBranch()

    def trim(self, prompt: ChatBranch, model: str):
        pass

    def write(self, prompt: ChatBranch, model: str):
        pass

    # Caching hint that indicates the whole cache storage has been lost, for example due to inference engine restart.
    def purge(self):
        pass

    def __getitem__(self, model: str) -> PromptCache:
        storage = self
        class PromptStorageCache(PromptCache):
            @property
            def name(self) -> str:
                return f'{storage.name}/{model}'
            @property
            def enabled(self) -> bool:
                return storage.enabled
            def cached(self, prompt: ChatBranch) -> ChatBranch:
                return storage.cached(prompt, model)
            def trim(self, prompt: ChatBranch):
                storage.trim(prompt, model)
            def write(self, prompt: ChatBranch):
                storage.write(prompt, model)
        return PromptStorageCache()

@cache
def disabled() -> PromptStorage:
    class DisabledPromptStorage(PromptStorage):
        @property
        def name(self) -> str:
            return 'disabled'
        @property
        def enabled(self) -> bool:
            return False
    return DisabledPromptStorage()

__all__ = [
    'PromptCache',
    'PromptStorage',
    'disabled',
]


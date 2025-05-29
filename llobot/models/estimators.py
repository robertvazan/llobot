from __future__ import annotations
from functools import cache, lru_cache
from pathlib import Path
import logging
from llobot.fs.zones import Zoning
import llobot.fs.zones
from llobot.models.stats import ModelStats
import llobot.models.stats.json

_logger = logging.getLogger(__name__)

# We cannot really assume any content length in general. We have to fall back to the worst case of one-character tokens.
# Even that could be optimistic with very extreme content consisting of rare unicode characters, but we don't have to care about those cases.
PESSIMISTIC_TOKEN_LENGTH: float = 1.0

# Empirically observed 4+ characters per token for English text.
OPTIMISTIC_TOKEN_LENGTH: float = 4.0

# All models are tokenized. Even byte models skip most bytes. Tokenization may be unknown (cloud models) or expensive (byte/chunk models).
# Context is always limited. Even models with infinite context (recursive, compressed) have practical limit on how many tokens they can process.
# Models always measure context window in tokens rather than characters. We therefore need empirical estimators for token length.
class TokenLengthEstimator:
    def calibrated(self, zone: str) -> bool:
        return True

    def update(self, zone: str, stats: ModelStats):
        pass

    def estimate(self, zone: str) -> float:
        return OPTIMISTIC_TOKEN_LENGTH

@cache
def constant(length: float) -> TokenLengthEstimator:
    class ConstantEstimator(TokenLengthEstimator):
        def estimate(self, zone: str) -> float:
            return length
    return ConstantEstimator()

@cache
def pessimistic() -> TokenLengthEstimator:
    return constant(PESSIMISTIC_TOKEN_LENGTH)

@cache
def optimistic() -> TokenLengthEstimator:
    return constant(OPTIMISTIC_TOKEN_LENGTH)

@lru_cache
def latest(
    location: Zoning | Path | str = llobot.fs.cache()/'llobot/stats/*.json',
    # We cannot afford to be optimistic with estimates even along the scope hierarchy.
    # Since we are happy to extrapolate to 3-5x larger token count anyway, initialization of token estimator
    # can be done in one turn by submitting prompt built using the pessimistic estimator.
    fallback: TokenLengthEstimator = pessimistic()
) -> TokenLengthEstimator:
    location = llobot.fs.zones.coerce(location)
    class LatestEstimator(TokenLengthEstimator):
        def calibrated(self, zone: str) -> bool:
            return location[zone].exists()
        def update(self, zone: str, stats: ModelStats):
            path = location[zone]
            llobot.models.stats.json.save(path, stats)
            fallback.update(zone, stats)
        def estimate(self, zone: str) -> float:
            path = location[zone]
            if path.exists():
                length = llobot.models.stats.json.load(path).token_length
                if length:
                    # Do not let token length estimates drop below 1.
                    # This can happen when the stats include system prompt that we do not see.
                    return max(length, 1)
            return fallback.estimate(zone)
    return LatestEstimator()

@lru_cache
def stable(underlying: TokenLengthEstimator, deadband: float = 0.1) -> TokenLengthEstimator:
    cache = {}
    class StableEstimator(TokenLengthEstimator):
        def calibrated(self, zone: str) -> bool:
            return underlying.calibrated(zone)
        def update(self, zone: str, stats: ModelStats):
            underlying.update(zone, stats)
            # Update is a good time to clear cache entries without causing too much disruption.
            # But it is not enough for stability. Bots have to lock token length along with knowledge.
            stored = cache.get(zone)
            if stored and abs(underlying.estimate(zone) / stored - 1) > deadband:
                del cache[zone]
        def estimate(self, zone: str) -> float:
            # Underlying estimator is unlikely to change without update() call, so no need to ever clear cache here.
            if zone not in cache:
                cache[zone] = underlying.estimate(zone)
            return cache[zone]
    return StableEstimator()

@lru_cache
def log_changes(underlying: TokenLengthEstimator) -> TokenLengthEstimator:
    reported = {}
    class LoggingEstimator(TokenLengthEstimator):
        def calibrated(self, zone: str) -> bool:
            return underlying.calibrated(zone)
        def update(self, zone: str, stats: ModelStats):
            underlying.update(zone, stats)
        def estimate(self, zone: str) -> float:
            length = underlying.estimate(zone)
            if length != reported.get(zone):
                reported[zone] = length
                _logger.info(f'Token length: {length:.1f} @ {zone}')
            return length
    return LoggingEstimator()

@cache
def standard() -> TokenLengthEstimator:
    return log_changes(stable(latest()))

def prefixed(prefix: str, underlying: TokenLengthEstimator) -> TokenLengthEstimator:
    class PrefixedEstimator(TokenLengthEstimator):
        def calibrated(self, zone: str) -> bool:
            return underlying.calibrated(prefix + zone)
        def update(self, zone: str, stats: ModelStats):
            underlying.update(prefix + zone, stats)
        def estimate(self, zone: str) -> float:
            return underlying.estimate(prefix + zone)
    return PrefixedEstimator()

__all__ = [
    'PESSIMISTIC_TOKEN_LENGTH',
    'OPTIMISTIC_TOKEN_LENGTH',
    'TokenLengthEstimator',
    'constant',
    'pessimistic',
    'optimistic',
    'latest',
    'stable',
    'standard',
    'prefixed',
]


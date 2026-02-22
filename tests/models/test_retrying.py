import pytest
import time
from typing import Iterator
from unittest.mock import patch
from llobot.models.retrying import RetryingModel
from llobot.models import Model
from llobot.chats.intent import ChatIntent
from llobot.chats.stream import ChatStream
from llobot.chats.thread import ChatThread
from llobot.utils.values import ValueTypeMixin

class FlakyModel(Model, ValueTypeMixin):
    def __init__(self, failures: int, fail_during_stream: bool = False):
        self.failures = failures
        self.fail_during_stream = fail_during_stream
        self.attempts = 0
        self._name = "flaky"

    @property
    def name(self) -> str: return self._name

    @property
    def identifier(self) -> str: return "flaky/model"

    def generate(self, prompt: ChatThread) -> ChatStream:
        self.attempts += 1

        def _stream() -> Iterator[str | ChatIntent]:
            if self.attempts <= self.failures:
                if self.fail_during_stream:
                    yield ChatIntent.RESPONSE
                    yield "Partial"
                    raise RuntimeError("Stream failed")
                else:
                    raise RuntimeError("Immediate failure")

            yield ChatIntent.RESPONSE
            yield "Success"

        return _stream()

def test_retrying_success_first_try():
    model = FlakyModel(failures=0)
    # Use small delay for test speed
    retrying = RetryingModel(model, delays=[0.001])

    stream = retrying.generate(ChatThread())
    result = list(stream)

    assert result == [ChatIntent.RESPONSE, "Success"]
    assert model.attempts == 1

def test_retrying_success_after_failure():
    model = FlakyModel(failures=2)
    retrying = RetryingModel(model, delays=[0.001, 0.001, 0.001])

    stream = retrying.generate(ChatThread())
    result = list(stream)

    assert result == [ChatIntent.RESPONSE, "Success"]
    assert model.attempts == 3 # 2 failures + 1 success

def test_retrying_stream_failure_buffering():
    # Test that partial output from failed attempts is discarded
    model = FlakyModel(failures=1, fail_during_stream=True)
    retrying = RetryingModel(model, delays=[0.001])

    stream = retrying.generate(ChatThread())
    result = list(stream)

    # Should only contain the successful result, no "Partial"
    assert result == [ChatIntent.RESPONSE, "Success"]
    assert model.attempts == 2

def test_retrying_exhaustion():
    model = FlakyModel(failures=10)
    retrying = RetryingModel(model, delays=[0.001])

    stream = retrying.generate(ChatThread())

    # Should raise the exception from the final attempt
    with pytest.raises(RuntimeError):
        list(stream)

    assert model.attempts == 2 # 1 retry + 1 final attempt

def test_retrying_value_semantics():
    model1 = FlakyModel(failures=0)
    model2 = FlakyModel(failures=0)

    r1 = RetryingModel(model1, delays=[1, 2])
    r2 = RetryingModel(model1, delays=[1, 2])
    r3 = RetryingModel(model2, delays=[1, 2])
    r4 = RetryingModel(model1, delays=[1])

    assert r1 == r2
    assert hash(r1) == hash(r2)
    assert r1 == r3 # Value equality based on fields
    assert r1 != r4

@patch('time.sleep')
def test_retrying_delays(mock_sleep):
    model = FlakyModel(failures=3)
    delays = [10, 20, 30]
    retrying = RetryingModel(model, delays=delays)

    list(retrying.generate(ChatThread()))

    assert mock_sleep.call_count == 3
    mock_sleep.assert_any_call(10)
    mock_sleep.assert_any_call(20)
    mock_sleep.assert_any_call(30)

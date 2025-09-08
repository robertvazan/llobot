import pytest
from llobot.environments import Environment
from llobot.environments.commands import CommandsEnv
from llobot.commands import Step, Command
from llobot.commands.chain import StepChain

class MockStep(Step):
    def __init__(self):
        self.process_called = False

    def process(self, env: Environment):
        self.process_called = True

class MockCommand(Command):
    def __init__(self, texts_to_handle: list[str] | None = None):
        self.texts_to_handle = set(texts_to_handle or [])
        self.process_called = False

    def handle(self, text: str, env: Environment) -> bool:
        return text in self.texts_to_handle

    def process(self, env: Environment):
        super().process(env)
        self.process_called = True

def test_step_chain_empty():
    """Tests that an empty StepChain does nothing."""
    chain = StepChain()
    env = Environment()
    chain.process(env) # Should not raise

def test_step_chain_calls_all():
    """Tests that StepChain calls process on all its steps."""
    step1 = MockStep()
    cmd1 = MockCommand()
    step2 = MockStep()
    chain = StepChain(step1, cmd1, step2)
    env = Environment()
    chain.process(env)
    assert step1.process_called
    assert cmd1.process_called
    assert step2.process_called

def test_step_chain_integration():
    """Tests a more realistic scenario with command consumption."""
    class ConsumingMockCommand(Command):
        def __init__(self, texts_to_handle: list[str]):
            self.texts_to_handle = texts_to_handle

        def handle(self, text: str, env: Environment) -> bool:
            return text in self.texts_to_handle

    cmd1 = ConsumingMockCommand(["cmd1", "cmd2"])
    cmd2 = ConsumingMockCommand(["cmd3"])
    step = MockStep()

    chain = StepChain(cmd1, cmd2, step)
    env = Environment()
    queue = env[CommandsEnv]
    queue.add(["cmd1", "cmd2", "cmd3", "cmd4"])

    chain.process(env)

    # cmd1 should consume cmd1 and cmd2.
    # cmd2 should consume cmd3.
    # cmd4 should remain.
    assert queue.get() == ["cmd4"]
    assert step.process_called

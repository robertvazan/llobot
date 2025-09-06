from llobot.commands.custom import CustomStep
from llobot.environments import Environment

def test_custom_step():
    called = False

    def my_action(env: Environment):
        nonlocal called
        called = True
        assert isinstance(env, Environment)

    step = CustomStep(my_action)
    env = Environment()
    step.process(env)
    assert called

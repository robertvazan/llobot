from llobot.environments.prompt import PromptEnv

def test_prompt_env():
    env = PromptEnv()
    assert env.get() == ''
    assert not env.is_last

    env.set('hello')
    assert env.get() == 'hello'
    assert not env.is_last

    env.mark_last()
    assert env.get() == 'hello'
    assert env.is_last

    env.set('world')
    assert env.get() == 'world'
    assert env.is_last

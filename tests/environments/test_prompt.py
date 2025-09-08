from llobot.environments.prompt import PromptEnv

def test_prompt_env():
    env = PromptEnv()
    assert env.get() == ''
    env.set('hello')
    assert env.get() == 'hello'
    env.set('world')
    assert env.get() == 'world'

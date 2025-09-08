from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage
from llobot.environments.status import StatusEnv

def test_status_env():
    env = StatusEnv()
    assert not env.populated
    assert env.content() == ''
    assert env.message() is None
    assert list(env.stream()) == []

    env.append('First part.')
    assert env.populated
    assert env.content() == 'First part.'
    assert env.message() == ChatMessage(ChatIntent.RESPONSE, 'First part.')
    stream_content = list(env.stream())
    assert len(stream_content) == 2
    assert stream_content[0] == ChatIntent.RESPONSE
    assert stream_content[1] == 'First part.'

    env.append(None)
    env.append('')
    assert env.content() == 'First part.'

    env.append('Second part.')
    assert env.content() == 'First part.\n\nSecond part.'
    assert env.message() == ChatMessage(ChatIntent.RESPONSE, 'First part.\n\nSecond part.')

from llobot.environments.context import ContextEnv
from llobot.chats.messages import ChatMessage
from llobot.chats.intents import ChatIntent
from llobot.chats.branches import ChatBranch

def test_context_env():
    env = ContextEnv()
    assert not env.populated
    assert not env.build()

    msg1 = ChatMessage(ChatIntent.PROMPT, "Hello")
    env.add(msg1)
    assert env.populated
    assert len(env.build()) == 1
    assert env.build()[0] == msg1

    msg2 = ChatMessage(ChatIntent.RESPONSE, "Hi")
    branch = ChatBranch([msg2])
    env.add(branch)
    assert len(env.build()) == 2
    assert env.build()[1] == msg2

    built = env.build()
    assert isinstance(built, ChatBranch)
    assert len(built) == 2
    assert built[0] == msg1
    assert built[1] == msg2

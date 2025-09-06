from llobot.environments.context import ContextEnv
from llobot.chats.messages import ChatMessage
from llobot.chats.intents import ChatIntent
from llobot.chats.branches import ChatBranch

def test_context_env():
    env = ContextEnv()
    assert not env.messages
    assert env.cost == 0

    msg1 = ChatMessage(ChatIntent.PROMPT, "Hello")
    env.add(msg1)
    assert len(env.messages) == 1
    assert env.messages[0] == msg1
    assert env.cost == msg1.cost

    msg2 = ChatMessage(ChatIntent.RESPONSE, "Hi")
    branch = ChatBranch([msg2])
    env.add(branch)
    assert len(env.messages) == 2
    assert env.messages[1] == msg2
    assert env.cost == msg1.cost + msg2.cost

    built = env.build()
    assert isinstance(built, ChatBranch)
    assert len(built) == 2
    assert built[0] == msg1
    assert built[1] == msg2

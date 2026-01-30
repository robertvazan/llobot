from unittest.mock import patch
from llobot.chats.thread import ChatThread
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.crammers.example.greedy import GreedyExampleCrammer
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.memory import MemoryEnv
from llobot.memories.examples import ExampleMemory

def create_env(examples):
    env = Environment()
    memory = ExampleMemory()
    env[MemoryEnv].configure(memory)
    return env

# Helper to mock recent examples on the memory instance in the env
def mock_recent(env, examples):
    memory = env[MemoryEnv].examples
    return patch.object(memory, 'recent', return_value=examples)

def test_cram_empty():
    """Tests cramming with no examples."""
    crammer = GreedyExampleCrammer(budget=1000)
    env = create_env([])
    with mock_recent(env, []):
        crammer.cram(env)
    assert not env[ContextEnv].build()

def test_cram_no_budget():
    """Tests cramming with zero budget."""
    ex1 = ChatThread([ChatMessage(ChatIntent.EXAMPLE_PROMPT, "p1"), ChatMessage(ChatIntent.EXAMPLE_RESPONSE, "r1")])
    crammer = GreedyExampleCrammer(budget=0)
    env = create_env([ex1])
    with mock_recent(env, [ex1]):
        crammer.cram(env)
    assert not env[ContextEnv].build()

def test_cram_fits():
    """Tests cramming examples that all fit in the budget."""
    ex1 = ChatThread([ChatMessage(ChatIntent.EXAMPLE_PROMPT, "p1"), ChatMessage(ChatIntent.EXAMPLE_RESPONSE, "r1")])
    ex2 = ChatThread([ChatMessage(ChatIntent.EXAMPLE_PROMPT, "p2"), ChatMessage(ChatIntent.EXAMPLE_RESPONSE, "r2")])
    crammer = GreedyExampleCrammer(budget=1000)
    env = create_env([ex2, ex1]) # recent first
    with mock_recent(env, [ex2, ex1]):
        crammer.cram(env)
    assert env[ContextEnv].build().messages == ex1.messages + ex2.messages

def test_cram_budget_limit():
    """Tests that cramming stops when budget is exceeded."""
    ex1 = ChatThread([ChatMessage(ChatIntent.EXAMPLE_PROMPT, "prompt one"), ChatMessage(ChatIntent.EXAMPLE_RESPONSE, "response one")])
    ex2 = ChatThread([ChatMessage(ChatIntent.EXAMPLE_PROMPT, "prompt two"), ChatMessage(ChatIntent.EXAMPLE_RESPONSE, "response two")])
    # ex1 and ex2 have the same cost
    assert ex1.cost == ex2.cost

    crammer = GreedyExampleCrammer(budget=ex1.cost + 5)
    env = create_env([ex2, ex1]) # Enough for one, not two
    with mock_recent(env, [ex2, ex1]):
        crammer.cram(env)
    assert env[ContextEnv].build().messages == ex2.messages

def test_cram_deduplication():
    """Tests that examples with the same prompt are deduplicated, keeping the most recent."""
    ex1 = ChatThread([ChatMessage(ChatIntent.EXAMPLE_PROMPT, "p1"), ChatMessage(ChatIntent.EXAMPLE_RESPONSE, "r1 old")])
    ex2 = ChatThread([ChatMessage(ChatIntent.EXAMPLE_PROMPT, "p1"), ChatMessage(ChatIntent.EXAMPLE_RESPONSE, "r1 new")]) # More recent
    ex3 = ChatThread([ChatMessage(ChatIntent.EXAMPLE_PROMPT, "p2"), ChatMessage(ChatIntent.EXAMPLE_RESPONSE, "r2")])
    crammer = GreedyExampleCrammer(budget=1000)
    env = create_env([ex2, ex1, ex3]) # ex2 is more recent for p1
    with mock_recent(env, [ex2, ex1, ex3]):
        crammer.cram(env)
    assert env[ContextEnv].build().messages == ex3.messages + ex2.messages

def test_seen_prompts_updated_on_skip():
    """Tests that a prompt is marked 'seen' even if the example is too large."""
    ex_new_long = ChatThread([ChatMessage(ChatIntent.EXAMPLE_PROMPT, "p1"), ChatMessage(ChatIntent.EXAMPLE_RESPONSE, "r1 new long content")])
    ex_old_short = ChatThread([ChatMessage(ChatIntent.EXAMPLE_PROMPT, "p1"), ChatMessage(ChatIntent.EXAMPLE_RESPONSE, "r1 old short")])
    crammer = GreedyExampleCrammer(budget=ex_old_short.cost + 5)
    env = create_env([ex_new_long, ex_old_short]) # Enough for short, not for long

    # ex_new_long is more recent, but doesn't fit. ex_old_short should not be chosen.
    with mock_recent(env, [ex_new_long, ex_old_short]):
        crammer.cram(env)
    assert not env[ContextEnv].build()

from llobot.chats.thread import ChatThread
from llobot.chats.builder import ChatBuilder
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.crammers.example.greedy import GreedyExampleCrammer

def test_cram_empty():
    """Tests cramming with no examples."""
    crammer = GreedyExampleCrammer()
    builder = ChatBuilder()
    builder.budget = 1000
    added = crammer.cram(builder, [])
    assert not added
    assert not builder.build()

def test_cram_no_budget():
    """Tests cramming with zero budget."""
    ex1 = ChatThread([ChatMessage(ChatIntent.EXAMPLE_PROMPT, "p1"), ChatMessage(ChatIntent.EXAMPLE_RESPONSE, "r1")])
    crammer = GreedyExampleCrammer()
    builder = ChatBuilder()
    builder.budget = 0
    added = crammer.cram(builder, [ex1])
    assert not added
    assert not builder.build()

def test_cram_fits():
    """Tests cramming examples that all fit in the budget."""
    ex1 = ChatThread([ChatMessage(ChatIntent.EXAMPLE_PROMPT, "p1"), ChatMessage(ChatIntent.EXAMPLE_RESPONSE, "r1")])
    ex2 = ChatThread([ChatMessage(ChatIntent.EXAMPLE_PROMPT, "p2"), ChatMessage(ChatIntent.EXAMPLE_RESPONSE, "r2")])
    crammer = GreedyExampleCrammer()
    builder = ChatBuilder()
    builder.budget = 1000
    added = crammer.cram(builder, [ex2, ex1]) # recent first
    assert added == [ex1, ex2]
    assert builder.build().messages == ex1.messages + ex2.messages

def test_cram_budget_limit():
    """Tests that cramming stops when budget is exceeded."""
    ex1 = ChatThread([ChatMessage(ChatIntent.EXAMPLE_PROMPT, "prompt one"), ChatMessage(ChatIntent.EXAMPLE_RESPONSE, "response one")])
    ex2 = ChatThread([ChatMessage(ChatIntent.EXAMPLE_PROMPT, "prompt two"), ChatMessage(ChatIntent.EXAMPLE_RESPONSE, "response two")])
    # ex1 and ex2 have the same cost
    assert ex1.cost == ex2.cost

    crammer = GreedyExampleCrammer()
    builder = ChatBuilder()
    builder.budget = ex1.cost + 5 # Enough for one, not two
    added = crammer.cram(builder, [ex2, ex1]) # ex2 is more recent
    assert added == [ex2]
    assert builder.build().messages == ex2.messages

def test_cram_deduplication():
    """Tests that examples with the same prompt are deduplicated, keeping the most recent."""
    ex1 = ChatThread([ChatMessage(ChatIntent.EXAMPLE_PROMPT, "p1"), ChatMessage(ChatIntent.EXAMPLE_RESPONSE, "r1 old")])
    ex2 = ChatThread([ChatMessage(ChatIntent.EXAMPLE_PROMPT, "p1"), ChatMessage(ChatIntent.EXAMPLE_RESPONSE, "r1 new")]) # More recent
    ex3 = ChatThread([ChatMessage(ChatIntent.EXAMPLE_PROMPT, "p2"), ChatMessage(ChatIntent.EXAMPLE_RESPONSE, "r2")])
    crammer = GreedyExampleCrammer()
    builder = ChatBuilder()
    builder.budget = 1000
    added = crammer.cram(builder, [ex2, ex1, ex3]) # ex2 is more recent for p1
    assert added == [ex3, ex2]
    assert builder.build().messages == ex3.messages + ex2.messages

def test_seen_prompts_updated_on_skip():
    """Tests that a prompt is marked 'seen' even if the example is too large."""
    ex_new_long = ChatThread([ChatMessage(ChatIntent.EXAMPLE_PROMPT, "p1"), ChatMessage(ChatIntent.EXAMPLE_RESPONSE, "r1 new long content")])
    ex_old_short = ChatThread([ChatMessage(ChatIntent.EXAMPLE_PROMPT, "p1"), ChatMessage(ChatIntent.EXAMPLE_RESPONSE, "r1 old short")])
    crammer = GreedyExampleCrammer()
    builder = ChatBuilder()
    builder.budget = ex_old_short.cost + 5 # Enough for short, not for long

    # ex_new_long is more recent, but doesn't fit. ex_old_short should not be chosen.
    added = crammer.cram(builder, [ex_new_long, ex_old_short])
    assert not added
    assert not builder.build()

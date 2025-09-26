from pathlib import Path
from llobot.chats.builders import ChatBuilder
from llobot.crammers.index.optional import OptionalIndexCrammer
from llobot.formats.indexes import IndexFormat
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex

class MockIndexFormat(IndexFormat):
    def render(self, knowledge: Knowledge) -> str:
        return "File index"

def test_cram_fits():
    """Tests that the index is added when it fits the budget."""
    crammer = OptionalIndexCrammer(index_format=MockIndexFormat())
    builder = ChatBuilder()
    builder.budget = 1000
    knowledge = Knowledge({Path("file.txt"): "content"})

    added = crammer.cram(builder, knowledge)
    assert added == knowledge.keys()
    assert "File index" in builder.build()

def test_cram_does_not_fit():
    """Tests that the index is not added when it exceeds the budget."""
    crammer = OptionalIndexCrammer(index_format=MockIndexFormat())
    builder = ChatBuilder()
    builder.budget = 10 # Too small
    knowledge = Knowledge({Path("file.txt"): "content"})

    added = crammer.cram(builder, knowledge)
    assert added == KnowledgeIndex()
    assert not builder.build()

def test_cram_empty_knowledge():
    """Tests that nothing is added for empty knowledge."""
    crammer = OptionalIndexCrammer()
    builder = ChatBuilder()
    builder.budget = 1000
    knowledge = Knowledge()

    added = crammer.cram(builder, knowledge)
    assert added == KnowledgeIndex()
    assert not builder.build()

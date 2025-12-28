from llobot.formats.knowledge import standard_knowledge_format
from llobot.formats.knowledge.bulk import BulkKnowledgeFormat

def test_standard_knowledge_format():
    assert isinstance(standard_knowledge_format(), BulkKnowledgeFormat)

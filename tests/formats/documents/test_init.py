from llobot.formats.documents import standard_document_format
from llobot.formats.documents.details import DetailsDocumentFormat

def test_standard_document_format():
    assert isinstance(standard_document_format(), DetailsDocumentFormat)

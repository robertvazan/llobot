from textwrap import dedent
from pathlib import Path
from llobot.formats.deltas.details import DetailsDocumentDeltaFormat
from llobot.knowledge.deltas.documents import DocumentDelta

def test_quad_backticks():
    formatter = DetailsDocumentDeltaFormat(quad_backticks=('markdown',))
    delta = DocumentDelta(Path('README.md'), '# Title\n\n```python\ncode\n```')
    result = formatter.render(delta)
    assert '````markdown' in result
    assert '````' in result.split('````markdown')[1]

from __future__ import annotations
from pathlib import PurePosixPath
from llobot.formats.documents.details import DetailsDocumentFormat
from llobot.formats.languages.extension import ExtensionLanguageMapping

def test_render_file_listing():
    fmt = DetailsDocumentFormat()
    rendered = fmt.render(PurePosixPath('file.py'), 'print("hello")')
    assert rendered == (
        '<details>\n'
        '<summary>File: ~/file.py</summary>\n\n'
        '```python\n'
        'print("hello")\n'
        '```\n\n'
        '</details>'
    )

def test_render_with_language_mapping():
    fmt = DetailsDocumentFormat(languages=ExtensionLanguageMapping({'.special': 'lang_special'}))
    rendered = fmt.render(PurePosixPath('test.special'), 'content')
    assert '```lang_special' in rendered

def test_render_markdown_quad_backticks():
    fmt = DetailsDocumentFormat()
    rendered = fmt.render(PurePosixPath('doc.md'), '```python\ncode\n```')
    assert '````markdown' in rendered
    assert '````\n\n</details>' in rendered

def test_render_quad_backticks_for_other_languages():
    fmt = DetailsDocumentFormat(quad_backticks=('python', 'markdown'))
    rendered = fmt.render(PurePosixPath('file.py'), '` `` ```')
    assert '````python' in rendered

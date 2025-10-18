from textwrap import dedent
from pathlib import Path
from llobot.formats.deltas.documents import standard_document_delta_format
from llobot.knowledge.deltas.documents import DocumentDelta
from llobot.knowledge.deltas.knowledge import KnowledgeDelta
from llobot.chats.message import ChatMessage
from llobot.chats.thread import ChatThread
from llobot.chats.intent import ChatIntent

def test_render_file():
    formatter = standard_document_delta_format()
    delta = DocumentDelta(Path('test.py'), 'def hello():\n    return "world"')
    result = formatter.render(delta)
    assert '<details>' in result
    assert '<summary>File: test.py</summary>' in result
    assert '```python' in result
    assert 'def hello():' in result
    assert '</details>' in result

def test_render_fresh():
    formatter = standard_document_delta_format()
    result = formatter.render_fresh(Path('test.py'), 'def hello():\n    return "world"')
    assert '<details>' in result
    assert '<summary>File: test.py</summary>' in result
    assert '```python' in result
    assert 'def hello():' in result
    assert '</details>' in result

def test_render_removal():
    formatter = standard_document_delta_format()
    delta = DocumentDelta(Path('test.py'), None, removed=True)
    result = formatter.render(delta)
    assert result == 'Removed: `test.py`'

def test_render_move():
    formatter = standard_document_delta_format()
    delta = DocumentDelta(Path('new.py'), None, moved_from=Path('old.py'))
    result = formatter.render(delta)
    assert result == 'Moved: `old.py` => `new.py`'

def test_find_file_listing():
    formatter = standard_document_delta_format()
    message = dedent("""
        Here is a file:

        <details>
        <summary>File: test.py</summary>

        ```python
        def hello():
            return "world"
        ```

        </details>

        And that's it.
        """).strip()
    matches = formatter.find(message)
    assert len(matches) == 1
    assert 'File: test.py' in matches[0]

def test_parse_file():
    formatter = standard_document_delta_format()
    formatted = dedent("""
        <details>
        <summary>File: test.py</summary>

        ```python
        def hello():
            return "world"
        ```

        </details>
        """).strip()
    delta = formatter.parse(formatted)
    assert delta is not None
    assert delta.path == Path('test.py')
    assert 'def hello():' in delta.content
    assert not delta.removed
    assert not delta.moved

def test_parse_removal():
    formatter = standard_document_delta_format()
    formatted = 'Removed: `test.py`'
    delta = formatter.parse(formatted)
    assert delta is not None
    assert delta.path == Path('test.py')
    assert delta.content is None
    assert delta.removed
    assert not delta.moved

def test_parse_move():
    formatter = standard_document_delta_format()
    formatted = 'Moved: `old/test.py` => `new/test.py`'
    delta = formatter.parse(formatted)
    assert delta is not None
    assert delta.path == Path('new/test.py')
    assert delta.moved_from == Path('old/test.py')
    assert delta.content is None
    assert not delta.removed

def test_parse_message():
    formatter = standard_document_delta_format()
    message = dedent("""
        Here are some changes:

        <details>
        <summary>File: new_file.py</summary>

        ```python
        print("hello")
        ```

        </details>

        Removed: `old_file.py`

        Moved: `src/old.py` => `src/new.py`
        """).strip()
    delta = formatter.parse_message(message)
    assert len(delta) == 3

def test_parse_chat():
    formatter = standard_document_delta_format()
    chat = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "Please make some changes."),
        ChatMessage(ChatIntent.RESPONSE, dedent("""
            Sure! Here's what I'll do:

            <details>
            <summary>File: example.py</summary>

            ```python
            def example():
                return True
            ```

            </details>

            Removed: `unused.py`
            """).strip())
    ])
    delta = formatter.parse_chat(chat)
    assert len(delta) == 2

def test_round_trip():
    """Test that rendering and then parsing returns equivalent delta."""
    formatter = standard_document_delta_format()
    original = DocumentDelta(Path('test.py'), 'def test():\n    pass')
    rendered = formatter.render(original)
    parsed = formatter.parse(rendered)
    assert parsed.path == original.path
    assert parsed.content.strip() == original.content.strip()
    assert parsed.removed == original.removed
    assert parsed.moved_from == original.moved_from

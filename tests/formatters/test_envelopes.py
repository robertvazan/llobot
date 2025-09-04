from textwrap import dedent
from pathlib import Path
from llobot.formatters.envelopes import details_envelopes, standard_envelopes
from llobot.knowledge.deltas import DocumentDelta, KnowledgeDelta
from llobot.chats.messages import ChatMessage
from llobot.chats.branches import ChatBranch
from llobot.chats.intents import ChatIntent
from llobot.knowledge.subsets import match_suffix

def test_format_file():
    formatter = standard_envelopes()
    delta = DocumentDelta(Path('test.py'), 'def hello():\n    return "world"')

    result = formatter.format(delta)

    assert '<details>' in result
    assert '<summary>File: test.py</summary>' in result
    assert '```python' in result
    assert 'def hello():' in result
    assert '</details>' in result

def test_format_diff():
    formatter = standard_envelopes()
    delta = DocumentDelta(Path('test.py'), '@@ -1,2 +1,3 @@\n def test():\n+    # comment\n     pass', diff=True)

    result = formatter.format(delta)

    assert '<details>' in result
    assert '<summary>Diff: test.py</summary>' in result
    assert '```diff' in result
    assert '@@' in result
    assert '</details>' in result

def test_format_removal():
    formatter = standard_envelopes()
    delta = DocumentDelta(Path('test.py'), None, removed=True)

    result = formatter.format(delta)

    assert result == 'Removed: `test.py`'

def test_format_move():
    formatter = standard_envelopes()
    delta = DocumentDelta(Path('new.py'), None, moved_from=Path('old.py'))

    result = formatter.format(delta)

    assert result == 'Moved: `old.py` => `new.py`'

def test_format_all():
    formatter = standard_envelopes()
    deltas = KnowledgeDelta([
        DocumentDelta(Path('file1.py'), 'content1'),
        DocumentDelta(Path('file2.py'), None, removed=True),
        DocumentDelta(Path('file3.py'), None, moved_from=Path('old3.py'))
    ])

    result = formatter.format_all(deltas)

    assert 'File: file1.py' in result
    assert 'Removed: `file2.py`' in result
    assert 'Moved: `old3.py` => `file3.py`' in result

def test_find_file_listing():
    formatter = standard_envelopes()
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

def test_find_removal():
    formatter = standard_envelopes()
    message = dedent("""
        Some text.

        Removed: `old_file.py`

        More text.
        """).strip()

    matches = formatter.find(message)

    assert len(matches) == 1
    assert matches[0] == 'Removed: `old_file.py`'

def test_find_move():
    formatter = standard_envelopes()
    message = dedent("""
        Some text.

        Moved: `old/path.py` => `new/path.py`

        More text.
        """).strip()

    matches = formatter.find(message)

    assert len(matches) == 1
    assert matches[0] == 'Moved: `old/path.py` => `new/path.py`'

def test_parse_file():
    formatter = standard_envelopes()
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
    assert not delta.diff
    assert not delta.removed
    assert not delta.moved

def test_parse_diff():
    formatter = standard_envelopes()
    formatted = dedent("""
        <details>
        <summary>Diff: test.py</summary>

        ```diff
        @@ -1,2 +1,3 @@
         def test():
        +    # comment
             pass
        ```

        </details>
        """).strip()

    delta = formatter.parse(formatted)

    assert delta is not None
    assert delta.path == Path('test.py')
    assert '@@' in delta.content
    assert delta.diff
    assert not delta.removed
    assert not delta.moved

def test_parse_removal():
    formatter = standard_envelopes()
    formatted = 'Removed: `test.py`'

    delta = formatter.parse(formatted)

    assert delta is not None
    assert delta.path == Path('test.py')
    assert delta.content is None
    assert delta.removed
    assert not delta.diff
    assert not delta.moved

def test_parse_move():
    formatter = standard_envelopes()
    formatted = 'Moved: `old/test.py` => `new/test.py`'

    delta = formatter.parse(formatted)

    assert delta is not None
    assert delta.path == Path('new/test.py')
    assert delta.moved_from == Path('old/test.py')
    assert delta.content is None
    assert not delta.removed
    assert not delta.diff

def test_parse_message():
    formatter = standard_envelopes()
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

    # Check file delta
    file_delta = next(d for d in delta if d.path == Path('new_file.py'))
    assert 'print("hello")' in file_delta.content

    # Check removal delta
    removed_delta = next(d for d in delta if d.removed)
    assert removed_delta.path == Path('old_file.py')

    # Check move delta
    moved_delta = next(d for d in delta if d.moved)
    assert moved_delta.path == Path('src/new.py')
    assert moved_delta.moved_from == Path('src/old.py')

def test_parse_chat():
    formatter = standard_envelopes()
    chat = ChatBranch([
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

    # Check file delta
    file_delta = next(d for d in delta if not d.removed)
    assert file_delta.path == Path('example.py')
    assert 'def example():' in file_delta.content

    # Check removal delta
    removed_delta = next(d for d in delta if d.removed)
    assert removed_delta.path == Path('unused.py')

def test_or_operator():
    formatter1 = details_envelopes()
    formatter2 = details_envelopes()

    combined = formatter1 | formatter2
    delta = DocumentDelta(Path('test.py'), 'content')

    result = combined.format(delta)
    assert result is not None

def test_and_operator():
    formatter = details_envelopes()
    filtered = formatter & match_suffix('.py')

    # Should format .py files
    py_delta = DocumentDelta(Path('test.py'), 'content')
    result = filtered.format(py_delta)
    assert result is not None

    # Should not format .txt files
    txt_delta = DocumentDelta(Path('test.txt'), 'content')
    result = filtered.format(txt_delta)
    assert result is None

def test_quad_backticks():
    formatter = details_envelopes(quad_backticks=('markdown',))
    delta = DocumentDelta(Path('README.md'), '# Title\n\n```python\ncode\n```')

    result = formatter.format(delta)

    # Should use 4 backticks for markdown content
    assert '````markdown' in result
    assert '````' in result.split('````markdown')[1]

def test_round_trip():
    """Test that formatting and then parsing returns equivalent delta."""
    formatter = standard_envelopes()
    original = DocumentDelta(Path('test.py'), 'def test():\n    pass')

    formatted = formatter.format(original)
    parsed = formatter.parse(formatted)

    assert parsed.path == original.path
    assert parsed.content.strip() == original.content.strip()
    assert parsed.diff == original.diff
    assert parsed.removed == original.removed
    assert parsed.moved_from == original.moved_from

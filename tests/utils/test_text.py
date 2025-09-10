import pytest
from llobot.utils.text import terminate_document, normalize_document, join_documents, concat_documents, dashed_name, markdown_code_block, markdown_code_details


def test_terminate_document():
    # Adds newline when missing
    assert terminate_document("hello") == "hello\n"

    # Doesn't add newline when already present
    assert terminate_document("hello\n") == "hello\n"

    # Handles empty string
    assert terminate_document("") == ""

    # Handles multiple newlines at end
    assert terminate_document("hello\n\n") == "hello\n\n"


def test_normalize_document():
    # Basic normalization
    assert normalize_document("hello\nworld") == "hello\nworld\n"

    # Removes trailing whitespace on lines
    assert normalize_document("hello   \nworld  ") == "hello\nworld\n"

    # Removes empty lines at beginning and end
    assert normalize_document("\n\nhello\nworld\n\n") == "hello\nworld\n"

    # Handles mixed whitespace
    assert normalize_document("  \nhello\n  \nworld\n  ") == "hello\n\nworld\n"

    # Handles empty string
    assert normalize_document("") == ""

    # Handles only whitespace
    assert normalize_document("   \n  \n  ") == ""

    # Preserves internal empty lines
    assert normalize_document("hello\n\nworld") == "hello\n\nworld\n"

    # Already normalized document
    assert normalize_document("hello\nworld\n") == "hello\nworld\n"

    # Single line
    assert normalize_document("hello") == "hello\n"


def test_join_documents():
    # Basic joining with separator, last part is not terminated
    assert join_documents("---\n", ["hello", "world"]) == "hello\n---\nworld"

    # Filters out empty and whitespace-only strings
    assert join_documents("---\n", ["hello", "", "world"]) == "hello\n---\nworld"
    assert join_documents("---\n", ["hello", "  ", "world"]) == "hello\n---\nworld"

    # Last part with newline is preserved
    assert join_documents("---\n", ["hello", "world\n"]) == "hello\n---\nworld\n"

    # Handles empty input
    assert join_documents("---\n", []) == ""
    assert join_documents("---\n", [""]) == ""

    # Single document is returned as-is
    assert join_documents("---\n", ["hello"]) == "hello"


def test_concat_documents():
    # Basic concatenation with double newline
    assert concat_documents("hello", "world") == "hello\n\nworld"

    # Filters out empty and whitespace-only strings
    assert concat_documents("hello", "", "world") == "hello\n\nworld"
    assert concat_documents("hello", "  ", "world") == "hello\n\nworld"

    # Whitespace is preserved
    assert concat_documents("  hello  ", "world") == "  hello  \n\nworld"

    # Documents other than the last one are newline-terminated unless they already are
    assert concat_documents("hello\n", "world\n") == "hello\n\nworld\n"

    # Handles empty input
    assert concat_documents() == ""

    # Single document
    assert concat_documents("hello") == "hello"


def test_dashed_name():
    # Basic conversion
    assert dashed_name("hello world") == "hello-world"

    # Preserves underscores
    assert dashed_name("hello_world") == "hello_world"

    # Handles various special characters
    assert dashed_name("hello@world!") == "hello-world"

    # Handles multiple consecutive non-alphanumeric characters
    assert dashed_name("hello!!!world") == "hello-world"

    # Handles leading and trailing special characters
    assert dashed_name("@hello_world@") == "hello_world"

    # Handles empty and special cases
    assert dashed_name("") == ""
    assert dashed_name("hello") == "hello"
    assert dashed_name("hello123world") == "hello123world"


def test_markdown_code_block():
    # Basic quoting
    assert markdown_code_block("python", "print('hello')") == "```python\nprint('hello')\n```"
    assert markdown_code_block("", "some code") == "```\nsome code\n```"

    # Document already has terminal newline
    assert markdown_code_block("python", "print('hello')\n") == "```python\nprint('hello')\n```"

    # Automatically adjusts backtick count when document contains backticks
    assert markdown_code_block("markdown", "Here is some `code`") == "```markdown\nHere is some `code`\n```"
    assert markdown_code_block("markdown", "```\ncode block\n```") == "````markdown\n```\ncode block\n```\n````"
    assert markdown_code_block("markdown", "````\ncode block\n````") == "`````markdown\n````\ncode block\n````\n`````"

    # Handles document starting with backticks
    assert markdown_code_block("markdown", "```python\ncode\n```") == "````markdown\n```python\ncode\n```\n````"

    # Handles empty document
    assert markdown_code_block("python", "") == "```python\n```"

    # Custom backtick count
    assert markdown_code_block("python", "print('hello')", backtick_count=4) == "````python\nprint('hello')\n````"


def test_markdown_code_details():
    # Basic details formatting
    expected = "<details>\n<summary>Test Summary</summary>\n\n```python\nprint('hello')\n```\n\n</details>"
    assert markdown_code_details("Test Summary", "python", "print('hello')") == expected

    # Complex summary with special characters
    expected = "<details>\n<summary>File: path/to/file.py (new)</summary>\n\n```python\nprint('hello')\n```\n\n</details>"
    assert markdown_code_details("File: path/to/file.py (new)", "python", "print('hello')") == expected

    # Custom backtick count is passed through to quote()
    expected = "<details>\n<summary>Test Summary</summary>\n\n````python\nprint('hello')\n````\n\n</details>"
    assert markdown_code_details("Test Summary", "python", "print('hello')", backtick_count=4) == expected

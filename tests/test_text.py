import pytest
from llobot.text import terminate, join, concat, dashed_name, quote


def test_terminate():
    # Adds newline when missing
    assert terminate("hello") == "hello\n"

    # Doesn't add newline when already present
    assert terminate("hello\n") == "hello\n"

    # Handles empty string
    assert terminate("") == ""

    # Handles multiple newlines at end
    assert terminate("hello\n\n") == "hello\n\n"


def test_join():
    # Basic joining with separator
    assert join("---\n", ["hello", "world"]) == "hello\n---\nworld\n"

    # Filters out empty and whitespace-only strings
    assert join("---\n", ["hello", "", "world"]) == "hello\n---\nworld\n"
    assert join("---\n", ["hello", "  ", "world"]) == "hello\n---\nworld\n"

    # Adds terminal newlines automatically
    assert join("---\n", ["hello\n", "world"]) == "hello\n---\nworld\n"

    # Handles empty input
    assert join("---\n", []) == ""
    assert join("---\n", [""]) == ""

    # Single document
    assert join("---\n", ["hello"]) == "hello\n"


def test_concat():
    # Basic concatenation (each document gets terminated, then joined with \n)
    assert concat("hello", "world") == "hello\n\nworld\n"

    # Filters out empty and whitespace-only strings
    assert concat("hello", "", "world") == "hello\n\nworld\n"

    # Adds terminal newlines automatically
    assert concat("hello\n", "world") == "hello\n\nworld\n"

    # Handles empty input
    assert concat() == ""

    # Single document
    assert concat("hello") == "hello\n"


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


def test_quote():
    # Basic quoting
    assert quote("python", "print('hello')") == "```python\nprint('hello')\n```"
    assert quote("", "some code") == "```\nsome code\n```"

    # Document already has terminal newline
    assert quote("python", "print('hello')\n") == "```python\nprint('hello')\n```"

    # Automatically adjusts backtick count when document contains backticks
    assert quote("markdown", "Here is some `code`") == "```markdown\nHere is some `code`\n```"
    assert quote("markdown", "```\ncode block\n```") == "````markdown\n```\ncode block\n```\n````"

    # Handles empty document
    assert quote("python", "") == "```python\n```"

    # Custom backtick count
    assert quote("python", "print('hello')", backtick_count=4) == "````python\nprint('hello')\n````"

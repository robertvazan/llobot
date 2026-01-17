from textwrap import dedent
from llobot.formats.prompts.grouped import GroupedPromptFormat

def test_grouped_prompt_format():
    fmt = GroupedPromptFormat()

    prompt = dedent("""\
        Preamble text.

        ## Section 1
        Content 1.

        ## Section 2
        Content 2.""")
    rendered = fmt.render(prompt)

    expected = dedent("""\
        Preamble text.

        <details>
        <summary>Section 1</summary>

        ## Section 1
        Content 1.

        </details>

        <details>
        <summary>Section 2</summary>

        ## Section 2
        Content 2.

        </details>""")

    assert rendered == expected

def test_grouped_prompt_format_no_sections():
    fmt = GroupedPromptFormat()
    prompt = "Just some text."
    rendered = fmt.render(prompt)
    assert rendered == "Just some text."

def test_grouped_prompt_format_only_sections():
    fmt = GroupedPromptFormat()
    prompt = dedent("""\
        ## Title
        Content""")
    rendered = fmt.render(prompt)
    expected = dedent("""\
        <details>
        <summary>Title</summary>

        ## Title
        Content

        </details>""")
    assert rendered == expected

def test_grouped_prompt_format_html_escaping():
    fmt = GroupedPromptFormat()
    prompt = dedent("""\
        ## Title <&>
        Content""")
    rendered = fmt.render(prompt)
    expected = dedent("""\
        <details>
        <summary>Title &lt;&amp;&gt;</summary>

        ## Title <&>
        Content

        </details>""")
    assert rendered == expected

def test_grouped_prompt_format_whitespace_preservation():
    fmt = GroupedPromptFormat()
    # Prompt starts with a newline and has indentation
    prompt = "\n" + dedent("""\
          Preamble with newline and indentation.

        ## Title
        Content with trailing spaces.
        """)
    rendered = fmt.render(prompt)

    # Expected:
    # - Leading newline and indentation preserved
    # - Trailing whitespace of preamble removed (by rstrip) and replaced by standard separator
    # - Section content trailing whitespace removed (by strip inside render loop)
    # - Final result rstripped (no trailing newlines)
    expected = "\n" + dedent("""\
          Preamble with newline and indentation.

        <details>
        <summary>Title</summary>

        ## Title
        Content with trailing spaces.

        </details>""")
    assert rendered == expected

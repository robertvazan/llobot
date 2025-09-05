from llobot.formats.mentions import parse_mentions
from llobot.chats.messages import ChatMessage
from llobot.chats.branches import ChatBranch
from llobot.chats.intents import ChatIntent

def test_parse_empty():
    assert parse_mentions('') == []

def test_parse_no_mentions():
    assert parse_mentions('this is a test') == []

def test_parse_bare():
    assert parse_mentions('this is @a-bare-mention.') == ['a-bare-mention']
    assert parse_mentions('@start of line') == ['start']
    assert parse_mentions('multiple @one and @two') == ['one', 'two']

def test_parse_bare_trailing_chars():
    assert parse_mentions('command is @cmd.') == ['cmd']
    assert parse_mentions('command is @cmd:') == ['cmd']
    assert parse_mentions('command is @cmd..:') == ['cmd']
    assert parse_mentions('command is @cmd.::') == ['cmd']
    assert parse_mentions('@cmd. in start') == ['cmd']

def test_parse_bare_allowed_chars():
    assert parse_mentions('@a-b/c*d?e:f=g.h') == ['a-b/c*d?e:f=g.h']

def test_parse_quoted_single_backtick():
    assert parse_mentions('this is @`a quoted mention`') == ['a quoted mention']
    assert parse_mentions('@` start of line ` ') == ['start of line']

def test_parse_quoted_double_backtick():
    assert parse_mentions('this is @``a "quoted" `mention` ``') == ['a "quoted" `mention`']
    assert parse_mentions('@`` start `of` line `` ') == ['start `of` line']

def test_parse_mixed_mentions():
    text = '@bare1 and @`quoted1` then @bare2 and @``quoted2``'
    expected = ['bare1', 'quoted1', 'bare2', 'quoted2']
    assert parse_mentions(text) == expected

def test_parse_no_mention_without_space():
    assert parse_mentions('thisis@notamention') == []
    assert parse_mentions('email@example.com') == []

def test_strip_code_blocks():
    text = """
    This is a test.
    ```python
    @ignored_in_block
    ```
    This is @a-mention outside.
    """
    assert parse_mentions(text) == ['a-mention']

def test_strip_inline_code_spans():
    assert parse_mentions('this is `@ignored`') == []
    assert parse_mentions('this is `@ignored` but @not-ignored') == ['not-ignored']
    assert parse_mentions('this is ``@ignored``') == []
    # A quoted mention is not an inline code span to be stripped.
    assert parse_mentions('this is a @`quoted mention`') == ['quoted mention']

def test_empty_commands():
    assert parse_mentions('@. @: @..::') == []
    assert parse_mentions('@` ` @`` `` @``') == []
    assert parse_mentions('@bare @ @`quoted`') == ['bare', 'quoted']
    assert parse_mentions('`@`') == [] # this is an inline code span

def test_chat_message_input():
    message = ChatMessage(ChatIntent.PROMPT, 'this is a test with @a-mention')
    assert parse_mentions(message) == ['a-mention']

def test_chat_branch_input():
    branch = ChatBranch([
        ChatMessage(ChatIntent.PROMPT, 'first message with @one'),
        ChatMessage(ChatIntent.RESPONSE, 'second message with @`two`'),
    ])
    assert parse_mentions(branch) == ['one', 'two']

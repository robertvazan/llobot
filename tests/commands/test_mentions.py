import llobot.commands.mentions
from llobot.chats.messages import ChatMessage
from llobot.chats.branches import ChatBranch
from llobot.chats.intents import ChatIntent

def test_parse_empty():
    assert llobot.commands.mentions.parse('') == []

def test_parse_no_mentions():
    assert llobot.commands.mentions.parse('this is a test') == []

def test_parse_bare():
    assert llobot.commands.mentions.parse('this is @a-bare-mention.') == ['a-bare-mention']
    assert llobot.commands.mentions.parse('@start of line') == ['start']
    assert llobot.commands.mentions.parse('multiple @one and @two') == ['one', 'two']

def test_parse_bare_trailing_chars():
    assert llobot.commands.mentions.parse('command is @cmd.') == ['cmd']
    assert llobot.commands.mentions.parse('command is @cmd:') == ['cmd']
    assert llobot.commands.mentions.parse('command is @cmd..:') == ['cmd']
    assert llobot.commands.mentions.parse('command is @cmd.::') == ['cmd']
    assert llobot.commands.mentions.parse('@cmd. in start') == ['cmd']

def test_parse_bare_allowed_chars():
    assert llobot.commands.mentions.parse('@a-b/c*d?e:f=g.h') == ['a-b/c*d?e:f=g.h']

def test_parse_quoted_single_backtick():
    assert llobot.commands.mentions.parse('this is @`a quoted mention`') == ['a quoted mention']
    assert llobot.commands.mentions.parse('@` start of line ` ') == ['start of line']

def test_parse_quoted_double_backtick():
    assert llobot.commands.mentions.parse('this is @``a "quoted" `mention` ``') == ['a "quoted" `mention`']
    assert llobot.commands.mentions.parse('@`` start `of` line `` ') == ['start `of` line']

def test_parse_mixed_mentions():
    text = '@bare1 and @`quoted1` then @bare2 and @``quoted2``'
    expected = ['bare1', 'quoted1', 'bare2', 'quoted2']
    assert llobot.commands.mentions.parse(text) == expected

def test_parse_no_mention_without_space():
    assert llobot.commands.mentions.parse('thisis@notamention') == []
    assert llobot.commands.mentions.parse('email@example.com') == []

def test_strip_code_blocks():
    text = """
    This is a test.
    ```python
    @ignored_in_block
    ```
    This is @a-mention outside.
    """
    assert llobot.commands.mentions.parse(text) == ['a-mention']

def test_strip_inline_code_spans():
    assert llobot.commands.mentions.parse('this is `@ignored`') == []
    assert llobot.commands.mentions.parse('this is `@ignored` but @not-ignored') == ['not-ignored']
    assert llobot.commands.mentions.parse('this is ``@ignored``') == []
    # A quoted mention is not an inline code span to be stripped.
    assert llobot.commands.mentions.parse('this is a @`quoted mention`') == ['quoted mention']

def test_empty_commands():
    assert llobot.commands.mentions.parse('@. @: @..::') == []
    assert llobot.commands.mentions.parse('@` ` @`` `` @``') == []
    assert llobot.commands.mentions.parse('@bare @ @`quoted`') == ['bare', 'quoted']
    assert llobot.commands.mentions.parse('`@`') == [] # this is an inline code span

def test_chat_message_input():
    message = ChatMessage(ChatIntent.PROMPT, 'this is a test with @a-mention')
    assert llobot.commands.mentions.parse(message) == ['a-mention']

def test_chat_branch_input():
    branch = ChatBranch([
        ChatMessage(ChatIntent.PROMPT, 'first message with @one'),
        ChatMessage(ChatIntent.RESPONSE, 'second message with @`two`'),
    ])
    assert llobot.commands.mentions.parse(branch) == ['one', 'two']

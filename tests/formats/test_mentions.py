from llobot.formats.mentions import parse_mentions, strip_mentions
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

def test_parse_preceded_by_symbols():
    assert parse_mentions('(@mention)') == ['mention']
    assert parse_mentions('(@mention1, @mention2)') == ['mention1', 'mention2']
    assert parse_mentions('{@mention1,@mention2}') == ['mention1', 'mention2']
    assert parse_mentions('[@mention1/@mention2]') == ['mention1', 'mention2']
    assert parse_mentions(')@mention') == ['mention']
    assert parse_mentions(']@mention') == ['mention']
    assert parse_mentions('}@mention') == ['mention']
    assert parse_mentions(',@mention') == ['mention']
    assert parse_mentions('-@mention') == ['mention']
    # Bare mentions can contain dots, so we need to test this case carefully.
    assert parse_mentions('word.@mention') == ['mention']

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

def test_strip_empty():
    assert strip_mentions('') == ''

def test_strip_no_mentions():
    assert strip_mentions('this is a test') == 'this is a test'
    assert strip_mentions('  padded with spaces  ') == 'padded with spaces'

def test_strip_leading():
    assert strip_mentions('@m1 message') == 'message'
    assert strip_mentions('  @m1  @`m2` message  ') == 'message'
    assert strip_mentions('@m1') == ''
    assert strip_mentions('  @m1 @m2  ') == ''

def test_strip_trailing():
    assert strip_mentions('message @m1') == 'message'
    assert strip_mentions('  message @m1 @`m2`  ') == 'message'
    assert strip_mentions('message@m1') == 'message@m1'

def test_strip_both():
    assert strip_mentions('@m1 message @m2') == 'message'
    assert strip_mentions(' @m1 @`m2` message @m3 @``m4`` ') == 'message'

def test_strip_middle_untouched():
    assert strip_mentions('message1 @m1 message2') == 'message1 @m1 message2'
    assert strip_mentions('  message1 @m1 message2  ') == 'message1 @m1 message2'

def test_strip_real_world_cases():
    assert strip_mentions('@project command') == 'command'
    assert strip_mentions('do something @project') == 'do something'
    assert strip_mentions('@project do something @llobot') == 'do something'
    assert strip_mentions('  @project @llobot do something  ') == 'do something'

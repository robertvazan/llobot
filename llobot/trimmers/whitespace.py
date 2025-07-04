from functools import cache
import re
from llobot.trimmers import Trimmer
import llobot.trimmers

@cache
def tabs() -> Trimmer:
    # Whitelist of file types where it is okay to replace tabs with 4 spaces.
    # Known exceptions: Makefile.
    from llobot.knowledge.subsets import cpp, java, python, rust, shell, toml, xml
    whitelist = (cpp.suffix()
        | java.suffix()
        | python.suffix()
        | rust.suffix()
        | shell.suffix()
        | toml.suffix()
        | xml.suffix())
    return llobot.trimmers.create(lambda path, content: content.replace('\t', '    ')) & whitelist

@cache
def trailing() -> Trimmer:
    # Whitelist of file types where trailing whitespace is not significant.
    # Known exceptions: *.md.
    from llobot.knowledge.subsets import cpp, java, python, rust, shell, toml, xml
    whitelist = (cpp.suffix()
        | java.suffix()
        | python.suffix()
        | rust.suffix()
        | shell.suffix()
        | toml.suffix()
        | xml.suffix())
    return llobot.trimmers.re(r'[ \t]+$', re.MULTILINE)

# Minimal trimmer that just normalizes whitespace (tabs and trailing whitespace).
@cache
def normalize() -> Trimmer:
    return tabs() + trailing()

__all__ = [
    'tabs',
    'trailing',
    'normalize',
]


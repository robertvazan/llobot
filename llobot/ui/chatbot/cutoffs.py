from __future__ import annotations
from datetime import datetime
import re
import llobot.time

CUTOFF_RE = re.compile(r'`:([0-9-]+)`')

def parse(message: str) -> datetime | None:
    lines = message.strip().splitlines()
    if not lines:
        return None
    m = CUTOFF_RE.fullmatch(lines[-1])
    return llobot.time.parse(m[1]) if m else None

def strip(message: str) -> str:
    lines = message.strip().splitlines()
    if not lines:
        return message
    m = CUTOFF_RE.fullmatch(lines[-1])
    if not m:
        return message
    # The rstrip() call here will modify the response if it contains extraneous newlines.
    # We don't care, because cache invalidation at the end of the current chat wouldn't do perceptible harm.
    return '\n'.join(lines[:-1]).rstrip()

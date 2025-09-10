from datetime import datetime, UTC
from llobot.utils.time import current_time, format_time, parse_time, try_parse_time
import time

def test_current_time():
    t1 = current_time()
    time.sleep(0.01)
    t2 = datetime.now(UTC).replace(microsecond=0)
    assert t1.tzinfo == UTC
    assert t1.microsecond == 0
    assert t2 >= t1

def test_format_parse_time():
    now = current_time()
    formatted = format_time(now)
    parsed = parse_time(formatted)
    assert parsed == now

def test_try_parse_time():
    now = current_time()
    formatted = format_time(now)
    assert try_parse_time(formatted) == now
    assert try_parse_time("invalid-time") is None

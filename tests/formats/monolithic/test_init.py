from llobot.formats.monolithic import standard_monolithic_format
from llobot.formats.monolithic.separator import SeparatorMonolithicFormat

def test_standard_monolithic_format():
    """Tests that the standard format is the separator-based one."""
    formatter = standard_monolithic_format()
    assert isinstance(formatter, SeparatorMonolithicFormat)

from __future__ import annotations
from llobot.utils.values import ValueTypeMixin

def test_value_type_mixin():
    class MyValue(ValueTypeMixin):
        def __init__(self, a, b, c=None):
            self.a = a
            self.b = b
            self.c = c
            self._cache = None # ephemeral

        def _ephemeral_fields(self) -> list[str]:
            return ['_cache']

    v1 = MyValue(1, 'foo')
    v2 = MyValue(1, 'foo')
    v3 = MyValue(2, 'foo')
    v4 = MyValue(1, 'bar')
    v5 = MyValue(1, 'foo', c=3)

    # Test __eq__
    assert v1 == v2
    assert v1 != v3
    assert v1 != v4
    assert v1 != v5
    assert v1 != "not a MyValue"

    # Test __hash__
    assert hash(v1) == hash(v2)
    assert hash(v1) != hash(v3)
    assert hash(v1) != hash(v4)
    assert hash(v1) != hash(v5)
    s = {v1, v2, v3, v4, v5}
    assert len(s) == 4

    # Test __repr__
    assert repr(v1) == "MyValue(a=1, b='foo', c=None)"
    assert repr(v3) == "MyValue(a=2, b='foo', c=None)"
    assert repr(v5) == "MyValue(a=1, b='foo', c=3)"
    
    # Test ephemeral field
    v1._cache = "some data"
    assert v1 == v2
    assert hash(v1) == hash(v2)
    assert repr(v1) == "MyValue(a=1, b='foo', c=None)"

    # Test another class
    class AnotherValue(ValueTypeMixin):
         def __init__(self, a, b, c=None):
            self.a = a
            self.b = b
            self.c = c

    v_other = AnotherValue(1, 'foo')
    assert v1 != v_other

    # Test no ephemeral fields
    class SimpleValue(ValueTypeMixin):
        def __init__(self, x):
            self.x = x
    
    s1 = SimpleValue(10)
    s2 = SimpleValue(10)
    s3 = SimpleValue(20)

    assert s1 == s2
    assert s1 != s3
    assert hash(s1) == hash(s2)
    assert repr(s1) == "SimpleValue(x=10)"

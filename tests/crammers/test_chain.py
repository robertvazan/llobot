from unittest.mock import Mock, call
from llobot.crammers import Crammer
from llobot.crammers.chain import CrammerChain
from llobot.environments import Environment
import pytest

def test_init_flattens_chains():
    c1 = Mock(spec=Crammer)
    c2 = Mock(spec=Crammer)
    c3 = Mock(spec=Crammer)

    chain1 = CrammerChain(c1, c2)
    chain2 = CrammerChain(chain1, c3)

    assert chain2.crammers == (c1, c2, c3)

def test_add_operator():
    class TrivialCrammer(Crammer):
        def cram(self, env: Environment) -> None:
            pass

    t1 = TrivialCrammer()
    t2 = TrivialCrammer()

    chain = t1 + t2
    assert isinstance(chain, CrammerChain)
    assert chain.crammers == (t1, t2)

    t3 = TrivialCrammer()
    chain2 = chain + t3
    assert isinstance(chain2, CrammerChain)
    assert chain2.crammers == (t1, t2, t3)

def test_add_operator_not_implemented():
    class TrivialCrammer(Crammer):
        def cram(self, env: Environment) -> None:
            pass
    t1 = TrivialCrammer()
    assert t1.__add__(1) is NotImplemented
    with pytest.raises(TypeError):
        t1 + 1

def test_cram_executes_in_order():
    c1 = Mock(spec=Crammer)
    c2 = Mock(spec=Crammer)
    env = Mock(spec=Environment)

    chain = CrammerChain(c1, c2)

    # Check order
    manager = Mock()
    manager.attach_mock(c1.cram, 'c1_cram')
    manager.attach_mock(c2.cram, 'c2_cram')

    chain.cram(env)
    assert manager.mock_calls == [call.c1_cram(env), call.c2_cram(env)]

def test_value_equality():
    class TrivialCrammer(Crammer):
        def __init__(self, name):
            self.name = name
        def cram(self, env): pass

    t1 = TrivialCrammer("a")
    t2 = TrivialCrammer("b")

    c1 = CrammerChain(t1, t2)
    c2 = CrammerChain(t1, t2)
    c3 = CrammerChain(t2, t1)

    assert c1 == c2
    assert c1 != c3
    assert hash(c1) == hash(c2)

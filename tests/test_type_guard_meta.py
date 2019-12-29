import pytest

from homebot.validator import TypeGuardMeta


def test_type_guard_metaclass():
    class Magic(metaclass=TypeGuardMeta):
        def __init__(self, a: int):
            self.a = a

        def __call__(self, b: float):
            return self. a + int(b)

    dut = Magic(10)  # Is an int. Should work
    assert dut.a == 10

    err_msg = "type of argument \"a\" must be int; got str instead"
    with pytest.raises(TypeError, match=err_msg):
        Magic("str")

    assert dut(10.0) == 20  # 10 + 10 = 2

    err_msg = 'type of argument "b" must be either float or int; got str instead'
    with pytest.raises(TypeError, match=err_msg):
        dut("str")


def test_type_guard_metaclass_no_annotations():
    class Magic(metaclass=TypeGuardMeta):
        def __init__(self):
            pass

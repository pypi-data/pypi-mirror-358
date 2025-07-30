from pylogical.attributes import *

def test_logical_attributes():
    assert Inverted(True).result() is False
    assert IsTruthy(1).result() is True
    assert IsFalsy(0).result() is True
    assert IsNone(None).result() is True
    assert IsNotNone("text").result() is True
    assert IsEven(4).result() is True
    assert IsOdd(3).result() is True
    assert IsPositive(5).result() is True
    assert IsNegative(-1).result() is True
    assert IsZero(0).result() is True
    assert IsEmpty([]).result() is True
    assert IsNotEmpty([1]).result() is True
    assert IsType("hello", str).result() is True
    assert Equals(5, 5).result() is True
    assert NotEquals(5, 6).result() is True
    assert IsSubset([1], [1,2,3]).result() is True
    assert IsSuperset([1,2,3], [1]).result() is True

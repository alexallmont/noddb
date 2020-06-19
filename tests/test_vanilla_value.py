import pytest
from noddb.value import InputValue, OutputValue, ValueException
from noddb.node import Node


def test_input_value():
    n = Node('n')
    n_in = InputValue('in', n, 11)
    assert n_in.name == 'in'
    assert n_in.path() == 'n.in'
    assert n_in.is_input() is True
    assert n_in.is_output() is False
    assert n_in.parent == n
    assert n_in.value() == 11
    assert n_in.is_sourced() is False
    assert n_in.source() is None


def test_output_value():
    n = Node('n')
    n_out = OutputValue('out', n, 13)
    assert n_out.name == 'out'
    assert n_out.path() == 'n.out'
    assert n_out.is_input() is False
    assert n_out.is_output() is True
    assert n_out.parent == n
    assert n_out.value() == 13
    assert n_out.is_sourced() is False
    assert n_out.source() is None


def test_deep_path():
    foo = Node('foo')
    bar = Node('bar', foo)
    etc = Node('etc', bar)
    tez = InputValue('tez', etc, 17)
    assert tez.path() == 'foo.bar.etc.tez'


def test_sourced():
    foo = Node('foo')
    foo_out = OutputValue('out', foo, 7)
    bar = Node('bar')
    bar_in = InputValue('out', bar, 5)

    bar_in.set_source(foo_out)
    assert bar_in.is_sourced() is True
    assert bar_in.source() == foo_out
    assert bar_in.value() == 7

    with pytest.raises(ValueException) as excinfo:
        bar_in.set_value(9)
    assert str(excinfo.value) == 'Cannot set "bar.out" whilst sourced from "foo.out"'

    bar_in.clear_source()
    assert bar_in.is_sourced() is False
    assert bar_in.source() is None
    bar_in.set_value(3)
    assert bar_in.value() == 3


def test_mismatch_set_value():
    n = Node('n')
    n_in = InputValue('in', n, 17)
    with pytest.raises(ValueException) as excinfo:
        n_in.set_value("fish")
    assert str(excinfo.value) == 'Cannot set "n.in" (int) to mismatched value fish (str)'


def test_source_from_non_output():
    a = InputValue('a', None, 'this')
    b = InputValue('b', None, 'that')
    with pytest.raises(ValueException) as excinfo:
        b.set_source(a)
    assert str(excinfo.value) == 'Cannot source from non-output "a"'


def test_double_source_input():
    a = OutputValue('a', None, 'this')
    b = OutputValue('b', None, 'that')
    c = InputValue('c', None, 'tother')
    c.set_source(a)
    with pytest.raises(ValueException) as excinfo:
        c.set_source(b)
    assert str(excinfo.value) == 'Cannot source "c" from "b" as already connected to "a"'


def test_source_to_non_input():
    a = OutputValue('a', None, 'this')
    b = OutputValue('b', None, 'that')
    with pytest.raises(ValueException) as excinfo:
        b.set_source(a)
    assert str(excinfo.value) == 'Cannot source to non-input "b"'


def test_source_mismatched_type():
    a = OutputValue('a', None, 23)
    b = InputValue('b', None, 'that')
    with pytest.raises(ValueException) as excinfo:
        b.set_source(a)
    assert str(excinfo.value) == 'Cannot source "b" (str) to mismatched output "a" (int)'


def test_invalid_clear():
    foo = InputValue('foo', None, 27)
    with pytest.raises(ValueException) as excinfo:
        foo.clear_source()
    assert str(excinfo.value) == 'Cannot clear source on non-connected input "foo"'

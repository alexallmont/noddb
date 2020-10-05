import pytest
from noddb.value import InputValue, OutputValue, ValueException
from noddb.node import Node


def test_input_value():
    n = Node(None, 'n')
    n_in = InputValue(n, 'in', 11)
    assert n_in.name == 'in'
    assert n_in.path() == 'n.in'
    assert n_in.is_input() is True
    assert n_in.is_output() is False
    assert n_in.parent == n
    assert n_in.value() == 11
    assert n_in.is_sourced() is False
    assert n_in.source() is None


def test_output_value():
    n = Node(None, 'n')
    n_out = OutputValue(n, 'out', 13)
    assert n_out.name == 'out'
    assert n_out.path() == 'n.out'
    assert n_out.is_input() is False
    assert n_out.is_output() is True
    assert n_out.parent == n
    assert n_out.value() == 13


def test_deep_path():
    foo = Node(None, 'foo')
    bar = Node(foo, 'bar')
    etc = Node(bar, 'etc')
    tez = InputValue(etc, 'tez', 17)
    assert tez.path() == 'foo.bar.etc.tez'


def test_sourced():
    foo = Node(None, 'foo')
    foo_out = OutputValue(foo, 'out', 7)
    bar = Node(None, 'bar')
    bar_in = InputValue(bar, 'out', 5)

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
    n = Node(None, 'n')
    n_in = InputValue(n, 'in', 17)
    with pytest.raises(ValueException) as excinfo:
        n_in.set_value("fish")
    assert str(excinfo.value) == 'Cannot set "n.in" (int) to mismatched value fish (str)'


def test_source_from_non_output():
    a = InputValue(None, 'a', 'this')
    b = InputValue(None, 'b', 'that')
    with pytest.raises(ValueException) as excinfo:
        b.set_source(a)
    assert str(excinfo.value) == 'Cannot source from non-output "a"'


def test_double_source_input():
    a = OutputValue(None, 'a', 'this')
    b = OutputValue(None, 'b', 'that')
    c = InputValue(None, 'c', 'tother')
    c.set_source(a)
    with pytest.raises(ValueException) as excinfo:
        c.set_source(b)
    assert str(excinfo.value) == 'Cannot source "c" from "b" as already connected to "a"'


def test_source_mismatched_type():
    a = OutputValue(None, 'a', 23)
    b = InputValue(None, 'b', 'that')
    with pytest.raises(ValueException) as excinfo:
        b.set_source(a)
    assert str(excinfo.value) == 'Cannot source "b" (str) to mismatched output "a" (int)'


def test_invalid_clear():
    foo = InputValue(None, 'foo', 27)
    with pytest.raises(ValueException) as excinfo:
        foo.clear_source()
    assert str(excinfo.value) == 'Cannot clear source on non-connected input "foo"'


def test_connect():
    n = Node(None, 'n')
    a = OutputValue(n, 'a', 'stuff')
    b = InputValue(n, 'b', 'oink')
    a >> b
    assert b.source() == a
    assert b.value() == 'stuff'

    b.clear_source()
    assert b.value() == 'stuff'
    b.set_value('etc')
    assert b.is_sourced() is False
    assert b.value() == 'etc'
    b << a
    assert b.source() == a
    assert b.value() == 'stuff'

    n['b'].clear_source()
    n['b'].set_value('oof')
    assert b.value() == 'oof'
    assert b.is_sourced() is False
    n['a'] >> n['b']
    assert b.source() == a
    assert b.value() == 'stuff'

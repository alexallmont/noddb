import pytest

from noddb.node import Node, NodeException


def test_root_node():
    foo = Node('foo')
    assert foo.name == 'foo'
    assert foo.parent is None
    assert foo.children == {}


def test_sub_node():
    foo = Node('foo')
    bar = Node('bar', foo)
    assert bar.name == 'bar'
    assert bar.parent == foo
    assert bar.children == {}
    assert foo.children == {'bar': bar}


def test_dup_sub_node():
    foo = Node('foo')
    _ = Node('bar', foo)
    with pytest.raises(NodeException) as excinfo:
        _ = Node('bar', foo)
    assert str(excinfo.value) == 'parent "foo" already has child "bar"'


def test_sub_path():
    foo = Node('foo')
    bar = Node('bar', foo)
    etc = Node('etc', bar)
    assert etc.path() == 'foo.bar.etc'


def test_input_output():
    foo = Node('foo')
    assert foo.is_input() is False
    assert foo.is_output() is False

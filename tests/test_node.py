import pytest

from noddb.node import Node, NodeArray, NodeException

# Note NodeBase is not generally imported. Used here for testing core regressions
from noddb.node import NodeBase


def test_root_node():
    foo = Node(None, 'foo')
    assert foo.name == 'foo'
    assert foo.parent is None
    assert foo.typename is 'Node'
    assert foo.path() is 'foo'
    assert foo.children == []

    with pytest.raises(NodeException) as excinfo:
        _ = Node(None, None)
    assert str(excinfo.value) == 'Unparented leaf nodes must be named'

def test_node_base_misuse():
    root = NodeBase(None, 'root')
    with pytest.raises(NodeException) as excinfo:
        _ = Node(root, 'etc')
    assert str(excinfo.value) == 'Nodes must parent to container types; detected add to NodeBase'

def test_sub_node():
    foo = Node(None, 'foo')
    bar = Node(foo, 'bar')
    assert foo.parent == None
    assert foo.children == [bar]
    assert bar.parent == foo
    assert bar.name == 'bar'
    assert bar.path() == 'foo.bar'

    with pytest.raises(NodeException) as excinfo:
        _ = Node(foo, None)
    assert str(excinfo.value) == 'Node children must be named; unnamed Node in foo'


def test_dup_sub_node():
    foo = Node(None, 'foo')
    _ = Node(foo, 'bar')

    with pytest.raises(NodeException) as excinfo:
        _ = Node(foo, 'bar')
    assert str(excinfo.value) == "Node child names must be unique; 'bar' already in foo"


def test_node_array():
    root = NodeArray(None, 'rootlist')
    assert root.name == 'rootlist'
    a = Node(root)
    b = Node(root)
    assert len(root.children) == 2
    assert a.path() == 'rootlist[0]'
    assert b.path() == 'rootlist[1]'

    c = Node(b, 'foo')
    assert c.path() == 'rootlist[1].foo'

    d = NodeArray(root)
    e = Node(d)
    assert len(root.children) == 3
    assert d.path() == 'rootlist[2]'
    assert e.path() == 'rootlist[2][0]'

    with pytest.raises(NodeException) as excinfo:
        _ = Node(root, 'bar')
    assert str(excinfo.value) == "NodeArray children must not be named; found 'name' in rootlist"


def test_get_item():
    root = Node(None, 'megacorp')
    bob = Node(root, 'bob')
    alice = Node(root, 'alice')
    frank = Node(alice, 'frank')

    assert root['bob'] == bob
    assert root['alice'] == alice
    assert root['alice']['frank'] == frank

    with pytest.raises(NodeException) as excinfo:
        root['alice']['jimbob']
    assert str(excinfo.value) == "Node megacorp.alice does not have child 'jimbob'"

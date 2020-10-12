import pytest
from noddb.node import Node, NodeArray
from noddb.path import split_path, path_to_node
from noddb.std_value import InputInt


def test_split_path():
    split = split_path('this.th_at[0][1].et0c')
    assert len(split) == 5
    assert split[0] == 'this'
    assert split[1] == 'th_at'
    assert split[2] == 0
    assert split[3] == 1
    assert split[4] == 'et0c'

    first_is_int = split_path('[1]')
    assert first_is_int == [1]

    first_two_are_ints = split_path('[2][3]')
    assert first_two_are_ints == [2, 3]

    with pytest.raises(ValueError) as excinfo:
        _ = split_path('good.0bad')
    assert str(excinfo.value) == "invalid literal for int() with base 10: '0bad'"


def test_path_to_node():
    class CustomNode(Node):
        def init_custom(self):
            InputInt(self, 'a')
            NodeArray(self, 'b')

    root = Node(None, 'root')
    foo = Node(root, 'foo')
    bar = NodeArray(foo, 'bar')
    custom = CustomNode(bar)

    assert path_to_node(root, 'foo') == foo
    assert path_to_node(root, 'foo.bar') == bar
    assert path_to_node(root, 'foo.bar[0]') == custom
    assert path_to_node(root, 'foo.bar[0].a') == custom['a']
    assert path_to_node(root, 'foo.bar[0].b') == custom['b']

    assert path_to_node(foo, 'bar') == bar
    assert path_to_node(bar, '[0]') == custom

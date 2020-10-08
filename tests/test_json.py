import pytest
from pytest import approx

from noddb.node import Node, NodeArray
from noddb.json import JsonRegistry, ExportException
from noddb.std_value import InputBool, InputInt, InputString, OutputBool, OutputInt, OutputFloat
from noddb.value import InputValue, OutputValue


def test_export_minimal():
    registry = JsonRegistry()

    assert registry.export_json(Node(None, 'a')) == {
        'nodes': {'a': {}},
        'sources': {},
        'values': {}
    }

    assert registry.export_json(NodeArray(None, 'b')) == {
        'nodes': {'b': []},
        'sources': {},
        'values': {}
    }

    assert registry.export_json(InputString(None, 'c')) == {
        'nodes': {'c': 'InputString'},
        'sources': {},
        'values': {'c': ''}
    }

    assert registry.export_json(OutputFloat(None, 'd', 6.3)) == {
        'nodes': {'d': 'OutputFloat'},
        'sources': {},
        'values': approx({'d': 6.3})
    }


def test_export_bad_types():
    class UnregisteredNode(Node):
        pass

    with pytest.raises(ExportException) as excinfo:
        _ = JsonRegistry().export_json(UnregisteredNode(None, 'whowhatnow'))
    assert str(excinfo.value) == "Unexpected node type 'UnregisteredNode' during export"

    with pytest.raises(ExportException) as excinfo:
        _ = JsonRegistry().export_json(InputValue(None, 'notype', 1))
    assert str(excinfo.value) == "Unexpected input value type 'InputValue' during export"

    with pytest.raises(ExportException) as excinfo:
        _ = JsonRegistry().export_json(OutputValue(None, 'notype', 1))
    assert str(excinfo.value) == "Unexpected output value type 'OutputValue' during export"


def test_export_interconnected():
    # Test storing a custom user-defined node
    class CustomNode(Node):
        def __init__(self, parent=None, name=None):
            super().__init__(parent, name)
            InputBool(self, 'inny', False)
            OutputInt(self, 'outy', 2)

    # Add a hierarchy under root 'foo'
    foo = Node(None, 'foo')
    x = OutputBool(foo, 'x', True)
    bar = NodeArray(foo, 'bar')
    y = OutputInt(bar, None, 3)
    etc = Node(bar)
    fzz = CustomNode(bar)
    z = InputInt(etc, 'z', 5)
    last_arr = NodeArray(bar)
    InputBool(last_arr, None, False)
    last_bool = InputBool(last_arr, None, True)

    # Test connecting inputs to outputs
    y >> z
    x >> fzz['inny']

    # Add an extra root and interconnect to deepest input in 'foo'
    extra_root = CustomNode(None, 'extra_root')
    extra_root['outy'] >> last_bool

    registry = JsonRegistry([CustomNode])
    assert registry.export_json([foo, extra_root]) == {
        'nodes': {
            'foo': {
                'bar': [
                    'OutputInt',
                    {
                        'z': 'InputInt'
                    },
                    'CustomNode',
                    [
                        'InputBool',
                        'InputBool'
                    ]
                ],
                'x': 'OutputBool'
            },
            'extra_root': 'CustomNode'
        },
        'sources': {
            'foo.bar[1].z': 'foo.bar[0]',
            'foo.bar[2].inny': 'foo.x',
            'foo.bar[3][1]': 'extra_root.outy'
        },
        'values': {
            'foo.bar[0]': 3,
            'foo.bar[2].outy': 2,
            'foo.bar[3][0]': False,
            'foo.x': True,
            'extra_root.inny': False,
            'extra_root.outy': 2
        }
    }

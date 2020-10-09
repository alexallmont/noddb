import pytest
from pytest import approx

from noddb.node import Node, NodeArray
from noddb.json import JsonRegistry, ExportException, ImportException
from noddb.std_value import InputBool, InputInt, InputFloat, InputString
from noddb.std_value import OutputBool, OutputInt, OutputFloat, OutputString
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


def test_bad_import():
    registry = JsonRegistry()

    with pytest.raises(ImportException) as excinfo:
        registry.import_json({
            'nodes': {},
            'values': {},
            'tastysnacks': {}
        })
    assert str(excinfo.value) == 'Expecting nodes, values and sources entries at root'

    with pytest.raises(ImportException) as excinfo:
        registry.import_json({
            'nodes': {},
            'values': [],
            'sources': {}
        })
    assert str(excinfo.value) == 'Expecting dict type for nodes, values and sources'

    with pytest.raises(ImportException) as excinfo:
        registry.import_json({
            'nodes': {
                'badtype': True
            },
            'values': {},
            'sources': {}
        })
    assert str(excinfo.value) == "Expecting dict, list or string values for nodes, found <class 'bool'>"


def test_node_import():
    class FooNode(Node):
        pass

    registry = JsonRegistry([FooNode])
    a_nodes = registry.import_json({
        'nodes': {
            'root': 'InputInt'
        },
        'values': {},
        'sources': {}
    })
    assert len(a_nodes) == 1
    assert type(a_nodes[0]) == InputInt
    assert a_nodes[0].name == 'root'
    assert a_nodes[0].value() == 0

    b_nodes = registry.import_json({
        'nodes': {
            'root1': ['InputInt'],
            'root2': 'FooNode'
        },
        'values': {},
        'sources': {}
    })
    assert len(b_nodes) == 2
    assert type(b_nodes[0]) == NodeArray
    assert len(b_nodes[0].children) == 1
    assert type(b_nodes[0][0]) == InputInt
    assert type(b_nodes[1]) == FooNode

    c_nodes = registry.import_json({
        'nodes': {
            'foo': {
                'bar': {
                    'a': 'FooNode',
                    'b': 'InputBool',
                    'c': 'OutputFloat'
                }
            },
        },
        'values': {},
        'sources': {}
    })
    assert type(c_nodes[0]) == Node
    assert c_nodes[0].name == 'foo'
    assert type(c_nodes[0]['bar']) == Node
    assert type(c_nodes[0]['bar']['a']) == FooNode
    assert type(c_nodes[0]['bar']['b']) == InputBool
    assert type(c_nodes[0]['bar']['c']) == OutputFloat


def test_value_import_set():
    registry = JsonRegistry()
    nodes = registry.import_json({
        'nodes': {
            'a': 'OutputString'
        },
        'values': {
            'a': 'stuff',
        },
        'sources': {}
    })
    assert type(nodes[0]) == OutputString
    assert nodes[0].value() == 'stuff'

    nodes = registry.import_json({
        'nodes': {
            'foo': {
                'bar': [
                    [
                        [
                            'OutputFloat',
                            'InputFloat'
                        ]
                    ]
                ]
            }
        },
        'values': {
            'foo.bar[0][0][0]': 3.0,
            'foo.bar[0][0][1]': 7.0,
        },
        'sources': {}
    })
    assert type(nodes[0]['bar'][0][0][0]) == OutputFloat
    assert type(nodes[0]['bar'][0][0][1]) == InputFloat
    assert nodes[0]['bar'][0][0][0].value() == approx(3)
    assert nodes[0]['bar'][0][0][1].value() == approx(7)


def test_source_import_set():
    registry = JsonRegistry()
    nodes = registry.import_json({
        'nodes': {
            'foo': {
                'a': 'OutputFloat'
            },
            'bar': {
                'b': 'InputFloat'
            }
        },
        'values': {
            'foo.a': 6.0,
        },
        'sources': {
            'bar.b': 'foo.a'
        }
    })
    assert nodes[0]['a'].value() == approx(6)
    assert nodes[1]['b'].is_sourced() is True
    assert nodes[1]['b'].value() == approx(6)
